import os
import sqlite3
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "app.db")

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
        """Khởi tạo Bảng 'users' trong SQLite Database nếu chưa tồn tại."""
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
                conn.commit()
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo SQLite Database: {e}")

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
            print(f"⚠️ Lỗi truy vấn SQLite get_user_by_username: {e}")
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

# Singleton instance
auth_service = AuthService()
