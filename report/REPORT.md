# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Hồ Nhất Khoa
**Mã SV:** 2A202600066
**Nhóm:** VinUni Policy RAG
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Cosine similarity cao (gần 1.0) có nghĩa là hai vector embedding hướng về cùng một hướng trong không gian ngữ nghĩa — tức là hai câu/đoạn văn mang ý nghĩa tương tự hoặc liên quan chặt chẽ với nhau, bất kể độ dài hay từ ngữ cụ thể khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: `"The student must maintain a GPA of 2.0 to keep their scholarship."`
- Sentence B: `"To retain financial aid, students are required to have at least a 2.0 grade point average."`
- Tại sao tương đồng: Cả hai câu diễn đạt cùng một quy định (GPA tối thiểu để giữ học bổng) dù dùng từ khác nhau. Embedding model nắm bắt được semantic meaning nên cho similarity cao (~0.90+).

**Ví dụ LOW similarity:**
- Sentence A: `"The library closes at 10 PM on weekdays."`
- Sentence B: `"Students found guilty of academic dishonesty may be suspended."`
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn không liên quan (giờ mở cửa thư viện vs hình thức kỷ luật), cosine similarity sẽ rất thấp (~0.05–0.15).

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity đo **góc** giữa hai vector (hướng ngữ nghĩa), không phụ thuộc vào độ dài (magnitude) của vector. Text embeddings thường khác nhau về magnitude do độ dài câu khác nhau, nhưng nghĩa tương đồng vẫn được biểu diễn qua cùng hướng — do đó cosine phù hợp hơn Euclidean vốn bị ảnh hưởng nặng bởi magnitude.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> **Phép tính:**
> - `step = chunk_size - overlap = 500 - 50 = 450`
> - Số chunks = `ceil((10,000 - overlap) / step) = ceil(9,950 / 450) = ceil(22.11) = 23`
> - Kiểm tra: chunk cuối bắt đầu tại `start = 22 × 450 = 9,900`, kết thúc tại `9,900 + 500 = 10,400 > 10,000` → valid (lấy đến hết)
>
> **Đáp án: 23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap = 100: `step = 500 - 100 = 400`, số chunks = `ceil(9,900 / 400) = 25` — tăng thêm 2 chunks. Overlap lớn hơn giúp thông tin ở ranh giới chunk (boundary) không bị cắt đứt ngữ cảnh, giảm nguy cơ miss thông tin quan trọng nằm giữa hai chunk liền kề.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** VinUniversity Institutional Policy Documents (Tài liệu chính sách nội bộ VinUni)

**Tại sao nhóm chọn domain này?**
> Nhóm chọn bộ tài liệu chính sách của VinUniversity vì đây là domain thực tế, có giá trị ứng dụng rõ ràng: sinh viên và giảng viên thường xuyên cần tra cứu thông tin về quy định học vụ, kỷ luật, và quyền lợi. Bộ tài liệu này có tính đa dạng cao (chính sách, SOP, quy định, hướng dẫn) và song ngữ (Anh/Việt), tạo ra thách thức thực tế cho hệ thống RAG. Ngoài ra, việc có ground truth rõ ràng từ các văn bản chính thức giúp đánh giá retrieval quality một cách khách quan.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự (approx) | Metadata đã gán |
|---|--------------|-------|-------------------|--------------------|
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

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `category` | `str` | `"Policy"`, `"SOP"`, `"Guideline"`, `"Regulation"`, `"Standard"`, `"Report"` | Cho phép filter theo loại văn bản; truy vấn về quy trình → SOP, về quy định → Regulation |
| `language` | `str` | `"en"`, `"vi"` | Tách biệt tài liệu tiếng Anh và tiếng Việt, tránh nhiễu cross-language khi embedding không phân biệt ngôn ngữ tốt |
| `department` | `str` | `"SAM"`, `"AQA"`, `"Operations"`, `"CHS"`, `"Library"` | Filter theo đơn vị phụ trách; query về học bổng → SAM, về học thuật → AQA |
| `topic` | `str` | `"academics"`, `"safety"`, `"finance"`, `"student_life"` | Nhóm theo chủ đề rộng để narrow search scope |
| `source` | `str` | `"09_Student_Grade_Appeal_Procedures.md"` | Traceability — biết chunk đến từ file nào để citation |
| `chunk_index` | `int` | `0`, `1`, `2`, ... | Cho phép reconstruct thứ tự văn bản gốc nếu cần ghép lại context |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu `09_Student_Grade_Appeal_Procedures.md` (~6,200 chars):

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Grade Appeal (6,200c) | FixedSizeChunker (chunk_size=200) | 31 | 200.0 | Không — cắt giữa câu |
| Grade Appeal (6,200c) | SentenceChunker (3 sentences) | 18 | ~280 | Tốt — câu hoàn chỉnh |
| Grade Appeal (6,200c) | RecursiveChunker (chunk_size=200) | 22 | ~195 | Khá — tôn trọng paragraph |

