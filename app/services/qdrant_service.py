import os
import hashlib
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from app.config.settings import settings

COLLECTION_NAME = settings.QDRANT_COLLECTION_NAME
VECTOR_DIM = settings.VECTOR_DIM

# ── Embedding Model (Sentence Transformers) ────────────────────────────────────
# Sử dụng paraphrase-multilingual-MiniLM-L12-v2 cho semantic embedding thực sự.
# Model này hỗ trợ 50+ ngôn ngữ (bao gồm tiếng Việt), output 384 dimensions.
_embedding_model = None

def _get_embedding_model():
    """Lazy-load SentenceTransformer model (chỉ tải 1 lần duy nhất)."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        model_name = settings.EMBEDDING_MODEL_NAME
        print(f"[Embedding] Đang tải model '{model_name}'...")
        _embedding_model = SentenceTransformer(model_name)
        print(f"[Embedding] Model '{model_name}' đã sẵn sàng (dim={_embedding_model.get_embedding_dimension()}).")
    return _embedding_model


# ── Chunking (RecursiveCharacterTextSplitter) ──────────────────────────────────
from langchain_text_splitters import RecursiveCharacterTextSplitter

def _create_text_splitter() -> RecursiveCharacterTextSplitter:
    """Tạo text splitter tách theo ranh giới ngữ nghĩa (heading, đoạn, câu)."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        separators=[
            "\n===",       # Heading lớn (=== SECTION ===)
            "\n---",       # Horizontal rule
            "\n\n",        # Đoạn văn (paragraph)
            "\n",          # Xuống dòng
            "。",           # Dấu chấm câu tiếng Nhật (nếu có)
            ".",           # Dấu chấm câu
            " ",           # Khoảng trắng (word boundary)
            "",            # Fallback: từng ký tự
        ],
        length_function=len,
        is_separator_regex=False,
    )


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
        self._text_splitter = _create_text_splitter()

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

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Sinh semantic embedding vectors bằng SentenceTransformer (batch).
        
        Model: paraphrase-multilingual-MiniLM-L12-v2
        - 384 dimensions, cosine similarity
        - Hỗ trợ tiếng Việt và 50+ ngôn ngữ khác
        """
        model = _get_embedding_model()
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

    def _embed_single(self, text: str) -> List[float]:
        """Sinh embedding vector cho một câu truy vấn duy nhất."""
        return self._embed([text])[0]

    @staticmethod
    def _deterministic_point_id(doc_id: str, chunk_idx: int) -> int:
        """Tạo Point ID ổn định, deterministic bằng hashlib (không phụ thuộc PYTHONHASHSEED).
        
        Đảm bảo cùng doc_id + chunk_idx luôn cho ra cùng point_id,
        tránh bị trùng lặp khi re-upsert.
        """
        raw = f"{doc_id}_chunk_{chunk_idx}"
        hash_hex = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        # Lấy 8 hex chars đầu (32 bit) để tạo positive int cho Qdrant
        return int(hash_hex[:8], 16)

    def upsert_document(self, doc_id: str, title: str, category: str, content: str, tags: List[str], version: str = "v1.0"):
        """Nạp và chia đoạn (chunking) tài liệu vào Qdrant Vector Collection.
        
        Sử dụng RecursiveCharacterTextSplitter để chia theo ranh giới ngữ nghĩa
        (heading → paragraph → sentence → word), tránh cắt ngang giữa câu.
        """
        # Tiền xử lý: chuẩn hóa khoảng trắng thừa
        clean_content = content.strip()
        if not clean_content:
            return

        # Chia đoạn thông minh bằng RecursiveCharacterTextSplitter
        chunks = self._text_splitter.split_text(clean_content)
        
        if not chunks:
            return

        # Tạo embedding text: kết hợp metadata + nội dung chunk để enrichment
        texts_to_embed = [
            f"{title} | {category} | {' '.join(tags)} | {chunk}"
            for chunk in chunks
        ]
        
        # Batch embedding (hiệu quả hơn nhiều so với encode từng câu)
        vectors = self._embed(texts_to_embed)

        points = []
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point_id = self._deterministic_point_id(doc_id, idx)
            
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
        print(f"[Qdrant] Đã upsert {len(points)} chunks cho document [{doc_id}] '{title}'")

    def rerank_citations(
        self,
        query: str,
        citations: List[Dict[str, Any]],
        cohere_api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Tái xếp hạng danh sách trích dẫn bằng Cohere Rerank API.
        
        Cohere Rerank trả về relevance_score từ 0.0 đến 1.0.
        Score này được giữ nguyên (không scale nhân tạo) để đảm bảo
        confidence metric phản ánh đúng chất lượng retrieval.
        """
        api_key = cohere_api_key or settings.COHERE_API_KEY
        if not api_key:
            return citations

        if not citations:
            return citations

        try:
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
                    
                    # Cập nhật relevance score trực tiếp từ Cohere (không scale nhân tạo)
                    for item in results:
                        idx = item.get("index")
                        raw_score = float(item.get("relevance_score", 0.0))
                        if 0 <= idx < len(citations):
                            citations[idx]["relevanceScore"] = round(raw_score, 4)
                    
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
        """Tìm kiếm các đoạn văn bản tương đồng cao nhất từ Qdrant Vector DB.
        
        Sử dụng SentenceTransformer embedding cho truy vấn, sau đó tùy chọn
        Cohere Rerank để tái xếp hạng kết quả.
        """
        query_vector = self._embed_single(query)
        
        # Nếu dùng Rerank và có API Key, kéo nhiều ứng viên hơn từ Qdrant (gấp đôi limit)
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
            score = getattr(res, "score", 0.0)
            citations.append({
                "docId": payload.get("doc_id", "KB-UNKNOWN"),
                "docTitle": payload.get("doc_title", "Tài liệu hệ thống"),
                "section": payload.get("section", "Phần nội dung"),
                "snippet": payload.get("snippet", ""),
                "relevanceScore": round(float(score), 4)
            })

        # Thực hiện Rerank nếu được kích hoạt
        if use_rerank_active:
            citations = self.rerank_citations(query, citations, cohere_api_key=effective_api_key)
        
        # Sau khi Rerank hoặc search, chỉ giữ lại Top limit tài liệu tốt nhất
        citations = citations[:limit]

        return citations


