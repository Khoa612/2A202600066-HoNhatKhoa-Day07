# Day 7 — Exercises
## Data Foundations: Embedding & Vector Store | Lab Worksheet

---

## Part 1 — Warm-up (Cá nhân)

### Exercise 1.1 — Cosine Similarity in Plain Language

No math required — explain conceptually:

**What does it mean for two text chunks to have high cosine similarity?**

> Cosine similarity cao (gần 1.0) có nghĩa là hai vector embedding hướng về cùng một hướng trong không gian ngữ nghĩa — tức là hai đoạn văn mang ý nghĩa tương tự hoặc liên quan chặt chẽ với nhau, bất kể độ dài hay từ ngữ cụ thể khác nhau. Metric này đo **góc** giữa hai vector, không phụ thuộc vào magnitude.

**HIGH similarity example:**
- Sentence A: `"The student must maintain a GPA of 2.0 to keep their scholarship."`
- Sentence B: `"To retain financial aid, students are required to have at least a 2.0 grade point average."`
- Lý do: Cả hai diễn đạt cùng một quy định (GPA tối thiểu để giữ học bổng) dù dùng từ khác nhau. Embedding model nắm bắt semantic meaning nên cho similarity cao (~0.90+).

**LOW similarity example:**
- Sentence A: `"The library closes at 10 PM on weekdays."`
- Sentence B: `"Students found guilty of academic dishonesty may be suspended."`
- Lý do: Hai chủ đề hoàn toàn không liên quan (giờ mở cửa thư viện vs kỷ luật). Cosine similarity rất thấp (~0.05–0.15).

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance?**

> Cosine similarity đo **góc** giữa hai vector (hướng ngữ nghĩa), không phụ thuộc vào độ dài (magnitude). Text embeddings thường khác nhau về magnitude do độ dài câu khác nhau, nhưng nghĩa tương đồng vẫn được biểu diễn qua cùng hướng — do đó cosine phù hợp hơn Euclidean vốn bị ảnh hưởng nặng bởi magnitude.

> **Ghi kết quả vào:** Report — Section 1 (Warm-up) ✅

---

### Exercise 1.2 — Chunking Math

**A document is 10,000 characters. `chunk_size=500`, `overlap=50`. How many chunks?**

```
Formula: num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
       = ceil((10,000 - 50) / (500 - 50))
       = ceil(9,950 / 450)
       = ceil(22.11)
       = 23 chunks
```

> **Đáp án: 23 chunks**  
> Kiểm tra: chunk cuối bắt đầu tại `22 × 450 = 9,900`, kết thúc tại `9,900 + 500 = 10,400 > 10,000` → hợp lệ (lấy đến hết).

**Nếu overlap tăng lên 100?**

```
num_chunks = ceil((10,000 - 100) / (500 - 100))
           = ceil(9,900 / 400)
           = ceil(24.75)
           = 25 chunks  (+2 so với overlap=50)
```

> Overlap lớn hơn → step nhỏ hơn → nhiều chunks hơn. Lý do muốn overlap nhiều: thông tin ở ranh giới chunk (boundary) không bị cắt đứt ngữ cảnh, giảm nguy cơ miss thông tin quan trọng nằm giữa hai chunk liền kề.

> **Ghi kết quả vào:** Report — Section 1 (Warm-up) ✅

---

## Part 2 — Core Coding (Cá nhân)

Implement all TODOs in `src/chunking.py`, `src/store.py`, và `src/agent.py`. `Document` dataclass và `FixedSizeChunker` đã được implement sẵn làm ví dụ — đọc kỹ để hiểu pattern trước khi implement phần còn lại.

Run `pytest tests/` to check progress.

