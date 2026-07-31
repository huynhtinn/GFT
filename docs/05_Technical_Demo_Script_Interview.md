# 🚀 TECH DEMO SCRIPT: AUTONOMOUS MULTI-AGENT & ADVANCED RAG ARCHITECTURE
> **Định dạng**: Technical Interview & Engineering Review Demo
> **Đối tượng lắng nghe**: Tech Lead, Senior AI/Software Engineers, Engineering Manager
> **Mục tiêu**: Thể hiện tư duy kiến trúc hệ thống (System Design), kỹ thuật AI/RAG nâng cao (Advanced RAG & Vector Engine), giải pháp Guardrails & HITL cấp Doanh nghiệp, cùng khả năng giải quyết các bài toán kỹ thuật phức tạp (Trade-offs, Concurrency, Calibration).

---

## ⏱️ CẤU TRÚC PHÂN ĐOẠN TECHNICAL DEMO (Dự kiến: 6 - 8 Phút)

| Phân đoạn | Chủ đề Kỹ thuật Trọng tâm | Thời lượng |
|-----------|---------------------------|------------|
| **Part 1** | **System Architecture & State Machine Design** (LangGraph vs Chain/DAG, Cyclic Loops) | ~1.5 phút |
| **Part 2** | **Deep Dive: Advanced Vector RAG Engine** (HNSW, MiniLM Embedding, Cohere Rerank v3, Chunking) | ~2.0 phút |
| **Part 3** | **Production Guardrails & Mathematical Calibration** (Confidence Score Mapping, Financial Safety) | ~1.5 phút |
| **Part 4** | **Enterprise HITL Architecture & Data Engine** (Context Briefing, SQLite WAL Concurrency) | ~1.5 phút |
| **Part 5** | **Engineering Trade-offs & Scalability Roadmap** (Latency, Token Cost, Horizontal Scaling) | ~1.0 phút |

---

## 🎯 CHI TIẾT TỪNG PHÂN ĐOẠN TECHNICAL DEMO

---

### 🏛️ PART 1: SYSTEM ARCHITECTURE & STATE MACHINE DESIGN (~1.5 PHÚT)

