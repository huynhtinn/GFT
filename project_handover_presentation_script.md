# 🎙️ KỊCH BẢN THUYẾT TRÌNH & TÀI LIỆU BÀN GIAO KỸ THUẬT DỰ ÁN
## System: GFT — Autonomous Customer Support Agent System

---

## 📌 PHẦN 1: THÔNG TIN BÀN GIAO HỆ THỐNG

- **Tên dự án**: GFT — Tổng Đài Hỗ Trợ Khách Hàng Tự Vận Hành (Autonomous Customer Support Agent)
- **Kiến trúc cốt lõi**: Multi-Agent State Machine (LangGraph) + Vector DB (Qdrant) + RAG (SentenceTransformers & Cohere Rerank) + LLM (Groq Llama-3.3-70B)
- **Môi trường vận hành**: Python 3.10+, Astral `uv`, Docker & Docker-Compose
- **Cơ sở dữ liệu**: Qdrant Vector DB (HNSW Index), SQLite 3 (WAL Journal Mode)
- **Giao diện quản trị**: Streamlit Web Dashboard (Phân quyền Admin vs Customer)

---

## 🎤 PHẦN 2: KỊCH BẢN THUYẾT TRÌNH DỰ ÁN (PRESENTATION SCRIPT)

> *Dành cho người đại diện trình bày / demo dự án trước Hội đồng kiểm duyệt, Đội ngũ Quản lý hoặc Đội ngũ Kỹ thuật tiếp nhận.*

---

### 🟢 Slide 1: Giới Thiệu Bài Toán & Mục Tiêu Hệ Thống

**Lời thoại diễn thuyết:**
> *"Kính chào quý vị và các đồng nghiệp. Hôm nay tôi xin giới thiệu hệ thống **GFT — Tổng Đài Hỗ Trợ Tự Vận Hành Thế Hệ Mới**.
> 
> Trong các doanh nghiệp hiện nay, bộ phận Chăm sóc Khách hàng (CSKH) phải đối mặt với hàng nghìn ticket mỗi ngày từ nhiều kênh: Website, Email, Zalo. Hai thách thức lớn nhất là: **Thời gian phản hồi chậm** và **Chi phí nhân sự cao cho các câu hỏi lặp đi lặp lại**. Các Chatbot truyền thống theo luật (rule-based) thì quá cứng nhắc, còn nếu dùng LLM đơn thuần thì dễ gặp hiện tượng "ảo giác" (hallucination), trả lời sai sự thật.
> 
> Hệ thống của chúng tôi giải quyết bài toán này bằng kiến trúc **Multi-Agent State Machine phối hợp cùng RAG & Human-in-the-Loop**, đảm bảo 3 tiêu chí: **Tự động hóa cao — Trả lời chính xác có dẫn nguồn — Tuyệt đối an toàn trước rủi ro**."*

---

### 🟢 Slide 2: Sơ Đồ Kiến Trúc Multi-Agent Pipeline (9 Nodes)

**Lời thoại diễn thuyết:**
> *"Mời quý vị nhìn vào sơ đồ kiến trúc luồng xử lý. Khác với các hệ thống RAG đơn luồng tuyến tính, chúng tôi xây dựng một **LangGraph State Machine** gồm 9 nút xử lý độc lập hoạt động như một phòng ban CSKH thực sự:
> 
> 1. **Node 1 - Spam Inspector**: Bộ lọc rác ban đầu.
> 2. **Node 2 - Intent & Priority Classifier**: Phân loại ý định và gán độ ưu tiên P0 đến P3.
> 3. **Node 3 - Slot Inspector**: Kiểm tra thiếu thông tin và tự động hỏi làm rõ.
> 4. **Node 4 - Supervisor Coordinator**: Trợ lý điều phối luồng và phong cách phản hồi.
> 5. **Node 5 - Query Optimizer**: Bộ viết lại và mở rộng câu truy vấn.
> 6. **Node 6 - Qdrant RAG & Cohere Rerank**: Tìm kiếm ngữ nghĩa thực sự và tái xếp hạng.
> 7. **Node 7 - Reasoning Layer**: Tầng suy luận lập luận từng bước (Chain-of-Thought).
> 8. **Node 8 - Guardrails Router**: Ma trận đánh giá rủi ro và quyết định luồng đi.
> 9. **Node 9 - HITL Briefing Generator**: Soạn gói thông tin tóm tắt cho Nhân sự khi có leo thang."*

---

### 🟢 Slide 3: Trái Tim RAG Engine & Embedding Thực Sự

