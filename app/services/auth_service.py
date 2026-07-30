import os
import json
import sqlite3
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime


DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "user.db")


class AuthService:
    """Service quản lý Đăng ký, Đăng nhập và Phân quyền Người dùng lưu trữ trên SQLite Database."""

    def __init__(self):
        self.db_path = os.path.abspath(DB_FILE)
        self._init_sqlite_db()
        self._seed_default_users()

    def _get_connection(self) -> sqlite3.Connection:
        """Tạo kết nối tới SQLite DB với Row Factory trả về dict."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _hash_password(self, password: str) -> str:
        """Mã hóa mật khẩu sử dụng SHA-256 kèm salt cố định."""
        salt = "gft_autonomous_agent_salt_2026"
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    def _init_sqlite_db(self):
        """Khởi tạo Bảng 'users' và 'tickets' trong SQLite Database nếu chưa tồn tại."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        email TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'customer',
                        created_at TEXT NOT NULL
                    );
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tickets (
                        id TEXT PRIMARY KEY,
                        customer_name TEXT NOT NULL,
                        customer_email TEXT NOT NULL,
                        channel TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        content TEXT NOT NULL,
                        category TEXT,
                        priority TEXT,
                        status TEXT NOT NULL,
                        confidence_score REAL,
                        citations_json TEXT,
                        ai_answer TEXT,
                        clarification_question TEXT,
                        missing_slots_json TEXT,
                        context_package_json TEXT,
                        logs_json TEXT,
                        created_at TEXT NOT NULL,
                        resolved_at TEXT
                    );
                """)
                conn.commit()
        except Exception as e:
            print(f"Lỗi khởi tạo SQLite Database: {e}")


    def _seed_default_users(self):
        """Tạo sẵn các tài khoản demo mặc định trong SQLite nếu chưa tồn tại."""
        defaults = [
            {
                "username": "admin",
                "password": "123",
                "email": "admin@gft.com",
                "full_name": "Quản Trị Viên / Nhân Sự (Admin)",
                "role": "admin"
            },
            {
                "username": "customer",
                "password": "123",
                "email": "khachhang@gmail.com",
                "full_name": "Nguyễn Văn A (Khách hàng)",
                "role": "customer"
            }
        ]

        for u in defaults:
            username_clean = u["username"].lower()
            existing = self.get_user_by_username(username_clean)
            if not existing:
                self.register_user(
                    username=username_clean,
                    password=u["password"],
                    email=u["email"],
                    full_name=u["full_name"],
                    role=u["role"]
                )

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin người dùng theo Username từ SQLite."""
        username_clean = username.strip().lower()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username_clean,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            print(f"Lỗi truy vấn SQLite get_user_by_username: {e}")
        return None

    def register_user(
        self,
        username: str,
        password: str,
        email: str,
        full_name: str,
        role: str = "customer"
    ) -> Dict[str, Any]:
        """Đăng ký tài khoản mới lưu vào SQLite DB."""
        username_clean = username.strip().lower()
        if not username_clean:
            return {"success": False, "message": "Tên đăng nhập không được để trống!"}

        if self.get_user_by_username(username_clean):
            return {"success": False, "message": f"Tài khoản '{username_clean}' đã tồn tại trong Hệ thống!"}

        if len(password) < 3:
            return {"success": False, "message": "Mật khẩu phải có ít nhất 3 ký tự!"}

        user_role = "admin" if role == "admin" else "customer"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        password_hash = self._hash_password(password)


        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, full_name, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username_clean, password_hash, email.strip(), full_name.strip() or username_clean, user_role, created_at))
                conn.commit()

            user_data = {
                "username": username_clean,
                "email": email.strip(),
                "full_name": full_name.strip() or username_clean,
                "role": user_role,
                "created_at": created_at
            }
            return {"success": True, "message": "Đăng ký tài khoản thành công!", "user": user_data}
        except Exception as e:
            return {"success": False, "message": f"Lỗi lưu trữ dữ liệu SQLite: {e}"}

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Xác thực đăng nhập tài khoản từ SQLite DB."""
        user = self.get_user_by_username(username)
        if not user:
            return None

        if user["password_hash"] == self._hash_password(password):
            return {
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "created_at": user.get("created_at")
            }

        return None

    def save_ticket(self, t: Dict[str, Any]):
        """Lưu hoặc cập nhật thông tin Ticket vào SQLite Database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tickets (
                        id, customer_name, customer_email, channel, subject, content,
                        category, priority, status, confidence_score, citations_json,
                        ai_answer, clarification_question, missing_slots_json,
                        context_package_json, logs_json, created_at, resolved_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        status=excluded.status,
                        ai_answer=excluded.ai_answer,
                        resolved_at=excluded.resolved_at,
                        logs_json=excluded.logs_json;
                """, (
                    t["id"],
                    t.get("customerName", ""),
                    t.get("customerEmail", ""),
                    t.get("channel", "web"),
                    t.get("subject", ""),
                    t.get("content", ""),
                    t.get("category", "faq"),
                    t.get("priority", "P3_LOW"),
                    t.get("status", "NEW"),
                    t.get("confidenceScore", 0.0),
                    json.dumps(t.get("citations", []), ensure_ascii=False),
                    t.get("aiAnswer"),
                    t.get("clarificationQuestion"),
                    json.dumps(t.get("missingSlots", []), ensure_ascii=False),
                    json.dumps(t.get("contextPackage", {}), ensure_ascii=False),
                    json.dumps(t.get("logs", []), ensure_ascii=False),
                    t.get("createdAt", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    t.get("resolvedAt")
                ))
                conn.commit()
        except Exception as e:
            print(f"Lỗi lưu ticket vào SQLite: {e}")

    def load_all_tickets(self) -> Dict[str, Dict[str, Any]]:
        """Tải toàn bộ danh sách Ticket từ SQLite Database."""
        tickets_db: Dict[str, Dict[str, Any]] = {}
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tickets ORDER BY created_at ASC")
                rows = cursor.fetchall()
                for row in rows:
                    r = dict(row)
                    ticket_id = r["id"]
                    tickets_db[ticket_id] = {
                        "id": ticket_id,
                        "customerName": r.get("customer_name"),
                        "customerEmail": r.get("customer_email"),
                        "channel": r.get("channel"),
                        "subject": r.get("subject"),
                        "content": r.get("content"),
                        "category": r.get("category"),
                        "priority": r.get("priority"),
                        "status": r.get("status"),
                        "confidenceScore": r.get("confidence_score"),
                        "citations": json.loads(r.get("citations_json") or "[]"),
                        "aiAnswer": r.get("ai_answer"),
                        "clarificationQuestion": r.get("clarification_question"),
                        "missingSlots": json.loads(r.get("missing_slots_json") or "[]"),
                        "contextPackage": json.loads(r.get("context_package_json") or "{}"),
                        "logs": json.loads(r.get("logs_json") or "[]"),
                        "createdAt": r.get("created_at"),
                        "resolvedAt": r.get("resolved_at")
                    }
        except Exception as e:
            print(f"Lỗi đọc danh sách tickets từ SQLite: {e}")
        return tickets_db

# Singleton instance
auth_service = AuthService()

