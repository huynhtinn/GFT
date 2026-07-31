FROM python:3.11-slim

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

WORKDIR /app

# Cài đặt system dependencies cơ bản
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml và mã nguồn
COPY pyproject.toml ./
COPY app ./app
COPY knowledge_base ./knowledge_base
COPY app_streamlit.py ./app_streamlit.py
COPY README.md ./

# Cài đặt Python dependencies
RUN pip install --upgrade pip && \
    pip install .

# Tải sẵn SentenceTransformers model vào Docker Layer để khởi động siêu nhanh
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Expose Streamlit (8501) và FastAPI (8000)
EXPOSE 8501 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Mặc định khởi chạy Streamlit Web Dashboard
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
