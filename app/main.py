import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router, tickets_db
from app.services.qdrant_service import seed_initial_kb

app = FastAPI(
    title="AI Support Agent — Autonomous Ops Backend",
    description="Backend Python hỗ trợ LangGraph Multi-Agent Architecture, Qdrant Vector DB, và Human-in-the-Loop Workflow.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

@app.on_event("startup")
def startup_event():
    """Khởi tạo seed data cho Qdrant Vector DB và Tickets DB."""
    seed_initial_kb()
    print("[Qdrant Vector DB] Initialized & Seeded successfully.")
    print("[LangGraph Multi-Agent Engine] State Machine ready.")

@app.get("/")
def root():
    return {
        "system": "AUTOMATION/AGENT — Tổng đài Hỗ trợ Tự vận hành",
        "backend": "Python + LangGraph + Qdrant Vector DB",
        "docs_url": "/docs",
        "api_endpoint": "/api/tickets"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
