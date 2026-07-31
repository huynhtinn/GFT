# 🔬 DANH SÁCH CÔNG CỤ, MÔ HÌNH, API VÀ NGUỒN THAM KHẢO CHÍNH
## Autonomous Customer Support Agent System

---

## 1. DANH SÁCH MÔ HÌNH AI VÀ DỊCH VỤ CLOUD API (AI MODELS & APIS)

### 1. Large Language Model (LLM Cloud API)
* **Nhà cung cấp**: Groq Cloud AI Inference Engine ([https://console.groq.com](https://console.groq.com))
* **Mô hình**: `llama-3.3-70b-versatile` (Meta Llama 3.3 70B Parameters)
* **Đặc điểm**: Tốc độ phản hồi cực nhanh (~250-300 tokens/giây), hỗ trợ xử lý ngữ cảnh dài (128k context window), suy luận tiếng Việt tốt.
* **Nhiệm vụ trong hệ thống**: Phân loại Spam, phân loại Intent & Priority, điều phối luồng Supervisor Agent, tối ưu hóa câu hỏi Query Optimizer, và thực hiện lập luận Chain-of-Thought trong Reasoning Layer.

### 2. Embedding Model (Multilingual Semantic Embeddings)
* **Nhà cung cấp**: HuggingFace / Sentence-Transformers ([https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2))
* **Mô hình**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
* **Đặc điểm**: Kích thước vector 384 chiều (normalized cosine), hỗ trợ 50+ ngôn ngữ (bao gồm tiếng Việt), chạy trực tiếp trên GPU/CPU local không tốn chi phí API.
* **Nhiệm vụ trong hệ thống**: Biến đổi văn bản đoạn tri thức và câu truy vấn người dùng thành các vector không gian biểu diễn ngữ nghĩa.

### 3. Re-ranking Model (Cohere Rerank API)
* **Nhà cung cấp**: Cohere AI ([https://cohere.com/rerank](https://cohere.com/rerank))
* **Mô hình**: `rerank-multilingual-v3.0`
* **Đặc điểm**: Mô hình Cross-Encoder chuyên dụng cho nhiệm vụ tái xếp hạng tài liệu tri thức dựa trên sự tương quan sâu giữa câu hỏi và đoạn văn bản.
* **Nhiệm vụ trong hệ thống**: Đánh giá và sắp xếp lại danh sách ứng viên Top-K tài liệu từ Qdrant DB để đưa các đoạn tri thức chuẩn xác nhất lên đầu trước khi gửi cho Reasoning Layer.

---

## 2. DANH SÁCH THƯ VIỆN VÀ CÔNG CỤ NỀN TẢNG (FRAMEWORKS & TOOLS)

| Công cụ / Thư viện | Phiên bản | Vai trò & Mục đích sử dụng trong hệ thống |
|-------------------|-----------|-------------------------------------------|
| **LangGraph** | `>= 0.2.60` | Khung điều phối luồng State Machine đa Agent (StateGraph, Conditional Edges, MemorySaver Checkpointer). |
| **LangChain Core** | `>= 0.3.30` | Các trừu tượng hóa tin nhắn Prompt (SystemMessage, HumanMessage, TypedDict State). |
| **LangChain Text Splitters** | `>= 0.3.0` | Thư viện chia nhỏ văn bản ngữ nghĩa `RecursiveCharacterTextSplitter`. |
| **Qdrant Client** | `>= 1.12.0` | Thư viện kết nối Vector Database Qdrant (HNSW Indexing, Vector Search, Cosine Distance). |
| **Qdrant Docker** | `qdrant/qdrant` | Container dịch vụ Vector DB lưu trữ vector embedding trên RAM/Disk với tốc độ truy vấn miligiây. |
| **SQLite3 (WAL Mode)** | Tích hợp sẵn Python | Cơ sở dữ liệu lưu trữ bền vững tài khoản người dùng và trạng thái toàn bộ ticket hỗ trợ. |
| **Streamlit** | `>= 1.30.0` | Framework xây dựng giao diện người dùng Web App mượt mà, hỗ trợ phân quyền Admin vs Customer. |
| **Pydantic & Pydantic Settings** | `>= 2.10.0` | Quản lý cấu hình tập trung đọc từ file `.env` và xác thực dữ liệu đầu vào/đầu ra. |
| **UV Package Manager** | Trình quản lý package | Quản lý môi trường ảo `.venv` và cài đặt thư viện tốc độ cao thay thế pip. |

---

## 3. TÀI LIỆU VÀ NGUỒN THAM KHẢO CHÍNH (REFERENCES)

1. **LangGraph State Machine Documentation**:
   * Official Guide: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
   * Human-in-the-Loop Architecture: [https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)

2. **Qdrant Vector Database Documentation**:
   * Official Docs: [https://qdrant.tech/documentation/](https://qdrant.tech/documentation/)
   * HNSW Vector Indexing & Metrics: [https://qdrant.tech/documentation/concepts/indexing/](https://qdrant.tech/documentation/concepts/indexing/)

3. **Cohere Rerank API Integration Guide**:
   * Cohere Rerank v3 Announcement: [https://cohere.com/blog/rerank-3](https://cohere.com/blog/rerank-3)
   * API Endpoint Specification: [https://docs.cohere.com/reference/rerank](https://docs.cohere.com/reference/rerank)

4. **SentenceTransformers & Multilingual Embeddings**:
   * Model Card (`paraphrase-multilingual-MiniLM-L12-v2`): [https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

5. **Groq Cloud Developer Hub**:
   * Groq Console & Rate Limits: [https://console.groq.com/docs/models](https://console.groq.com/docs/models)
