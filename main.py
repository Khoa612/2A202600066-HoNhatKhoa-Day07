"""
main.py — VinPolicys RAG Pipeline with embedding cache + real LLM.

Usage:
    python main.py                      # Run all 5 benchmark queries
    python main.py "Your question"      # Run a single custom query
    python main.py --rebuild            # Force re-chunk & re-embed (clears cache)

Embedding cache:
    Chunks + embeddings are saved to data/chunk_cache.json after the first run.
    Subsequent runs load from cache — zero API calls for embedding.
    Cache is invalidated when you pass --rebuild or delete the cache file manually.
"""

from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv

from src.agent import KnowledgeBaseAgent
from src.chunking import SemanticChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.models import Document
from src.store import EmbeddingStore

# ── Config ────────────────────────────────────────────────────────────
SAMPLE_FILES = [
    "data/VinPolicys/01_Sexual_Misconduct_Response_Guideline.md",
    "data/VinPolicys/02_Admissions_Regulations_GME_Programs.md",
    "data/VinPolicys/03_Cam_Ket_Chat_Luong_Dao_Tao.md",
    "data/VinPolicys/04_Chat_Luong_Dao_Tao_Thuc_Te.md",
    "data/VinPolicys/05_Doi_Ngu_Giang_Vien_Co_Huu.md",
    "data/VinPolicys/06_English_Language_Requirements.md",
    "data/VinPolicys/07_Lab_Management_Regulations.md",
    "data/VinPolicys/08_Library_Access_Services_Policy.md",
    "data/VinPolicys/09_Student_Grade_Appeal_Procedures.md",
    "data/VinPolicys/10_Tieu_Chuan_ANAT_PCCN.md",
    "data/VinPolicys/11_Quy_Dinh_Xu_Ly_Su_Co_Chay.md",
    "data/VinPolicys/12_Scholarship_Maintenance_Criteria.md",
    "data/VinPolicys/13_Student_Academic_Integrity.md",
    "data/VinPolicys/14_Student_Award_Policy.md",
    "data/VinPolicys/15_Student_Code_of_Conduct.md",
]

QUESTIONS = [
    "What are all the conditions a student must maintain to stay in good academic standing at VinUni?",
    "What safety and conduct regulations must students follow when using VinUni campus facilities?",
    "What are the admission and language requirements for students entering medical programs at VinUni?",
    "What procedures and consequences apply when a student breaks university rules?",
    "How does VinUni evaluate and ensure the quality of its academic programs and teaching staff?",
]

CACHE_FILE = Path("data/chunk_cache.json")
CHUNK_SIZE = 800
SEMANTIC_THRESHOLD = 0.5
TOP_K = 3


# ── LLM Factory ───────────────────────────────────────────────────────

def demo_llm(prompt: str) -> str:
    """Mock LLM — returns a preview of the prompt (no API call)."""
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] {preview}..."


def openai_llm(prompt: str) -> str:
    """Real LLM using OpenAI GPT-4o-mini."""
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for VinUniversity students and staff. "
                    "Answer questions based ONLY on the provided context. "
                    "Be concise, accurate, and respond in the same language as the question. "
                    "If the context is insufficient, say so clearly."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=600,
    )
    return response.choices[0].message.content


# ── Embedding Cache ───────────────────────────────────────────────────