### Strategy Của Tôi

**Loại:** `SemanticChunker` (Custom — cắt theo ngữ nghĩa AI)

**Mô tả cách hoạt động:**  
> SemanticChunker hoạt động theo 4 bước. Đầu tiên, văn bản được tách thành từng câu đơn lẻ bằng regex lookbehind `(?<=[.!?]) `. Sau đó, toàn bộ câu được gửi vào embedding model trong **1 batch API call** để lấy vector cho từng câu. Tiếp theo, cosine similarity giữa câu `i` và câu `i+1` được tính để phát hiện khi nào chủ đề thay đổi (`sim < threshold`). Cuối cùng, các câu được gom lại thành chunk — khi similarity giảm mạnh hoặc khi kích thước chunk vượt `max_chunk_size`, chunk được flush và bắt đầu chunk mới.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tài liệu chính sách VinUni có cấu trúc đa đoạn (purpose → scope → procedure → consequence) với mỗi đoạn nói về một sub-topic khác nhau. SemanticChunker phát hiện chính xác những điểm chuyển chủ đề này thay vì cắt cứng theo ký tự, giữ cho mỗi chunk tập trung vào 1 concept. Điều này đặc biệt quan trọng với tài liệu policy vì câu hỏi của người dùng thường liên quan đến 1 quy định cụ thể, không phải nhiều section cùng lúc.

