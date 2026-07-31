import os
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

from app.config.settings import settings

logger = logging.getLogger("groq_llm_service")
logging.basicConfig(level=logging.INFO)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def parse_json_response(raw_response: Optional[str]) -> Optional[Dict[str, Any]]:
    """Hàm helper trích xuất và parse JSON an toàn từ phản hồi của LLM."""
    if not raw_response:
        return None
    
    clean_text = raw_response.strip()
    
    # Loại bỏ code block markdown ```json ... ``` nếu có
    if clean_text.startswith("```"):
        lines = clean_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        clean_text = "\n".join(lines).strip()

    # Tìm vị trí JSON object {...}
    json_start = clean_text.find("{")
    json_end = clean_text.rfind("}") + 1
    
    if json_start != -1 and json_end > json_start:
        json_str = clean_text[json_start:json_end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as err:
            logger.warning(f"Lỗi parse JSON từ LLM output: {err}. Raw text snippet: {json_str[:150]}")
    
    return None


class GroqLLMService:
    """Service kết nối Groq Cloud API sử dụng mô hình Llama-3.3-70B kèm Retry & Structured Output."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.default_model = settings.GROQ_MODEL

    def is_available(self) -> bool:
        """Kiểm tra xem Groq API Key đã được cấu hình hay chưa."""
        return bool(self.api_key and self.api_key.startswith("gsk_"))

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        json_mode: bool = False,
        max_retries: int = 3
    ) -> Optional[str]:
        """Gửi yêu cầu Chat Completion tới Groq API với cơ chế Retry tự động (Exponential Backoff)."""
        if not self.is_available():
            logger.warning("GROQ_API_KEY chưa được cấu hình hoặc không hợp lệ. Khởi chạy chế độ Fallback.")
            return None

        target_model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AutonomousSupportAgent/1.0"
        }

        retry_delay = 1.0  # Ban đầu chờ 1s

        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(
                    GROQ_API_URL,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=15) as response:
                    if response.status == 200:
                        resp_data = json.loads(response.read().decode("utf-8"))
                        choices = resp_data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "").strip()
                        return None
            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8", errors="ignore")
                logger.error(f"[Groq API HTTP Error {e.code}] Attempt {attempt}/{max_retries}: {error_body[:200]}")
                if e.code in [429, 500, 502, 503, 504] and attempt < max_retries:
                    time.sleep(retry_delay)
                    retry_delay *= 2.0
                else:
                    break
            except Exception as e:
                logger.error(f"[Groq Connection Error] Attempt {attempt}/{max_retries}: {e}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    retry_delay *= 2.0
                else:
                    break

        return None


# Global instance
groq_llm = GroqLLMService()