def save_cache(records: list[dict], path: Path) -> None:
    """Save chunk records (with embeddings) to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  Cache saved -> {path} ({len(records)} chunks, {size_mb:.1f} MB)")


def load_cache(path: Path) -> list[dict] | None:
    """Load chunk records from JSON cache. Returns None if not found."""
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  Cache loaded <- {path} ({len(records)} chunks, {size_mb:.1f} MB)")
    return records


def build_store_from_cache(records: list[dict], embedder) -> EmbeddingStore:
    """Inject pre-embedded records into EmbeddingStore (no re-embedding)."""
    store = EmbeddingStore(collection_name="vinpolicys_cache", embedding_fn=embedder)
    store._store = [
        {
            "id": r["id"],
            "content": r["content"],
            "embedding": r["embedding"],
            "metadata": r["metadata"],
        }
        for r in records
    ]
    return store


# ── Document Loading & Chunking ───────────────────────────────────────

def load_documents_from_files(file_paths: list[str]) -> list[Document]:
    """Load raw documents from file paths."""
    allowed = {".md", ".txt"}
    docs: list[Document] = []
    for raw_path in file_paths:
        path = Path(raw_path)
        if path.suffix.lower() not in allowed:
            print(f"  Skipping unsupported: {path}")
            continue
        if not path.exists():
            print(f"  Skipping missing: {path}")
            continue
        docs.append(Document(
            id=path.stem,
            content=path.read_text(encoding="utf-8"),
            metadata={"source": str(path), "extension": path.suffix.lower()},
        ))
    return docs


def chunk_and_embed(docs: list[Document], embedder) -> list[dict]:
    """
    Chunk documents with SemanticChunker (parallel) then embed all chunks
    in a single batch call. Returns serializable record dicts.
    """
    chunker = SemanticChunker(
        embedding_fn=embedder, threshold=SEMANTIC_THRESHOLD, max_chunk_size=CHUNK_SIZE
    )

    def chunk_one(doc: Document) -> list[Document]:
        chunks = chunker.chunk(doc.content)
        print(f"  {doc.id}: {len(chunks)} chunks")
        return [
            Document(
                id=f"{doc.id}_{i}",
                content=chunk_text,
                metadata={**doc.metadata, "chunk_index": i, "doc_id": doc.id},
            )
            for i, chunk_text in enumerate(chunks)
        ]

    # Parallel chunking (each file → 1 batch embed call inside SemanticChunker)
    chunked: list[Document] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(chunk_one, doc): doc for doc in docs}
        for future in as_completed(futures):
            chunked.extend(future.result())

    print(f"\n  Total chunks: {len(chunked)}")
    print("  Embedding all chunks (1 batch API call)...")

    # Batch embed all chunks for the store
    if hasattr(embedder, "embed_batch"):
        contents = [d.content for d in chunked]
        embeddings = embedder.embed_batch(contents)
    else:
        embeddings = [embedder(d.content) for d in chunked]

    records = [
        {
            "id": doc.id,
            "content": doc.content,
            "embedding": emb,
            "metadata": doc.metadata,
        }
        for doc, emb in zip(chunked, embeddings)
    ]
    return records


# ── Main Demo ─────────────────────────────────────────────────────────

def run_manual_demo(
    queries: list[str] | None = None,
    sample_files: list[str] | None = None,
    force_rebuild: bool = False,
    use_real_llm: bool = False,
) -> int:
    files = sample_files or SAMPLE_FILES
    queries_to_run = queries or QUESTIONS

    load_dotenv(override=False)

    # ── Pick embedder ────────────────────────────────────────────────
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "openai":
        try:
            embedder = OpenAIEmbedder(
                model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)
            )
        except Exception as e:
            print(f"  OpenAI embedder failed ({e}), falling back to mock.")
            embedder = _mock_embed
    elif provider == "local":
        try:
            embedder = LocalEmbedder(
                model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL)
            )
        except Exception as e:
            print(f"  Local embedder failed ({e}), falling back to mock.")
            embedder = _mock_embed
    else:
        embedder = _mock_embed

    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    print("=" * 68)
    print(f"  VinPolicys RAG — embedding={backend}")
    print(f"  LLM={('gpt-4o-mini (real)' if use_real_llm else 'demo (mock)')}")
    print("=" * 68)

    # ── Load or build cache ──────────────────────────────────────────
    records: list[dict] | None = None

    if not force_rebuild:
        print("\n[1/3] Checking embedding cache...")
        records = load_cache(CACHE_FILE)

    if records is None:
        print("\n[1/3] Building index from scratch...")
        docs = load_documents_from_files(files)
        if not docs:
            print("ERROR: No valid documents loaded. Check SAMPLE_FILES paths.")
            return 1

        print(f"  Loaded {len(docs)} documents")
        print("\n  Chunking (SemanticChunker, parallel)...")
        records = chunk_and_embed(docs, embedder)
        save_cache(records, CACHE_FILE)
    else:
        print("[1/3] Using cached index — no embedding API calls needed.")

    # ── Build in-memory store from records ───────────────────────────
    print(f"\n[2/3] Loading {len(records)} chunks into vector store...")
    store = build_store_from_cache(records, embedder)
    print(f"  Store ready: {store.get_collection_size()} chunks")

    # ── Pick LLM ────────────────────────────────────────────────────
    llm_fn = openai_llm if use_real_llm else demo_llm

    agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn)

    # ── Run queries & export ─────────────────────────────────────────
    output_file = "benchmark.md"
    print(f"\n[3/3] Running {len(queries_to_run)} queries -> {output_file}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# RAG System Benchmark\n\n")
        f.write(f"**Embedding:** {backend}  \n")
        f.write(f"**LLM:** {'gpt-4o-mini' if use_real_llm else 'demo_llm (mock)'}  \n")
        f.write(f"**Total Chunks:** {store.get_collection_size()}  \n")
        f.write(f"**Chunker:** SemanticChunker (threshold={SEMANTIC_THRESHOLD}, max={CHUNK_SIZE})  \n\n")
        f.write("---\n\n")

        for i, query in enumerate(queries_to_run, start=1):
            print(f"\n  Q{i}: {query}")
            f.write(f"## Query #{i}\n**{query}**\n\n")

            results = store.search(query, top_k=TOP_K)
            f.write(f"### Search Results (Top {TOP_K})\n")
            for j, r in enumerate(results, 1):
                score = r["score"]
                source = r["metadata"].get("source", "?")
                preview = r["content"].replace("\n", " ")
                f.write(f"**{j}.** `score={score:.3f}` | `{source}`\n")
                f.write(f"> {preview}\n\n")

            answer = agent.answer(query, top_k=TOP_K)
            f.write("### Agent Answer\n")
            f.write(f"{answer}\n\n---\n\n")

            print(f"     -> Done.")

    print(f"\n  Results saved to '{output_file}'")
    print("=" * 68)
    return 0


def main() -> int:
    args = sys.argv[1:]

    force_rebuild = "--rebuild" in args
    use_real_llm = "--real-llm" in args

    # Strip flags from args to get the query (if any)
    query_parts = [a for a in args if not a.startswith("--")]
    queries = [" ".join(query_parts).strip()] if query_parts else None

    return run_manual_demo(
        queries=queries,
        force_rebuild=force_rebuild,
        use_real_llm=use_real_llm,
    )


if __name__ == "__main__":
    raise SystemExit(main())