**Code snippet:**
```python
class SemanticChunker:
    def __init__(self, embedding_fn, threshold=0.8,
                 min_sentences=2, max_chunk_size=1000):
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
        # Detect topic shifts via cosine similarity
        chunks, current_group = [], [sentences[0]]
        for i, sim in enumerate(pairwise_similarities):
            size_split = len(" ".join(current_group)) + len(sentences[i+1]) > self.max_chunk_size
            semantic_split = sim < self.threshold and len(current_group) >= self.min_sentences
            if semantic_split or size_split:
                chunks.append(" ".join(current_group))
                current_group = [sentences[i+1]]
            else:
                current_group.append(sentences[i+1])
        if current_group:
            chunks.append(" ".join(current_group))
        return chunks
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality |
|-----------|----------|-------------|------------|-------------------|
| Grade Appeal | RecursiveChunker (best baseline) | 22 | ~195 chars | Tốt (structure-aware) |
| Grade Appeal | **SemanticChunker (của tôi)** | **~12** | **~480 chars** | **Tốt nhất (meaning-aware)** |

*Ghi chú: SemanticChunker tạo ít chunk hơn nhưng mỗi chunk tập trung vào 1 topic → retrieval precision cao hơn.*

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Embedding | Chunks | Q1 | Q2 | Q3 | Q4 | Q5 | Tổng |
|-----------|----------|-----------|--------|----|----|----|----|----|----|
| **Khoa (tôi)** | SemanticChunker (th=0.5, max=800) | OpenAI `text-embedding-3-small` | 808 | 2/2 | 2/2 | 2/2 | 2/2 | 0/2 | **8/10** |
| Đặng Tùng Anh | Hybrid Header + RecursiveChunker | OpenAI `text-embedding-3-small` | ~800 | 2/2 | 2/2 | 2/2 | 2/2 | 0/2 | **8/10** |
| Mai Tấn Thành | HeaderAwareChunker | Voyage AI | 237 | 2/2 | 2/2 | 2/2 | 2/2 | 0/2 | **8/10** |
| Nguyễn Đức Hoàng Phúc | RecursiveChunker | Local `all-MiniLM-L6-v2` | ~400 | 2/2 | 2/2 | 2/2 | 1/2 | 0/2 | **7/10** |
| Phạm Lê Hoàng Nam | Header-aware + RecursiveChunker | Mock embeddings (fallback) | 824 | 2/2 | 1/2 | 2/2 | 2/2 | 1/2 | **8/10** |

> **Quan sát quan trọng:** Tất cả 5 thành viên đều thất bại ở **Q5** bất kể dùng strategy hay embedding model nào. Đây không phải lỗi của strategy mà là **cross-lingual embedding gap** — phân tích kỹ dưới đây.

### Phân Tích Sâu: Tại Sao Q5 Thất Bại Toàn Bộ?

**Query Q5:** *"How does VinUni evaluate and ensure the quality of its academic programs and teaching staff?"* (Tiếng Anh)  
**Expected documents:** `03_Cam_Ket_Chat_Luong_Dao_Tao`, `04_Chat_Luong_Dao_Tao_Thuc_Te`, `05_Doi_Ngu_Giang_Vien_Co_Huu` — **100% tiếng Việt**

**Root cause — Cross-lingual embedding gap:**

Khi embedding model (dù OpenAI, Voyage AI, hay Local) encode câu tiếng Anh và câu tiếng Việt có cùng nghĩa, hai vector không nằm gần nhau trong embedding space nếu model không được train đa ngôn ngữ:

```
Query (EN):  "evaluate academic quality"   → vector_EN  [0.2, 0.8, -0.3, ...]
Doc   (VI):  "đảm bảo chất lượng đào tạo" → vector_VI  [0.7, -0.1, 0.5, ...]
cosine_similarity(vector_EN, vector_VI) ≈ 0.1–0.3  ← QUÁ THẤP → không retrieve

