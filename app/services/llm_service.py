import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

from app.config.settings import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class GroqLLMService:
    """Service kết nối Groq Cloud API sử dụng mô hình llama-3.3-70b-versatile."""

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
        max_tokens: int = 1024
    ) -> Optional[str]:
        """Gửi yêu cầu Chat Completion tới Groq API."""
        if not self.is_available():
            print("⚠️ GROQ_API_KEY chưa được cấu hình. Sử dụng Fallback heuristic.")
            return None

        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }


        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AutonomousSupportAgent/1.0"
        }

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
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            print(f"❌ [Groq API Error {e.code}]: {error_body}")
        except Exception as e:
            print(f"❌ [Groq API Connection Error]: {e}")

        return None

# Global instance
groq_llm = GroqLLMService()