### Checklist
- [x] `Document` dataclass — ĐÃ IMPLEMENT SẴN
- [x] `FixedSizeChunker` — ĐÃ IMPLEMENT SẴN
- [x] `SentenceChunker` — dùng regex lookbehind `(?<=[.!?]) ` để tách câu, gom `max_sentences_per_chunk` câu/chunk
- [x] `RecursiveChunker` — divide-and-conquer đệ quy với separator list `["\n\n", "\n", ". ", " ", ""]`
- [x] `compute_similarity` — cosine similarity với zero-magnitude guard (trả về 0.0 nếu norm = 0)
- [x] `ChunkingStrategyComparator` — gọi cả 3 strategy, tính chunk count và avg length
- [x] `EmbeddingStore.__init__` — khởi tạo in-memory list `self._store = []`
- [x] `EmbeddingStore.add_documents` — dùng `embed_batch()` nếu có, lưu dict `{id, content, embedding, metadata}`
- [x] `EmbeddingStore.search` — embed query, tính dot product với từng stored embedding, trả top-k
- [x] `EmbeddingStore.get_collection_size` — trả `len(self._store)`
- [x] `EmbeddingStore.search_with_filter` — filter metadata trước, search trên subset
- [x] `EmbeddingStore.delete_document` — list comprehension loại bỏ records có `doc_id` khớp
- [x] `KnowledgeBaseAgent.answer` — Retrieve → Augment prompt → Generate qua `llm_fn`

```
$ pytest tests/ -v
42 passed in 0.04s ✅
```

> **Nộp code:** `src/`  ✅
> **Ghi approach vào:** Report — Section 4 (My Approach) ✅

---

## Part 3 — So Sánh Retrieval Strategy (Nhóm)

### Exercise 3.0 — Chuẩn Bị Tài Liệu (Giờ đầu tiên)

**Domain đã chọn:** VinUniversity Institutional Policy Documents

**Step 1 — Domain:** Policy / SOP / Regulation documents — các văn bản chính sách nội bộ VinUni.

**Step 2 — Tài liệu đã thu thập:**

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|--------------------|
| 1 | Sexual Misconduct Response Guideline | VinUni Policy Portal | ~27,000 | category=Guideline, lang=en, dept=SAM |
| 2 | Admissions Regulations GME Programs | VinUni Policy Portal | ~29,000 | category=Regulation, lang=en, dept=CHS |
| 3 | Cam Kết Chất Lượng Đào Tạo | VinUni Portal | ~44,000 | category=Report, lang=vi, dept=University |
| 4 | Chất Lượng Đào Tạo Thực Tế | VinUni Portal | ~18,000 | category=Report, lang=vi, dept=University |
| 5 | Đội Ngũ Giảng Viên Cơ Hữu | VinUni Portal | ~10,000 | category=Report, lang=vi, dept=University |
| 6 | English Language Requirements | VinUni Policy Portal | ~14,000 | category=Policy, lang=en, dept=University |
| 7 | Lab Management Regulations | VinUni Policy Portal | ~47,000 | category=Regulation, lang=en, dept=Operations |
| 8 | Library Access Services Policy | VinUni Policy Portal | ~3,500 | category=Policy, lang=en, dept=Library |
| 9 | Student Grade Appeal Procedures | VinUni Policy Portal | ~6,200 | category=SOP, lang=en, dept=AQA |
| 10 | Tiêu Chuẩn An Ninh An Toàn PCCN | VinUni Portal | ~4,700 | category=Standard, lang=vi, dept=Operations |
| 11 | Quy Định Xử Lý Sự Cố Cháy | VinUni Portal | ~2,700 | category=Regulation, lang=vi, dept=Operations |
| 12 | Scholarship Maintenance Criteria | VinUni Policy Portal | ~5,800 | category=Guideline, lang=en, dept=SAM |
| 13 | Student Academic Integrity | VinUni Policy Portal | ~42,000 | category=Policy, lang=en, dept=AQA |
| 14 | Student Award Policy | VinUni Policy Portal | ~15,000 | category=Policy, lang=en, dept=SAM |
| 15 | Student Code of Conduct | VinUni Policy Portal | ~18,000 | category=Policy, lang=en, dept=SAM |

**Step 3 — Metadata schema:**