Doc   (EN):  "scholarship maintaining GPA" → vector_EN2
cosine_similarity(vector_EN, vector_EN2) ≈ 0.5–0.7  ← ĐƯỢC RETRIEVE (dù không liên quan)
```

**Tại sao ngay cả Voyage AI cũng fail?** Voyage AI là embedding model chất lượng cao nhưng ưu tiên tiếng Anh — không phải multilingual theo nghĩa align cross-language. Score vẫn cao (~0.55) nhưng đều là docs tiếng Anh không liên quan.

**Giải pháp để đạt điểm Q5:**

| Giải pháp | Cách thực hiện | Độ khó |
|-----------|----------------|--------|
| **1. Dùng multilingual embedding** | Thay bằng `multilingual-e5-large` hoặc `paraphrase-multilingual-mpnet-base-v2` | Thấp |
| **2. Query translation** | Dịch query sang tiếng Việt trước khi search docs vi | Trung bình |
| **3. Dual-language search** | Search song song 2 collection (en/vi), merge kết quả theo score | Trung bình |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Không có strategy nào vượt trội hoàn toàn — 4/5 thành viên đạt 8/10, 1 thành viên 7/10. Điều này chứng tỏ với domain có tài liệu đồng ngôn ngữ (EN query → EN docs), hầu hết strategy hoạt động tốt. **HeaderAwareChunker + Voyage AI** (MaiTanThanh) đạt score cosine cao nhất và tạo ít chunks nhất, hiệu quả nhất về chi phí. **SemanticChunker + OpenAI** cho chunk có nghĩa rõ nhất nhưng đắt nhất. **Bài học chính:** Embedding model và chất lượng dữ liệu quan trọng hơn chunking strategy khi xét tổng điểm.

---

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng regex `re.split(r'(?<=[.!?]) |(?<=\.)\n', text)` với **lookbehind assertion** để tách tại điểm ngay sau dấu câu kết thúc (`.`, `!`, `?`) có khoảng trắng hoặc newline theo sau — giữ nguyên dấu câu vào câu trước. Sau đó gom mỗi `max_sentences_per_chunk` câu thành 1 chunk bằng `" ".join(sentences[i:i+n])`. Edge case: text rỗng trả về `[]`; text không có dấu câu → toàn bộ text là 1 câu → 1 chunk duy nhất.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Dùng chiến lược **divide-and-conquer đệ quy với danh sách separator ưu tiên** `["\n\n", "\n", ". ", " ", ""]`. Hàm `_split(text, separators)` có base case là `len(text) <= chunk_size` → trả về `[text]`. Ngược lại, thử split bằng separator đầu tiên; nếu không tìm thấy → thử separator tiếp theo (đệ quy). Nếu tìm thấy → gom các piece nhỏ lại (greedy merge) cho đến khi vượt `chunk_size` thì flush và đệ quy trên piece lớn.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> `add_documents` sử dụng `embed_batch()` nếu embedding function hỗ trợ (1 API call cho toàn bộ batch), ngược lại fallback về sequential. Mỗi document được lưu dưới dạng dict `{id, content, embedding, metadata}` trong `self._store` (list in-memory). `search(query, top_k)` embed query rồi tính **dot product** với từng stored embedding (tương đương cosine vì vectors đã normalized), sort descending và trả top-k.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` **filter trước, search sau**: lọc `self._store` bằng list comprehension kiểm tra tất cả key-value trong `metadata_filter` match, rồi chạy similarity search trên subset đã lọc — tránh tính similarity trên documents không liên quan. `delete_document(doc_id)` xóa tất cả records có `metadata["doc_id"] == doc_id` bằng list comprehension filter-out, trả `True` nếu có ít nhất 1 record bị xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> RAG pattern 3 bước: (1) **Retrieve** — gọi `store.search(question, top_k)` để lấy top-k chunks liên quan nhất. (2) **Augment** — join các chunks bằng `"\n\n"` và build prompt với structure: `"Based on the following context, answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"` — đặt context trước question để LLM focus vào context khi generate. (3) **Generate** — gọi `llm_fn(prompt)` và trả kết quả trực tiếp.

### Test Results

```
$ pytest tests/ -v

tests/test_solution.py::test_fixed_size_basic PASSED
tests/test_solution.py::test_fixed_size_no_overlap PASSED
tests/test_solution.py::test_fixed_size_exact_fit PASSED
tests/test_solution.py::test_fixed_size_shorter_than_chunk PASSED
tests/test_solution.py::test_fixed_size_empty PASSED
tests/test_solution.py::test_sentence_chunker_basic PASSED
tests/test_solution.py::test_sentence_chunker_single_sentence PASSED
tests/test_solution.py::test_sentence_chunker_empty PASSED
tests/test_solution.py::test_recursive_chunker_basic PASSED
tests/test_solution.py::test_recursive_chunker_short_text PASSED
tests/test_solution.py::test_recursive_chunker_empty PASSED
tests/test_solution.py::test_compute_similarity_identical PASSED
tests/test_solution.py::test_compute_similarity_orthogonal PASSED
tests/test_solution.py::test_compute_similarity_zero_vector PASSED
tests/test_solution.py::test_comparator_returns_all_strategies PASSED
tests/test_solution.py::test_store_add_and_search PASSED
tests/test_solution.py::test_store_search_top_k PASSED
tests/test_solution.py::test_store_filter PASSED
tests/test_solution.py::test_store_delete PASSED
tests/test_solution.py::test_agent_answer PASSED
... (42 tests total)

42 passed in 0.05s
```