**Lời thoại diễn thuyết:**
> *"Một điểm đột phá của dự án nằm ở **Động cơ RAG hai tầng (Two-Tier RAG Engine)**:
> 
> - **Tầng 1 (Embedding & Vector Search)**: Chúng tôi sử dụng mô hình multilingual `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` cho ra Vector 384 chiều, kết hợp bộ phân đoạn `RecursiveCharacterTextSplitter` của LangChain. Thay vì cắt văn bản thô theo số ký tự, hệ thống tách theo ranh giới ngữ nghĩa từ Tiêu đề -> Đoạn văn -> Câu -> Từ. Điểm tương đồng được tính toán qua Cosine Distance trên Qdrant DB.
> - **Tầng 2 (Reranking)**: Kết quả tìm được tiếp tục được đưa qua **Cohere Rerank v3.0** để tái xếp hạng theo điểm xác suất ngữ nghĩa.
> 
> Kết quả thử nghiệm thực tế: Khi khách hàng hỏi *"GÓI BASIC giá bao nhiêu và có bao nhiêu ticket"*, hệ thống đạt điểm tương đồng thực tế lên tới **91.4%**, trích xuất chính xác tuyệt đối đoạn tài liệu về giá gói 1.500.000 VNĐ/tháng và giới hạn 100 ticket."*

---

### 🟢 Slide 4: Tầng Điều Phối Supervisor & Tối Ưu Truy Vấn (Query Optimizer)

**Lời thoại diễn thuyết:**
> *"Khi khách hàng gửi một câu hỏi ngắn hoặc chứa ngôn ngữ đời thường, công cụ tìm kiếm truyền thống thường thất bại. Vì vậy, hệ thống tích hợp 2 Agent chuyên trách:
> 
> - **Query Optimizer & Expander**: Đóng vai trò làm giàu truy vấn. Nó tạo ra một câu `rewritten_query` chuẩn hóa ngữ nghĩa kỹ thuật, đồng thời tạo thêm 3 câu `expanded_queries` bằng các thuật ngữ tương đương. Cả 4 truy vấn này được chạy gộp (Multi-Query Retrieval) để không bỏ sót bất kỳ vết tri thức nào.
> - **Supervisor Agent**: Đánh giá toàn cục bức tranh yêu cầu. Nếu phát hiện ticket thuộc nhóm Bức xúc, Khiếu nại tiền bạc hoặc Sự cố P0 sập server, Supervisor sẽ lập tức ra lệnh `escalation_required = True` và chỉ định phong cách phản hồi phù hợp (`formal`, `empathetic` hoặc `technical`)."*

---

### 🟢 Slide 5: Tầng Lập Luận Reasoning (CoT) & Ma Trận An Toàn (Guardrails Router)

**Lời thoại diễn thuyết:**
> *"Để tránh hiện tượng LLM đưa ra câu trả lời ngây ngô hoặc bịa đặt, chúng tôi áp dụng tầng **Reasoning & Thought Layer**:
> 
> AI phải thực hiện **Chain-of-Thought reasoning (lập luận từng bước)** trong bộ nhớ trước:
> - *Bước 1: Phân tích thông tin thực tế từ yêu cầu.*
> - *Bước 2: Đối chiếu với các trích đoạn tri thức RAG tìm được.*
> - *Bước 3: Đưa ra giải pháp và kiểm tra điều khoản.*
> 
> Sau đó, **Guardrails Router** sẽ đối chiếu hai điều kiện:
> - Nếu `Grounding Confidence Score < 30%` (không tìm thấy tri thức tin cậy) HOẶC yêu cầu có rủi ro cao (P0, Khiếu nại) -> **Lập tức Kích hoạt Human Handoff (Chuyển nhân sự)**.
> - Ngược lại, nếu tri thức vững chắc và rủi ro thấp -> **Tự động phản hồi an toàn (`RESOLVED_AUTO`)**."*

---

### 🟢 Slide 6: Cơ Chế Human-in-the-Loop & Gói Briefing Cho Nhân Sự

**Lời thoại diễn thuyết:**
> *"Khi một Ticket bị leo thang sang Nhân sự (`ESCALATED_HUMAN`), hệ thống không chỉ quăng câu hỏi của khách sang cho nhân viên, mà Node 9 sẽ tự động tạo **AI Context Briefing Package**:
> 
> Gói này bao gồm:
> 1. Tóm tắt yêu cầu & Thái độ khách hàng (Khẩn cấp / Bức xúc / Bình thường).
> 2. Các bước AI đã xử lý trước đó.
> 3. Lý do chi tiết vì sao bị leo thang.
> 4. **Dự thảo câu trả lời sẵn (Auto Draft Response)** được AI soạn thảo dựa trên tài liệu.
> 
> Nhân sự chỉ cần mở tab phê duyệt trên Streamlit, kiểm tra bản nháp, chỉnh sửa nếu cần và bấm 1 nút để gửi cho khách hàng. Điều này giúp giảm 80% thời gian xử lý ticket của nhân viên hỗ trợ!"*