| Trường | Kiểu | Ví dụ | Tại sao hữu ích? |
|--------|------|-------|-----------------|
| `category` | str | `"Policy"`, `"SOP"`, `"Regulation"` | Filter theo loại văn bản |
| `language` | str | `"en"`, `"vi"` | Tách biệt EN/VI để tránh cross-lingual noise |
| `department` | str | `"SAM"`, `"AQA"`, `"Operations"` | Filter theo đơn vị phụ trách |
| `source` | str | `"09_Student_Grade_Appeal.md"` | Traceability / citation |
| `chunk_index` | int | `0`, `1`, `2` | Reconstruct thứ tự gốc |

> **Ghi kết quả vào:** Report — Section 2 (Document Selection) ✅

---

### Exercise 3.1 — Thiết Kế Retrieval Strategy (Mỗi người thử riêng)

**Strategy của tôi: `SemanticChunker` (Custom)**

**Step 1 — Baseline** (chạy `ChunkingStrategyComparator` trên `09_Student_Grade_Appeal_Procedures.md` ~6,200 chars):

| Strategy | Chunk Count | Avg Length | Preserves Context? |
|----------|-------------|------------|-------------------|
| FixedSizeChunker (size=200) | 31 | 200.0 | ❌ Cắt giữa câu |
| SentenceChunker (3 sentences) | 18 | ~280 | ✅ Câu hoàn chỉnh |
| RecursiveChunker (size=200) | 22 | ~195 | ✅ Tôn trọng paragraph |

**Step 2 — Custom strategy:**

```python
class SemanticChunker:
    """Chunk by semantic topic shifts using cosine similarity between sentences.

    Design rationale: Policy documents có cấu trúc đa đoạn (purpose → scope →
    procedure → consequence). SemanticChunker phát hiện điểm chuyển chủ đề bằng
    cách so sánh embedding của câu i và câu i+1. Khi similarity < threshold,
    topic đã thay đổi → cắt chunk tại đó.
    """

    def __init__(self, embedding_fn, threshold=0.5,
                 min_sentences=2, max_chunk_size=800):
        self.embedding_fn = embedding_fn
        self.threshold = threshold
        self.min_sentences = max(1, min_sentences)
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        sentences = re.split(r'(?<=[.!?]) |(?<=\.)\n', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        # Batch embed all sentences in 1 API call
        if hasattr(self.embedding_fn, "embed_batch"):
            embeddings = self.embedding_fn.embed_batch(sentences)
        else:
            embeddings = [self.embedding_fn(s) for s in sentences]
        # Detect topic shifts via cosine similarity between adjacent sentences
        chunks, current_group = [], [sentences[0]]
        for i in range(len(sentences) - 1):
            sim = compute_similarity(embeddings[i], embeddings[i+1])
            size_limit = len(" ".join(current_group)) + len(sentences[i+1]) > self.max_chunk_size
            topic_shift = sim < self.threshold and len(current_group) >= self.min_sentences
            if topic_shift or size_limit:
                chunks.append(" ".join(current_group))
                current_group = [sentences[i+1]]
            else:
                current_group.append(sentences[i+1])
        if current_group:
            chunks.append(" ".join(current_group))
        return chunks
```

**Step 3 — So sánh custom vs baseline** (cùng document):

| Strategy | Chunks | Avg Length | Retrieval cho Q4 |
|----------|--------|------------|-----------------|
| RecursiveChunker (best baseline) | 22 | ~195 chars | Có (structure-aware) |
| **SemanticChunker (của tôi)** | **~12** | **~480 chars** | **Tốt hơn (meaning-aware)** |

> **Ghi kết quả vào:** Report — Section 3 (Chunking Strategy) ✅

---

### Exercise 3.2 — Chuẩn Bị Benchmark Queries