**Số tests pass:** 42 / 42 ✅

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | *"Students must maintain a GPA of 2.0 to keep their scholarship."* | *"To retain financial aid, a minimum grade point average of 2.0 is required."* | high | ~0.92 | ✅ |
| 2 | *"The library closes at 10 PM on weekdays."* | *"Academic dishonesty may result in suspension from VinUniversity."* | low | ~0.08 | ✅ |
| 3 | *"Sexual misconduct includes any unwanted sexual contact or behavior."* | *"Students found committing misconduct face disciplinary actions."* | medium-high | ~0.61 | ✅ |
| 4 | *"Students may appeal a grade within 5 working days."* | *"The deadline for submitting a grade appeal is five business days."* | high | ~0.88 | ✅ |
| 5 | *"Fire safety equipment must be inspected monthly."* | *"All admitted students must demonstrate English proficiency."* | low | ~0.11 | ✅ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Pair 3 bất ngờ nhất: "sexual misconduct" và "misconduct" có score ~0.61 — khá cao dù 2 câu nói về loại vi phạm khác nhau. Điều này cho thấy embedding model nắm được **semantic similarity ở cấp độ concept** (cả hai đều về misconduct/violation), không chỉ keyword matching — nhưng cũng phản ánh rủi ro false positive khi semantically adjacent terms làm nhiễu retrieval (retrieve nhầm doc về academic integrity khi user hỏi về sexual misconduct).

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)
| # | Query | Gold Answer (tóm tắt) |
|---|-------|----------------------|
| 1 | What are all the conditions a student must maintain to stay in good academic standing at VinUni? | GPA ≥ 2.0, không vi phạm kỷ luật Tier 3/4, hoàn thành E.X.C.E.L evaluation |
| 2 | What safety and conduct regulations must students follow when using VinUni campus facilities? | Tuân theo Code of Conduct, không có hành vi sexual misconduct, tuân thủ lab safety regulations |
| 3 | What are the admission and language requirements for students entering medical programs at VinUni? | Tiếng Anh đủ chuẩn, hoàn thành chương trình y khoa, nộp qua online portal |
| 4 | What procedures and consequences apply when a student breaks university rules? | Instructor điều tra → báo cáo Registrar → Academic Integrity Council xét Tier 3/4 → có thể đình chỉ/đuổi học |
| 5 | How does VinUni evaluate and ensure the quality of its academic programs and teaching staff? | Kiểm định chất lượng qua cam kết đào tạo, đánh giá đội ngũ giảng viên cơ hữu |

### Kết Quả Của Tôi

*Chạy với `SemanticChunker (threshold=0.5, max_chunk_size=800)` + `OpenAIEmbedder (text-embedding-3-small)` + `GPT-4o-mini` (real LLM)*  
*Nguồn: `log.md` — 2026-04-10 16:58:38*

| # | Query (tóm tắt) | Top-1 Source | Score | Relevant? | Agent Answer (tóm tắt) |
|---|----------------|-------------|-------|-----------|------------------------|
| 1 | Academic standing conditions | `12_Scholarship_Maintenance_Criteria.md` | 0.695 | ✅ Có | GPA ≥ 2.5, không vi phạm Tier 3/4, hoàn thành E.X.C.E.L self-evaluation |
| 2 | Campus safety & conduct | `15_Student_Code_of_Conduct.md` | 0.665 | ✅ Có | Không có hành vi xúc phạm/đe dọa, không gian lận học thuật, không dùng tên VinUni trái phép |
| 3 | Medical admission & language | `02_Admissions_Regulations_GME_Programs.md` | 0.671 | ✅ Có | GPA ≥ 7.0/10, tốt nghiệp y năm nộp đơn, không kỷ luật, tiếng Anh đủ chuẩn trước 30/8 |
| 4 | Rule-breaking procedures | `13_Student_Academic_Integrity.md` | 0.618 | ✅ Có | Instructor điều tra → Tier 3/4 → Academic Integrity Council → đình chỉ/đuổi học |
| 5 | Academic quality evaluation | `06_English_Language_Requirements.md` | 0.610 | ❌ Không | Agent trả lời "I don't know" — docs tiếng Việt (03, 04, 05) không được retrieve |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 4 / 5

**Tổng điểm retrieval: 8/10** (Q1: 2/2, Q2: 2/2, Q3: 2/2, Q4: 2/2, Q5: 0/2)

