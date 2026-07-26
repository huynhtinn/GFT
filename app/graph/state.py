from typing import TypedDict, List, Dict, Any, Optional

class GroundingCitation(TypedDict):
    """Cấu trúc dữ liệu trích dẫn tri thức từ Vector DB (Qdrant)."""
    docId: str
    docTitle: str
    section: str
    snippet: str
    relevanceScore: float

class ContextPackage(TypedDict):
    """Gói dữ liệu AI Context Briefing tổng hợp dành cho Nhân sự hỗ trợ (HITL)."""
    summary: str
    sentiment: str
    triedSteps: List[str]
    recommendedAction: str
    autoDraftResponse: str
    confidenceScore: float
    escalationReason: str

class PipelineLog(TypedDict):
    """Cấu trúc nhật ký ghi nhận từng bước xử lý trong LangGraph Pipeline."""
    stepId: str
    stepName: str
    status: str
    timestamp: str
    detail: str
    data: Optional[Dict[str, Any]]

class SupportState(TypedDict, total=False):
    """State quản lý toàn bộ vòng đời Ticket trong LangGraph State Machine."""
    ticket_id: str
    customer_name: str
    customer_email: str
    channel: str
    subject: str
    content: str
    
    category: str
    priority: str
    status: str
    
    missing_slots: List[str]
    clarification_question: str
    
    citations: List[GroundingCitation]
    confidence_score: float
    
    context_package: Optional[ContextPackage]
    ai_answer: str
    
    is_spam: bool
    is_duplicate: bool
    
    pipeline_logs: List[PipelineLog]