def seed_initial_kb(kb_dir: Optional[str] = None):
    """Đọc toàn bộ file trong thư mục knowledge_base/ và nạp vào Qdrant Vector DB."""
    if kb_dir is None:
        kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base"))
    
    if not os.path.exists(kb_dir):
        print(f"[Qdrant Seed] Thư mục tri thức '{kb_dir}' không tồn tại. Bỏ qua seeding.")
        return

    cat_map = {
        "billing": "Thanh toán & Hóa đơn",
        "emergency": "Quy trình Khẩn cấp",
        "faq": "Hỏi đáp Thông tin",
        "technical": "Kỹ thuật & Tích hợp"
    }

    count = 0
    for root, _, files in os.walk(kb_dir):
        for f in files:
            if f.endswith(".txt"):
                file_path = os.path.join(root, f)
                rel_dir = os.path.basename(root)
                category = cat_map.get(rel_dir, "Hỏi đáp Thông tin")
                doc_title = os.path.splitext(f)[0].replace("-", " ").title()
                doc_id = f"KB-FILE-{hash(f) % 9000 + 1000}"
                
                try:
                    with open(file_path, "r", encoding="utf-8") as file_obj:
                        content = file_obj.read()
                    
                    qdrant_kb.upsert_document(
                        doc_id=doc_id,
                        title=doc_title,
                        category=category,
                        content=content,
                        tags=[rel_dir, "kb_auto_seed"]
                    )
                    count += 1
                except Exception as err:
                    print(f"[Qdrant Seed Error] {file_path}: {err}")

    print(f"[Qdrant Seed] Đã nạp thành công {count} tài liệu từ '{kb_dir}' vào Qdrant Vector DB.")


# Global Qdrant KB instance
qdrant_kb = QdrantKBEngine()