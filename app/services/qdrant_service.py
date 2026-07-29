import os
import math
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue

COLLECTION_NAME = "knowledge_base"
VECTOR_DIM = 384  # Standard embedding dimension

class QdrantKBEngine:
    def __init__(self, url: Optional[str] = None, in_memory: bool = False):
        # Default connection logic: try Qdrant Docker (localhost:6333) or fallback to :memory:
        qdrant_url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        
        try:
            if in_memory:
                self.client = QdrantClient(location=":memory:")
                print("[Qdrant] Running in In-Memory Mode.")
            else:
                self.client = QdrantClient(url=qdrant_url, timeout=3.0)
                # Test connection
                self.client.get_collections()
                print(f"[Qdrant] Successfully connected to Qdrant Docker/Server at {qdrant_url}.")
        except Exception as e:
            print(f"[Qdrant] Could not connect to {qdrant_url} ({e}). Falling back to In-Memory mode.")
            self.client = QdrantClient(location=":memory:")


        self._init_collection()

    def _init_collection(self):
        """Khởi tạo collection Qdrant với thông số HNSW Vector Search."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == COLLECTION_NAME for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
                )
        except Exception as err:
            print(f"⚠️ Collection init warning: {err}")

    def _simple_embedding(self, text: str) -> List[float]:
        """Mô phỏng hàm sinh Vector Embedding (384 dim normalized)."""
        vec = np.zeros(VECTOR_DIM, dtype=float)
        words = text.lower().split()
        for idx, word in enumerate(words):
            hash_val = sum(ord(c) for c in word)
            pos = hash_val % VECTOR_DIM
            vec[pos] += 1.0 / (idx + 1)
        
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec = np.random.randn(VECTOR_DIM)
            vec = vec / np.linalg.norm(vec)
        
        return vec.tolist()

    def upsert_document(self, doc_id: str, title: str, category: str, content: str, tags: List[str], version: str = "v1.0"):
        """Nạp và chia đoạn (chunking) tài liệu vào Qdrant Vector Collection."""
        chunks = [content[i:i+200] for i in range(0, len(content), 180)]
        points = []

        for idx, chunk in enumerate(chunks):
            point_id = hash(f"{doc_id}_{idx}") & 0x7FFFFFFF
            vector = self._simple_embedding(f"{title} {category} {' '.join(tags)} {chunk}")
            
            payload = {
                "doc_id": doc_id,
                "doc_title": title,
                "category": category,
                "section": f"Trích đoạn {idx + 1}",
                "snippet": chunk,
                "tags": tags,
                "version": version
            }

            points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        self.client.upsert(collection_name=COLLECTION_NAME, points=points)

    def search_relevant_chunks(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Tìm kiếm các đoạn văn bản tương đồng cao nhất từ Qdrant Vector DB."""
        query_vector = self._simple_embedding(query)
        
        search_results = []
        try:
            # qdrant-client >= 1.10 dùng query_points
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_vector,
                    limit=limit
                )
                search_results = getattr(res, "points", [])
            elif hasattr(self.client, "search"):
                search_results = self.client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=limit
                )
        except Exception as err:
            print(f"⚠️ Search error: {err}")

        citations = []
        for res in search_results:
            payload = getattr(res, "payload", {}) or {}
            score = getattr(res, "score", 0.85)
            citations.append({
                "docId": payload.get("doc_id", "KB-UNKNOWN"),
                "docTitle": payload.get("doc_title", "Tài liệu hệ thống"),
                "section": payload.get("section", "Phần nội dung"),
                "snippet": payload.get("snippet", ""),
                "relevanceScore": round(float(score), 2)
            })

        return citations


# Global Qdrant KB instance
qdrant_kb = QdrantKBEngine()

def seed_initial_kb():
    """Khởi tạo kho tri thức mặc định cho Qdrant."""
    documents = [
        {
            "doc_id": "KB-POL-001",
            "title": "Chính sách Hoàn tiền & Hủy dịch vụ năm 2026",
            "category": "Thanh toán & Hóa đơn",
            "content": "Hoàn tiền 100% nếu tài khoản phát sinh lỗi thanh toán trùng lặp (Double billing) hoặc gói cước bị gián đoạn quá 48 giờ liên tục. Thời gian xử lý hoàn tiền 3-5 ngày làm việc qua Momo/VNPAY.",
            "tags": ["hoàn tiền", "thanh toán", "hủy gói", "momo", "vnpay"]
        },
        {
            "doc_id": "KB-TECH-002",
            "title": "Hướng dẫn Xử lý Sự cố Kết nối API & Lỗi HTTP 500 / 403",
            "category": "Kỹ thuật & Tích hợp",
            "content": "Lỗi 403 Forbidden: Kiểm tra API Key hết hạn hoặc chưa whitelist IP Client. Lỗi 500 Internal Error: Payload JSON đúng format <10MB. Thử lại sau 60s với Exponential Backoff.",
            "tags": ["lỗi 403", "lỗi 500", "api key", "ip client", "kỹ thuật"]
        },
        {
            "doc_id": "KB-PRICE-003",
            "title": "Bảng giá Gói cước Enterprise & Quyền lợi SLA",
            "category": "Hỏi đáp Thông tin",
            "content": "Gói Enterprise: Từ 12.000.000 VNĐ/tháng, không giới hạn ticket, cam kết SLA 99.99% uptime máy chủ, phản hồi sự cố khẩn cấp < 15 phút.",
            "tags": ["bảng giá", "enterprise", "gói cước", "sla 99.9%"]
        },
        {
            "doc_id": "KB-SEC-004",
            "title": "Quy trình Xử lý Sự cố Khẩn cấp (P0 Emergency Protocol)",
            "category": "Quy trình Khẩn cấp",
            "content": "Sự cố P0: Sập máy chủ toàn bộ hoặc nghi ngờ rò rỉ dữ liệu. AI Agent KHÔNG TỰ XỬ LÝ các case P0, bắt buộc chuyển thẳng cho Trưởng ca DevOps trực tiếp can thiệp.",
            "tags": ["khẩn cấp", "p0", "sập máy chủ", "rò rỉ dữ liệu", "devops"]
        }
    ]

    for doc in documents:
        qdrant_kb.upsert_document(**doc)

# Initialize seed on module import
seed_initial_kb()
