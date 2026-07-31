# 🛠️ HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY HỆ THỐNG
## Autonomous Customer Support Agent System

---

## 1. YÊU CẦU MÔI TRƯỜNG & PHẦN MỀM

Trước khi tiến hành cài đặt, đảm bảo máy tính của bạn đã cài đặt các công cụ sau:

* **Hệ điều hành**: Linux (Ubuntu 20.04/22.04 LTS), macOS, hoặc Windows (WSL2).
* **Python**: Phiên bản `>= 3.10` (Khuyên dùng Python 3.10 hoặc 3.11).
* **Docker & Docker Compose**: Để chạy Qdrant Vector Database Server (`qdrant/qdrant`).
* **UV Package Manager** (Khuyên dùng): Trình quản lý package Python siêu nhanh.

---

## 2. QUY TRÌNH CÀI ĐẶT CHI TIẾT (STEP-BY-STEP)

### Bước 1: Mở Thư Mục Dự Án
```bash
cd /home/tin/projects/GFT
```

### Bước 2: Cấu Hình File Biến Môi Trường (`.env`)
Tạo hoặc mở file `.env` tại thư mục gốc của dự án và điền thông tin API Key:

```env
# Groq Cloud API Key (Mô hình LLM: llama-3.3-70b-versatile)
# Đăng ký miễn phí tại: https://console.groq.com/keys
GROQ_API_KEY=gsk_your_groq_api_key_here

# Qdrant Database Server URL
QDRANT_URL=http://localhost:6333

# Cohere Reranker API Key (Tùy chọn - Dùng cho Re-ranking)
# Đăng ký miễn phí tại: https://dashboard.cohere.com/api-keys
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=rerank-multilingual-v3.0
USE_RERANK=true

# Ngưỡng tin cậy RAG % tối thiểu để AI tự động trả lời (Mặc định: 45.0%)
RAG_CONFIDENCE_THRESHOLD=45.0
```

---

### Bước 3: Khởi Chạy Qdrant Vector Database Server (Docker)
Sử dụng Docker Compose để khởi chạy container Qdrant DB trên cổng `6333`:

```bash
docker compose up -d
```

*Kiểm tra trạng thái container Qdrant:*
```bash
docker ps
```
*(Nếu thấy container `qdrant` có trạng thái `Up` và mở port `6333:6333` là đã thành công).*

---

### Bước 4: Cài Đặt Các Thư Viện Dependency (Bằng UV hoặc Pip)

#### Sử dụng UV Package Manager (Cách khuyên dùng):
```bash
uv sync
```

#### Hoặc sử dụng Pip trong virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

### Bước 5: Khởi Chạy Ứng Dụng Streamlit Web UI

Sử dụng lệnh sau để khởi chạy ứng dụng web Streamlit:

```bash
uv run streamlit run app_streamlit.py
```

Sau khi chạy thành công, ứng dụng sẽ mở giao diện tại địa chỉ:
* **Local URL**: [http://localhost:8501](http://localhost:8501)
* **Network URL**: [http://<your-ip>:8501](http://<your-ip>:8501)

---

## 3. TÀI KHOẢN DEMO SỬ DỤNG TRÊN GIAO DIỆN

Hệ thống đã tự động tạo sẵn 2 tài khoản demo mặc định trong cơ sở dữ liệu SQLite (`user.db`):

| Vai trò | Username | Mật khẩu | Chức năng chính |
|---------|----------|----------|-----------------|
| **Admin / Nhân Sự** | `admin` | `123` | Phê duyệt ticket bị chuyển tiếp (Escalations Queue), Xem AI Briefing Package, Quản lý Qdrant Knowledge Base. |
| **Khách Hàng** | `customer` | `123` | Gửi ticket hỗ trợ mới, Thử nghiệm kịch bản mẫu, Xem kết quả phản hồi AI và lịch sử ticket cá nhân. |

---

## 4. LỆNH KIỂM THỬ VÀ TROUBLESHOOTING

### 1. Kiểm thử biên dịch cú pháp mã nguồn:
```bash
.venv/bin/python -m py_compile app/services/qdrant_service.py app/main.py app/graph/nodes.py app_streamlit.py
```

### 2. Kiểm thử chạy nạp dữ liệu tri thức vào Qdrant (Auto-Seeding Test):
```bash
.venv/bin/python -c "from app.services.qdrant_service import seed_initial_kb; seed_initial_kb()"
```

### 3. Kiểm thử kết nối Groq Cloud API & Qdrant Vector Search:
```bash
.venv/bin/python -c "from app.services.qdrant_service import qdrant_kb; print(qdrant_kb.search_relevant_chunks('Hướng dẫn thanh toán', limit=2))"
```