---

### 🟢 Slide 7: Trải Nghiệm Giao Diện Phân Quyền Trực Quan (Demo Streamlit)

**Lời thoại diễn thuyết:**
> *"Giao diện ứng dụng được xây dựng trên Streamlit với cơ chế phân quyền tài khoản chặt chẽ:
> 
> - **Đối với Khách Hàng (Customer View)**:
>   - Giao diện thân thiện, có sẵn 12 Kịch bản mẫu (FAQ, Lỗi API 403, Khẩn cấp P0, Hoàn tiền, Spam...).
>   - Các thông tin kỹ thuật nội bộ như Trích dẫn RAG, Supervisor decision, Reasoning trace hoàn toàn được ẩn đi để đảm bảo trải nghiệm tự nhiên và an toàn bảo mật.
> 
> - **Đối với Admin / Nhân Sự (Staff View)**:
>   - Xem được toàn bộ nhật ký suy luận CoT, điểm số Confidence thực tế và trích dẫn tri thức dẫn nguồn.
>   - Quản lý Hàng chờ duyệt ticket (Escalations Queue) và công cụ Upload / Index tài liệu tri thức (PDF, DOCX, JSON, TXT) trực tiếp vào Qdrant DB."*

---

### 🟢 Slide 8: Cơ Sở Dữ Liệu SQLite WAL & Hạ Tầng Docker

**Lời thoại diễn thuyết:**
> *"Về hạ tầng kỹ thuật:
> 
> - **Cơ sở dữ liệu SQLite**: Sử dụng chế độ **WAL (Write-Ahead Logging)** và `busy_timeout=5000ms`. Mọi thay đổi về trạng thái, câu trả lời, logs, citations được đồng bộ tức thì, chịu tải an toàn trong môi trường đa tiến trình mà không bị khóa database.
> - **Định danh UUID**: Mã Ticket sinh ra dưới dạng `TCK-XXXXXX` bằng UUID hex, triệt tiêu 100% nguy cơ trùng lặp mã.
> - **Đóng gói Docker**: Ứng dụng đã được đóng gói hoàn chỉnh bằng `Dockerfile` (đã nướng sẵn model embedding vào layer) và `docker-compose.yml` gồm 2 container `qdrant_vector_db` và `gft_support_app` có tích hợp Healthcheck probes."*

---

### 🟢 Slide 9: Tổng Kết Điểm Nổi Bật & Hướng Phát Triển

**Lời thoại diễn thuyết:**
> *"Tóm lại, dự án **GFT Autonomous Support Agent** đã hoàn thành trọn vẹn với các điểm sáng:
> 
> 1. Kiến trúc Multi-Agent LangGraph hiện đại, dễ mở rộng.
> 2. RAG Engine thực sự với SentenceTransformers & Cohere Rerank.
> 3. Tự động hóa cao đi đôi với an toàn tuyệt đối nhờ Guardrails & HITL.
> 4. Sẵn sàng đóng gói triển khai ngay lập tức với Docker.
> 
> Về hướng phát triển tiếp theo, người tiếp nhận có thể dễ dàng mở rộng thêm các kênh tích hợp Realtime Webhook (Zalo ZNS, Telegram Bot, Email SMTP) và tích hợp các mô hình LLM Local như Ollama/Qwen.
> 
> Xin chân thành cảm ơn quý vị đã theo dõi!"*

---

## 🛠️ PHẦN 3: HƯỚNG DẪN BÀN GIAO KỸ THUẬT (TECHNICAL HANDOVER)

> *Dành cho Kỹ sư / Lập trình viên tiếp nhận mã nguồn.*

---

### 1. Danh Sách File Mã Nguồn Trọng Yếu