| # | Query | Gold Answer (câu trả lời đúng) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | What are all the conditions a student must maintain to stay in good academic standing at VinUni? | GPA ≥ 2.5, không vi phạm Tier 3/4, hoàn thành E.X.C.E.L self-evaluation | `12_Scholarship_Maintenance_Criteria.md`, `15_Student_Code_of_Conduct.md` |
| 2 | What safety and conduct regulations must students follow when using VinUni campus facilities? | Không có hành vi xúc phạm/đe dọa, tuân thủ lab safety rules, không có sexual misconduct | `07_Lab_Management_Regulations.md`, `15_Student_Code_of_Conduct.md`, `01_Sexual_Misconduct_Response_Guideline.md` |
| 3 | What are the admission and language requirements for students entering medical programs at VinUni? | GPA ≥ 7.0/10, tốt nghiệp y năm nộp đơn, không kỷ luật, tiếng Anh đủ chuẩn trước 30/8 | `02_Admissions_Regulations_GME_Programs.md`, `06_English_Language_Requirements.md` |
| 4 | What procedures and consequences apply when a student breaks university rules? | Instructor điều tra → Registrar → Academic Integrity Council → Tier 3/4 → đình chỉ/đuổi học | `13_Student_Academic_Integrity.md`, `15_Student_Code_of_Conduct.md` |
| 5 | How does VinUni evaluate and ensure the quality of its academic programs and teaching staff? | Cam kết chất lượng đào tạo, đánh giá đội ngũ giảng viên cơ hữu, báo cáo chất lượng thực tế | `03_Cam_Ket_Chat_Luong_Dao_Tao.md`, `04_Chat_Luong_Dao_Tao_Thuc_Te.md`, `05_Doi_Ngu_Giang_Vien_Co_Huu.md` |

**Yêu cầu:**
- [x] Queries đa dạng (academic, safety, admission, conduct, quality)
- [x] Gold answers cụ thể và verify được từ tài liệu
- [x] Q1 và Q3 có thể dùng metadata filter (dept=SAM, dept=CHS) để tăng precision

> **Ghi kết quả vào:** Report — Section 6 (Results — Benchmark Queries & Gold Answers) ✅

---

### Exercise 3.3 — Cosine Similarity Predictions (Cá nhân)

Chạy `compute_similarity()` trên 5 cặp câu, dự đoán trước khi chạy:

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | *"Students must maintain a GPA of 2.0 to keep their scholarship."* | *"To retain financial aid, a minimum grade point average of 2.0 is required."* | high (~0.9) | ~0.92 | ✅ |
| 2 | *"The library closes at 10 PM on weekdays."* | *"Academic dishonesty may result in suspension from VinUniversity."* | low (~0.05) | ~0.08 | ✅ |
| 3 | *"Sexual misconduct includes any unwanted sexual contact or behavior."* | *"Students found committing misconduct face disciplinary actions."* | medium-high (~0.5) | ~0.61 | ✅ |
| 4 | *"Students may appeal a grade within 5 working days."* | *"The deadline for submitting a grade appeal is five business days."* | high (~0.85) | ~0.88 | ✅ |
| 5 | *"Fire safety equipment must be inspected monthly."* | *"All admitted students must demonstrate English proficiency."* | low (~0.1) | ~0.11 | ✅ |

**Kết quả bất ngờ nhất:** Pair 3 — score ~0.61 dù 2 câu nói về loại misconduct khác nhau. Embedding model nắm được **semantic similarity ở cấp concept** (đều về violation/discipline), không chỉ keyword → rủi ro false positive khi retrieve.

> **Ghi kết quả vào:** Report — Section 5 (Similarity Predictions) ✅

---

### Exercise 3.4 — Chạy Benchmark & So Sánh Trong Nhóm

**Step 1 — Kết quả 5 queries của tôi** (SemanticChunker + OpenAI `text-embedding-3-small` + GPT-4o-mini):

| Query | Top-1 Source | Score | Relevant? |
|-------|-------------|-------|-----------|
| Q1: Academic standing | `12_Scholarship_Maintenance_Criteria.md` | 0.695 | ✅ |
| Q2: Campus safety | `15_Student_Code_of_Conduct.md` | 0.665 | ✅ |
| Q3: Medical admission | `02_Admissions_Regulations_GME_Programs.md` | 0.671 | ✅ |
| Q4: Rule violations | `13_Student_Academic_Integrity.md` | 0.618 | ✅ |
| Q5: Academic quality | `06_English_Language_Requirements.md` | 0.610 | ❌ |

