import os
import math
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue

from app.config.settings import settings

COLLECTION_NAME = settings.QDRANT_COLLECTION_NAME
VECTOR_DIM = settings.VECTOR_DIM

class QdrantKBEngine:
    def __init__(self, url: Optional[str] = None, in_memory: bool = False):
        # Connection logic: try Qdrant Docker or fallback to :memory:
        qdrant_url = url or settings.QDRANT_URL
        
        try:
            if in_memory:
                self.client = QdrantClient(location=":memory:")
                print("[Qdrant] Running in In-Memory Mode.")
            else:
                self.client = QdrantClient(url=qdrant_url, timeout=settings.QDRANT_TIMEOUT_SECONDS)
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
            print(f"Collection init warning: {err}")

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
        chunk_size = settings.RAG_CHUNK_SIZE
        overlap = settings.RAG_CHUNK_OVERLAP
        step = max(1, chunk_size - overlap)
        
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), step)]
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

    def rerank_citations(
        self,
        query: str,
        citations: List[Dict[str, Any]],
        cohere_api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Tái xếp hạng danh sách trích dẫn bằng Cohere Rerank API."""
        api_key = cohere_api_key or settings.COHERE_API_KEY
        if not api_key:
            return citations

        if not citations:
            return citations

        try:
            # Chuẩn bị payload cho Cohere Rerank v1 API
            payload = {
                "model": settings.COHERE_MODEL,
                "query": query,
                "documents": [c["snippet"] for c in citations]
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AutonomousSupportAgent/1.0"
            }

            url = "https://api.cohere.com/v1/rerank"
            import json
            import urllib.request
            import urllib.error

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    results = resp_data.get("results", [])
                    
                    # Cập nhật điểm và ánh xạ lại (Chuẩn hóa Cohere Rerank probability sang Qdrant Cosine scale)
                    for item in results:
                        idx = item.get("index")
                        raw_score = float(item.get("relevance_score", 0.0))
                        if 0 <= idx < len(citations):
                            # Cohere Rerank v3.0 trả về xác suất từ 0.0 đến 1.0 (thường thấp, >=0.1 là rất khớp)
                            # Chuẩn hóa về thang điểm cosine của Qdrant (thường từ 0.4 đến 0.99)
                            if raw_score >= 0.1:
                                scaled_score = 0.4 + raw_score * 0.55
                            else:
                                scaled_score = raw_score * 4.0
                            citations[idx]["relevanceScore"] = round(min(0.99, scaled_score), 2)
                    
                    # Sắp xếp lại theo điểm mới giảm dần
                    citations.sort(key=lambda x: x["relevanceScore"], reverse=True)
        except Exception as e:
            print(f"[Cohere Rerank API Error]: {e}")
            # Fallback về sắp xếp cũ của Qdrant
        
        return citations

    def search_relevant_chunks(
        self,
        query: str,
        limit: int = 3,
        cohere_api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm các đoạn văn bản tương đồng cao nhất từ Qdrant Vector DB."""
        query_vector = self._simple_embedding(query)
        
        # Nếu dùng Rerank và có API Key, chúng ta kéo nhiều ứng viên hơn từ Qdrant (gấp đôi limit)
        effective_api_key = cohere_api_key or settings.COHERE_API_KEY
        use_rerank_active = settings.USE_RERANK and bool(effective_api_key)
        qdrant_limit = limit * 2 if use_rerank_active else limit

        search_results = []
        try:
            # qdrant-client >= 1.10 dùng query_points
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_vector,
                    limit=qdrant_limit
                )
                search_results = getattr(res, "points", [])
            elif hasattr(self.client, "search"):
                search_results = self.client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=qdrant_limit
                )
        except Exception as err:
            print(f"Search error: {err}")

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

        # Thực hiện Rerank nếu được kích hoạt
        if use_rerank_active:
            # Lưu lại điểm gốc Qdrant cho nhật ký nếu cần thiết (không bắt buộc)
            citations = self.rerank_citations(query, citations, cohere_api_key=effective_api_key)
            # Sau khi Rerank, chỉ giữ lại Top limit tài liệu tốt nhất
            citations = citations[:limit]

        return citations


# Global Qdrant KB instance
qdrant_kb = QdrantKBEngine()