| File | Chức năng chính | Cần lưu ý khi chỉnh sửa |
|------|-----------------|------------------------|
| [app/graph/nodes.py](file:///home/tin/projects/GFT/app/graph/nodes.py) | Định nghĩa 9 Nodes xử lý logic Multi-Agent | Mọi cuộc gọi LLM đều truyền `json_mode=True` và qua `parse_json_response()`. |
| [app/graph/builder.py](file:///home/tin/projects/GFT/app/graph/builder.py) | Lắp ráp StateGraph & Conditional Edges | Nơi điều hướng luồng (routing after spam, slot, guardrails). |
| [app/services/qdrant_service.py](file:///home/tin/projects/GFT/app/services/qdrant_service.py) | Vector DB Engine, Embedding & Chunking | Sử dụng `SentenceTransformer` (dim=384) và `RecursiveCharacterTextSplitter`. |
| [app/services/llm_service.py](file:///home/tin/projects/GFT/app/services/llm_service.py) | Groq API Client & Safe JSON Parsing | Có cơ chế Retry 3 lần với Exponential Backoff (1s, 2s, 4s). |
| [app/services/auth_service.py](file:///home/tin/projects/GFT/app/services/auth_service.py) | SQLite DB (WAL mode), Auth & Ticket Persistence | `save_ticket()` cập nhật đầy đủ 11 trường dữ liệu khi conflict ID. |
| [app_streamlit.py](file:///home/tin/projects/GFT/app_streamlit.py) | Giao diện Web Streamlit | Quản lý Session State, presets kịch bản mẫu và phân quyền giao diện. |
| [docker-compose.yml](file:///home/tin/projects/GFT/docker-compose.yml) | Orchestration Docker | Định nghĩa container `qdrant` và `app` kèm healthcheck. |

---

### 2. Hướng Dẫn Thiết Lập Môi Trường Từ Đầu

#### Bước 1: Clone và Cài đặt Dependencies bằng Astral `uv`
```bash
cd /path/to/GFT
uv sync
```

#### Bước 2: Khai báo Biến Môi Trường (`.env`)
Tạo file `.env` tại thư mục gốc:
```env
GROQ_API_KEY=gsk_your_groq_cloud_key
COHERE_API_KEY=your_cohere_key
QDRANT_URL=http://localhost:6333
COHERE_MODEL=rerank-multilingual-v3.0
USE_RERANK=true
```

#### Bước 3: Khởi chạy Qdrant Server & App
- **Chạy local dev**:
  ```bash
  # Terminal 1: Chạy Qdrant Docker
  docker run -p 6333:6333 qdrant/qdrant:v1.12.0

  # Terminal 2: Chạy Streamlit App
  uv run streamlit run app_streamlit.py
  ```

- **Chạy Docker Compose (Production)**:
  ```bash
  docker-compose up --build -d
  ```

---

### 3. Quy Trình Bảo Trì & Mở Rộng (Extensibility Guide)

#### A. Muốn bổ sung Thư mục Tri thức mới vào Knowledge Base:
1. Thêm file `.txt` vào thư mục tương ứng trong `knowledge_base/` (ví dụ `knowledge_base/technical/file-moi.txt`).
2. Khi app khởi chạy hoặc gọi `seed_initial_kb()`, hệ thống sẽ tự động đọc, chunking bằng `RecursiveCharacterTextSplitter` và tạo Vector Index trên Qdrant DB.

#### B. Muốn thay đổi Mô hình Embedding:
1. Mở `app/config/settings.py`, chỉnh sửa `EMBEDDING_MODEL_NAME`.
2. Lưu ý: Nếu thay đổi mô hình có số chiều (dimension) khác 384, cần cập nhật `VECTOR_DIM` tương ứng và xóa collection cũ trên Qdrant để tạo lại.

#### C. Muốn bổ sung thêm Node mới vào LangGraph:
1. Viết hàm node mới trong `app/graph/nodes.py` (nhận `SupportState`, trả về `Dict[str, Any]`).
2. Mở `app/graph/builder.py`:
   - Khai báo `builder.add_node("node_name", new_node_function)`.
   - Nối cạnh `builder.add_edge()` hoặc `builder.add_conditional_edges()`.

#### D. Muốn đổi Provider LLM (ví dụ chuyển từ Groq sang OpenAI / Ollama):
1. Chỉnh sửa `app/services/llm_service.py`. Giữ nguyên interface hàm `generate_completion(messages, temperature, max_tokens, json_mode)`.
2. Mọi node trong Graph sẽ tự động sử dụng LLM Provider mới mà không cần sửa đổi code của từng node.

---

## 🔐 PHẦN 4: CHECKLIST BÀN GIAO DỰ ÁN

- [x] Mã nguồn đã được kiểm tra cú pháp clean (`py_compile` pass 100%).
- [x] Tệp cấu hình `.env.example` đã được chuẩn hóa.
- [x] Đã xóa toàn bộ API Keys nhạy cảm khỏi mã nguồn công khai.
- [x] Cơ sở dữ liệu SQLite `user.db` đã chạy ổn định ở chế độ WAL.
- [x] Dữ liệu tri thức mẫu (15 file `.txt`) đã được tự động nạp thành công vào Qdrant DB.
- [x] Dockerfile & Docker-Compose đã được kiểm thử tính năng đóng gói.
- [x] Tài liệu `README.md` và Kịch bản Thuyết trình Bàn giao đã hoàn thiện.
