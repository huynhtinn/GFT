"""
Runner script for Autonomous Support Agent Python Backend
Run with:
    uv run python run.py
or
    python run.py
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("----------------------------------------------------------------------")
    print("🤖 AUTOMATION/AGENT — Tổng đài Hỗ trợ Tự vận hành")
    print("📦 Framework: Python + LangGraph State Machine + Qdrant Vector DB")
    print("⚡ FastAPI Server running on: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("----------------------------------------------------------------------")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