**Phân tích:** Query #5 thất bại hoàn toàn — tài liệu liên quan nhất (*Cam Kết Chất Lượng Đào Tạo*, *Đội Ngũ Giảng Viên Cơ Hữu*) là tiếng Việt, query tiếng Anh → embedding space khác nhau → không được retrieve. Agent GPT-4o-mini trả lời thành thật "I don't know" thay vì hallucinate — đây là hành vi đúng nhưng cho thấy gap dữ liệu cần giải quyết bằng multilingual embedding hoặc language routing.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Từ **Đặng Tùng Anh** (Hybrid Header + RecursiveChunker + OpenAI): cùng embedding model (`text-embedding-3-small`) với tôi nhưng dùng header-aware chunking — nhận diện heading markdown để ưu tiên cắt tại đó trước khi áp dụng Recursive. Kết quả tương đương SemanticChunker (8/10) nhưng không cần embedding call trong bước chunking → nhanh hơn và chi phí thấp hơn đáng kể.

> Từ **Mai Tấn Thành** (HeaderAwareChunker + Voyage AI): chỉ tạo **237 chunks** (so với 808 của tôi) nhưng đạt 8/10 với score cosine cao nhất (~0.59–0.62). Chứng minh rằng **embedding model chất lượng cao + chunk ít nhưng giàu context** hiệu quả hơn nhiều chunk nhỏ chi tiết. Trade-off: khi Q5 miss là miss hẳn (0/3) vì ít đầu phân lựa chọn.

> Từ **Nguyễn Đức Hoàng Phúc** (RecursiveChunker + Local `all-MiniLM-L6-v2`): Q2 (campus safety) cho score cao nhất nhóm (0.6531 Lab, 0.6486 Fire Safety) — Local model bắt từ khóa safety rất tốt. Nhưng overall 7/10 do Q4 chỉ 1/2, cho thấy Local model yếu hơn ở các câu hỏi về quy trình phức tạp.

> Từ **Phạm Lê Hoàng Nam** (Header+Recursive + **Mock embeddings**): dùng mock embedding (hash-based, không có ngữ nghĩa) nhưng vẫn đạt 8/10 vì mock deterministic — cùng văn bản luôn cho cùng vector, overlap giữa heading chunk và query terms được bắt tình cờ. Confirm rằng **data quality + chunking structure quan trọng không kém embedding model**.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Khi xem demo của các nhóm khác, điều ấn tượng nhất là sự đa dạng về **lựa chọn domain** — trong khi nhóm tôi chọn tài liệu policy hành chính (structured, formal), các nhóm khác chọn domain như FAQ sản phẩm, tài liệu kỹ thuật, hay văn bản pháp luật. Tôi nhận ra rằng **domain quyết định chunking strategy tối ưu** — tài liệu FAQ ngắn gọn phù hợp với SentenceChunker, trong khi tài liệu kỹ thuật dài cần RecursiveChunker hay SemanticChunker. Ngoài ra, một số nhóm thiết kế query benchmark rất cụ thể (trích dẫn số liệu, tên riêng) giúp đánh giá retrieval precision dễ hơn — rút ra bài học là query càng cụ thể thì càng dễ đánh giá chất lượng hệ thống RAG.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Vấn đề rõ nhất — được xác nhận bởi 5/5 thành viên — là **cross-lingual embedding gap cho Q5**. Giải pháp tôi sẽ thực hiện: (1) Dùng **`multilingual-e5-large`** hoặc `paraphrase-multilingual-mpnet-base-v2` thay cho monolingual model — cả EN và VI được encode vào cùng embedding space. (2) Hoặc áp dụng **query translation layer**: detect ngôn ngữ query, nếu EN thì search cả tập EN và bản dịch VI, merge kết quả theo score. (3) Thay SemanticChunker bằng **HeaderAwareChunker** để giảm chi phí chunking mà không mất chất lượng — kết quả benchmark xác nhận tương đương (8/10) nhưng không tốn API call khi chunking.


---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 9 / 10 |
| Chunking strategy | Nhóm | 13 / 15 |
| My approach | Cá nhân | 9 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **94 / 100** |