#### 🖥️ Thao tác trên Streamlit UI:
1. Mở trang chủ ứng dụng ([http://localhost:8501](http://localhost:8501)).
2. Đăng nhập tài khoản **Khách hàng** (`customer` / `123`).
3. Mở Sidebar, điểm qua giao diện và sẵn sàng tại tab **`Tiếp Nhận Ticket`**.

#### 🎙️ Kịch bản Lời thoại Chuyên môn (Dễ hiểu & Thuyết phục):
> *"Em chào Anh/Chị trong Hội đồng Kỹ thuật! Hôm nay em xin trình bày về kiến trúc của **Autonomous Customer Support Agent System** — hệ thống tổng đài hỗ trợ tự động hóa dựa trên **LangGraph State Machine** và **Advanced RAG Architecture**.*
> 
> *Đầu tiên, về mặt **Thiết kế Kiến trúc (System Design)**: Tại sao em lại chọn **LangGraph State Machine** thay vì viết một chuỗi lệnh chạy thẳng từ trên xuống dưới?*
> 
> *Trong thực tế chăm sóc khách hàng, **luồng xử lý không bao giờ đi theo đường thẳng**:*
> - *Nếu gặp tin rác hay quảng cáo lừa đảo ➔ Hệ thống phải tự ngắt và đóng ticket ngay (`SPAM_CLOSED`).*
> - *Nếu khách hàng báo lỗi mà đưa thiếu thông tin (ví dụ: báo lỗi API nhưng quên gửi API Key) ➔ AI phải **quay ngược lại đặt câu hỏi làm rõ** cho đến khi đủ dữ liệu mới đi tiếp (`CLARIFICATION_SENT` - Vòng lặp Cyclic Loop).*
> - *Nếu gặp ca nhạy cảm như đòi hoàn tiền hay khiếu nại ➔ AI phải **tạm dừng lại**, chuyển thông tin cho nhân sự duyệt rồi mới xử lý tiếp (`ESCALATED_HUMAN`).*
> 
> *Để làm được điều đó, em cần một kiến trúc **"Có bộ nhớ trạng thái" (Stateful Architecture)**:*
> - *Mỗi Ticket khi đi qua hệ thống được đóng gói thành một đối tượng trạng thái chung (`State`).*
> - **LangGraph Checkpointer** đóng vai trò như một **"nút Bookmark tạm dừng & khôi phục"**: khi cần con người can thiệp (Human-in-the-Loop), hệ thống sẽ lưu lại chính xác trạng thái hiện tại. Sau khi nhân sự duyệt xong, luồng sẽ chạy tiếp từ đúng điểm dừng đó mà không phải chạy lại từ đầu.*
> 
> *Toàn bộ quy trình này được em chia nhỏ thành **9 Node Agent chuyên biệt**: từ Spam Inspector, Phân loại Intent, Kiểm tra Slot thiếu, Supervisor điều phối, Tối ưu câu hỏi, RAG Vector Engine, Suy luận CoT, Guardrails Router cho đến AI Briefing Generator.*"

---

### 🔍 PART 2: DEEP DIVE: ADVANCED VECTOR RAG ENGINE (~2.0 PHÚT)

#### 🖥️ Thao tác trên Streamlit UI:
1. Tại tab **`Tiếp Nhận Ticket`**, bấm chọn nút Kịch bản mẫu: **`FAQ Giá Cước`**.
2. Thấy câu hỏi dài về startup 90 ticket/tháng, bấm nút màu đỏ **`Gửi Yêu Cầu & Thực Thi`**.
3. Khi kết quả trả về, cuộn tới khu vực **`🧭 Bộ Điều Phối & Tối Ưu Truy Vấn`** và **`📚 Trích Dẫn Tri Thức Dẫn Nguồn`**.
4. Chỉ con trỏ chuột vào **`Rewritten Query`**, **`Expanded Queries`** và điểm số tương đồng `91.4%`.

#### 🎙️ Kịch bản Lời thoại Chuyên môn (Technical Script):
> *"Tiếp theo, em xin đi sâu vào **RAG Engine Pipeline** — nơi em đã giải quyết bài toán Semantic Search cho văn bản tiếng Việt phức tạp.*
> 
> *Một lỗi phổ biến của các hệ thống RAG cơ bản là dùng Naive Character Chunking và Vector Search đơn tầng. Trong dự án này, em triển khai **4 kỹ thuật Advanced RAG**:*
> 
> 1. **Semantic Hierarchy Chunking**: Em sử dụng `RecursiveCharacterTextSplitter` với cây phân cách ưu nghĩa `["\n===", "\n---", "\n\n", "\n", "."]`, đặt `chunk_size = 800` và `chunk_overlap = 150` (~20%). Điều này đảm bảo các đoạn tài liệu không bị ngắt ngang giữa câu, giữ trọn vẹn ngữ nghĩa liên tục.*
> 
> 2. **Real Dense Vector Embedding**: Thay vì các hàm Hash thô sơ hay API đắt đỏ, em tích hợp mô hình **`SentenceTransformers (paraphrase-multilingual-MiniLM-L12-v2)`** chạy local. Model này tạo ra Vector 384 chiều đã được L2 Normalized, tối ưu cho 50+ ngôn ngữ bao gồm Tiếng Việt.*
> 
> 3. **Deterministic Hash Point Indexing**: Để tránh lỗi trùng lặp Point trong Qdrant do `hash()` ngẫu nhiên của Python giữa các lần restart server, em xây dựng hàm sinh Point ID bằng **`hashlib.sha256(f"{doc_id}_chunk_{idx}")`**, đảm bảo tính **Idempotent** tuyệt đối khi re-upsert.*
> 
> 4. **Multi-Query Expansion & Cohere Cross-Encoder Reranking**: 
>    * Khi người dùng nhập một câu hỏi dài tự nhiên, node **Query Optimizer** sử dụng LLM để sinh ra `rewritten_query` và 3 `expanded_queries` chứa thuật ngữ tương đương.
>    * Em thực hiện **Multi-Query Retrieval** song song trên Qdrant DB (HNSW Indexing với Cosine Distance).
>    * Sau khi gộp và De-duplicate danh sách ứng viên, em đưa qua **`Cohere Rerank v3 API (rerank-multilingual-v3.0)`** — một mô hình Cross-Encoder chuyên dụng để tính lại trọng số tương quan sâu trước khi lấy Top-K.*"

---

### 🛡️ PART 3: PRODUCTION GUARDRAILS & MATHEMATICAL CALIBRATION (~1.5 PHÚT)

#### 🖥️ Thao tác trên Streamlit UI:
1. Tiếp tục tại tab **`Tiếp Nhận Ticket`**, bấm chọn Kịch bản mẫu: **`Đòi Hoàn Tiền 2 Lần`**.
2. Thấy nội dung bức xúc bị trừ tiền 2 lần trên hóa đơn tháng 7, bấm nút màu đỏ **`Gửi Yêu Cầu & Thực Thi`**.
3. Chỉ vào Badge màu đỏ **`ESCALATED_HUMAN (Chuyển Nhân sự)`**, ô **`Confidence Score: 91.3%`**, và phần lập luận của **`Supervisor Agent decisions`**.

#### 🎙️ Kịch bản Lời thoại Chuyên môn (Technical Script):
> *"Bây giờ, em xin trình bày về bài toán **Enterprise Guardrails & Safety** — Tính năng quan trọng nhất để đưa AI Agent vào Production.*
> 
> *Anh/Chị hãy quan sát ví dụ này: Khách hàng báo bị trừ tiền 2 lần và đòi hoàn tiền gấp.*
> *Ở đây có một hiện tượng rất thú vị:*
> - **Confidence Score của RAG đạt rất cao: 91.3%** (AI tìm được chính xác 100% tài liệu quy định hoàn tiền trong Vector DB).
> - **NHƯNG Trạng thái hệ thống vẫn ra `ESCALATED_HUMAN`!**
> 
> *Tại sao lại có sự tách biệt này?*
> 
> 1. **Mathematical Confidence Calibration**: Điểm Cosine Similarity của các model Multilingual Embedding cho câu hỏi dài thường nằm trong khoảng `0.12 - 0.45`. Nếu nhân 100 thô sơ, điểm sẽ bị lệch về 15-20%. Em đã xây dựng một **Hàm quy đổi piecewise calibration (Chuẩn hóa từng khoảng toán học)** để đưa điểm số về đúng thang phần trăm trung thực từ 0% đến 99%.*
> 
> 2. **Two-Tier Guardrails Decision Matrix**: Tại node **Guardrails Router**, hệ thống đánh giá ma trận 2 lớp:
>    - **Lớp 1 (Grounding Check)**: `confidence_score < RAG_CONFIDENCE_THRESHOLD` (Mặc định 45.0%).
>    - **Lớp 2 (Business Risk Check)**: `priority == P0_CRITICAL`, `category in [complaint, urgent]`, hoặc `supervisor_decision.escalation_required == True`.
> 
> *Dù RAG Confidence đạt 91.3%, nhưng vì đây là ca tranh chấp tài chính (`BILLING / P1_HIGH`), **Supervisor Agent** đã đánh giá rủi ro cao và đặt `escalation_required = True`. Theo chính sách an toàn doanh nghiệp, AI không bao giờ được tự động chuyển tiền hoàn cho khách mà bắt buộc phải qua sự phê duyệt của Con người!*"

---

### 👨‍💻 PART 4: ENTERPRISE HITL ARCHITECTURE & DATA ENGINE (~1.5 PHÚT)

#### 🖥️ Thao tác trên Streamlit UI:
1. Đăng xuất tài khoản khách hàng, đăng nhập tài khoản Admin (`admin` / `123`).
2. Chọn trang **`Giao Diện Nhân Sự`** trên Sidebar.
3. Trong Escalations Queue, chọn Ticket `[TCK-1812]` (Ticket bị trừ tiền 2 lần).
4. Chỉ vào 2 khu vực chính:
   * **`AI Context Briefing Package`**: Tóm tắt 1 câu, Thái độ `Bức xúc`, Các bước AI đã thử, Hành động đề xuất.
   * **`Phê Duyệt & Chỉnh Sửa Câu Trả Lời`**: Bản nháp câu trả lời đã điền sẵn tên khách hàng và nhân sự.
5. Bấm nút màu xanh **`Phê Duyệt & Gửi Phản Hồi Cho Khách Hàng`**.

#### 🎙️ Kịch bản Lời thoại Chuyên môn (Technical Script):
> *"Tiếp theo là thiết kế **Human-in-the-Loop (HITL) Workflow** ở trang Workspace Nhân Sự.*
> 
> *Thay vì bắt nhân viên hỗ trợ đọc lại toàn bộ thread chat dài hay tự soạn câu trả lời từ đầu, node **HITL Briefing Generator** đóng gói sẵn một **`ContextPackage`**:*
> - *Tóm tắt sự cố chỉ trong 1 câu.*
> - *Phân tích sentiment thái độ khách hàng (`Khẩn cấp/Bức xúc`).*
> - *Liệt kê Audit Log các bước AI đã chuẩn bị trước.*
> - *Tự động soạn sẵn bản nháp phản hồi chuyên nghiệp.*
> 
> *Nhân viên hỗ trợ chỉ cần thẩm định giao dịch thực tế trên ERP/Core Banking, chỉnh sửa câu từ nếu cần và bấm **`Phê Duyệt`**.*
> 
> *Về mặt **Database Engine & Persistence**:*
> - *Dữ liệu ticket được đồng bộ lưu trữ vào SQLite DB (`user.db`).*
> - *Để giải quyết vấn đề **`database is locked`** khi nhiều user đồng thời thao tác trên Streamlit multi-threading, em đã kích hoạt **SQLite WAL Mode (`PRAGMA journal_mode=WAL;`)** kết hợp `busy_timeout=5000` và `timeout=10.0`.*
> - *Mọi câu lệnh ghi dữ liệu đều sử dụng `ON CONFLICT(id) DO UPDATE SET` cho toàn bộ 16 trường thuộc tính, đảm bảo dữ liệu giữa In-memory Session State và SQLite luôn khớp nhau 100%.*"

---

### 📊 PART 5: ENGINEERING TRADE-OFFS & SCALABILITY ROADMAP (~1.0 PHÚT)

#### 🖥️ Thao tác trên Streamlit UI:
1. Chuyển sang tab **`Tra Cứu Tri Thức`** trên Sidebar.
2. Cho xem nhanh giao diện Vectorize & Index tài liệu mới vào Qdrant DB.

#### 🎙️ Kịch bản Lời thoại Chuyên môn (Technical Script):
> *"Để kết thúc phần trình bày, em xin tóm tắt các **Engineering Trade-offs** chính mà em đã cân nhắc trong kiến trúc:*
> 
> 1. **Latency vs Retrieval Accuracy**: Việc dùng Multi-Query Expansion kết hợp Cohere Cross-Encoder Rerank làm tăng độ chính xác tìm kiếm RAG lên đáng kể, nhưng làm tăng latency khoảng ~300ms. Em đã tối ưu bằng cách giới hạn max 4 query song song và đặt timeout cho Cohere API.
> 
> 2. **LLM Cost & Speed Optimization**: Em sử dụng Groq Cloud API với mô hình **Llama-3.3-70B** đạt tốc độ ~250-300 tokens/s, giúp các bước Agentic Decision (Spam, Classify, Supervisor, Reasoning) hoàn tất chỉ trong dưới 2.5 giây.
> 
> 3. **Scalability Roadmap**: 
>    - Hiện tại hệ thống chạy SQLite WAL mode phù hợp cho scale vừa và nhỏ. Khi lên Production thực sự với lưu lượng lớn, lớp DB Persistence có thể chuyển đổi dễ dàng sang **PostgreSQL (pgvector)** hoặc **Redis Stream Message Queue**.
>    - Đóng gói toàn bộ backend thành Docker Container và mở rộng API endpoints qua FastAPI (`app/main.py`).
> 
> *Em cảm ơn Anh/Chị trong Hội đồng Kỹ thuật đã lắng nghe. Em rất mong nhận được các câu hỏi phản biện chuyên sâu từ Anh/Chị ạ!"*

---

## 🛠️ DANH SÁCH TỪ KHÓA KỸ THUẬT NỔI BẬT CẦN ĐỂ CẬP TRONG BÀI PHỎNG VẤN

| Thuật ngữ Kỹ thuật | Khái niệm & Ứng dụng trong dự án của bạn |
|--------------------|------------------------------------------|
| **LangGraph State Machine** | Graph quản lý trạng thái đa Agent (State Graph, Cyclic Loops, Memory Checkpointer). |
| **HNSW Indexing** | Hierarchical Navigable Small World Graph index trong Qdrant giúp Vector Search đạt tốc độ O(log N). |
| **Dense Vector Embeddings** | Biểu diễn ngữ nghĩa 384 dimensions qua `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. |
| **Cross-Encoder Reranking** | Tái xếp hạng tài liệu bằng `Cohere Rerank v3 (rerank-multilingual-v3.0)` cho độ tương quan chính xác cao. |
| **Recursive Character Chunking** | Tách đoạn văn bản theo thứ tự ưu tiên ngữ nghĩa (`\n===`, `\n---`, `\n\n`, `\n`, `.`) với 150-char overlap. |
| **Deterministic SHA-256 Point ID** | Sinh ID ổn định qua `hashlib.sha256` chống trùng lặp point khi re-upsert vào Qdrant. |
| **Confidence Score Calibration** | Hàm quy đổi toán học piecewise mapping từ điểm Cosine thô về phần trăm % trung thực. |
| **Decision Matrix Guardrails** | Ma trận đánh giá an toàn 2 lớp (Rủi ro nghiệp vụ + Ngưỡng tin cậy RAG). |
| **Human-in-the-Loop (HITL)** | Luồng can thiệp con người đóng gói AI Briefing Package (Sentiment, Recommendation, Auto-Draft). |
| **SQLite WAL Mode** | Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) giải quyết tranh chấp ghi dữ liệu đa luồng. |
