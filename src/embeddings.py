from __future__ import annotations

import hashlib
import math

LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_PROVIDER_ENV = "EMBEDDING_PROVIDER"


class MockEmbedder:
    """Deterministic embedding backend used by tests and default classroom runs."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self._backend_name = "mock embeddings fallback"

    def __call__(self, text: str) -> list[float]:
        digest = hashlib.md5(text.encode()).hexdigest()
        seed = int(digest, 16)
        vector = []
        for _ in range(self.dim):
            seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
            vector.append((seed / 0xFFFFFFFF) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts. Returns a list of vectors in the same order."""
        return [self(t) for t in texts]


class LocalEmbedder:
    """Sentence Transformers-backed local embedder."""

    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._backend_name = model_name
        self.model = SentenceTransformer(model_name)

    def __call__(self, text: str) -> list[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return [float(value) for value in embedding]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch encode: SentenceTransformer handles this natively and efficiently."""
        embeddings = self.model.encode(texts, normalize_embeddings=True, batch_size=64)
        return [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]


class OpenAIEmbedder:
    """OpenAI embeddings API-backed embedder."""

    # OpenAI allows up to 2048 inputs per request
    _BATCH_LIMIT = 2048

    def __init__(self, model_name: str = OPENAI_EMBEDDING_MODEL) -> None:
        from openai import OpenAI

        self.model_name = model_name
        self._backend_name = model_name
        self.client = OpenAI()

    def __call__(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model_name, input=text)
        return [float(value) for value in response.data[0].embedding]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of texts in a SINGLE API call (or minimal batches).

        OpenAI accepts up to 2048 inputs per request — so instead of N API
        calls for N sentences, this does ceil(N / 2048) calls total.
        For typical documents (< 300 sentences) this means exactly 1 call.
        """
        results: list[list[float]] = []
        for start in range(0, len(texts), self._BATCH_LIMIT):
            batch = texts[start : start + self._BATCH_LIMIT]
            response = self.client.embeddings.create(
                model=self.model_name,
                input=batch,
            )
            # Response items are ordered by index, safe to iterate directly
            for item in response.data:
                results.append([float(v) for v in item.embedding])
        return results


_mock_embed = MockEmbedder()