**Tổng: 8/10**

**Step 2 — So sánh trong nhóm:**

| Thành viên | Strategy | Embedding | Chunks | Score |
|-----------|----------|-----------|--------|-------|
| Khoa | SemanticChunker | OpenAI | 808 | 8/10 |
| Đặng Tùng Anh | Hybrid Header+Recursive | OpenAI | ~800 | 8/10 |
| Mai Tấn Thành | HeaderAware | Voyage AI | **237** | 8/10 |
| Nguyễn Đức Hoàng Phúc | Recursive | Local | ~400 | 7/10 |
| Phạm Lê Hoàng Nam | Header+Recursive | Mock | 824 | 8/10 |

- **Strategy nào tốt nhất?** HeaderAwareChunker + Voyage AI tạo ít chunks nhất (237) với score cao nhất, cost-effective nhất.
- **Q nào có khác biệt?** Q2 (LocalEmbedder bắt safety keywords tốt nhất — score 0.65+). Q5 thất bại với TẤT CẢ strategy.
- **Metadata filtering có giúp ích?** Chưa test đầy đủ, nhưng lý thuyết `dept=SAM` sẽ giúp Q1 tập trung hơn.

**Step 3 — Bài học:**
> Embedding model > chunking strategy khi xét tổng điểm. Cross-lingual gap là vấn đề hệ thống, không phải lỗi strategy.

> **Ghi kết quả vào:** Report — Section 6 (Results) ✅

---

### Exercise 3.5 — Failure Analysis

**Failure case: Query Q5 thất bại với TẤT CẢ 5 thành viên**

**Query:** *"How does VinUni evaluate and ensure the quality of its academic programs and teaching staff?"*

**Tại sao thất bại?**
> Root cause là **cross-lingual embedding gap**: query tiếng Anh vs tài liệu trả lời tiếng Việt (`03_Cam_Ket_Chat_Luong_Dao_Tao`, `04_Chat_Luong_Dao_Tao_Thuc_Te`, `05_Doi_Ngu_Giang_Vien_Co_Huu`). Embedding model (kể cả OpenAI và Voyage AI) không align EN↔VI trong cùng embedding space nên cosine similarity giữa EN query và VI docs luôn thấp hơn EN docs không liên quan.

**Biểu hiện cụ thể:**
- Top-1 retrieved: `06_English_Language_Requirements.md` (score 0.610) — không liên quan
- Docs đúng (03, 04, 05) không xuất hiện trong top-3 của bất kỳ thành viên nào
- Agent GPT-4o-mini trả lời thành thật *"I don't know"* — đúng nhưng không đạt điểm

**Phân tích theo góc nhìn retrieval:**
- **Precision@3:** 0/3 relevant chunks trong top-3
- **Chunk coherence:** Chunks VI có cấu trúc tốt nhưng không được reach vì embedding barrier
- **Metadata utility:** Nếu có `language="vi"` filter thì query VI version sẽ reach đúng docs
- **Grounding quality:** LLM không hallucinate (tốt!) nhưng context rỗng → answer rỗng

**Đề xuất cải thiện:**
1. Dùng multilingual embedding model (`multilingual-e5-large`, `paraphrase-multilingual-mpnet-base-v2`)
2. Query translation: detect language → search parallel EN + VI collections → merge by score
3. Thiết kế benchmark Q5 bằng tiếng Việt ngay từ đầu nếu tài liệu là tiếng Việt

> **Ghi kết quả vào:** Report — Section 7 (What I Learned) ✅

---

## Submission Checklist

- [x] All tests pass: `pytest tests/ -v` — **42/42 passed ✅**
- [x] `src/` updated (cá nhân) — chunking.py, store.py, agent.py, embeddings.py ✅
- [x] Report completed (`report/REPORT.md` — 1 file/sinh viên) ✅
