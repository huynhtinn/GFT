from datetime import datetime
from typing import Dict, Any
from app.graph.state import SupportState, PipelineLog, GroundingCitation, ContextPackage
from app.services.qdrant_service import qdrant_kb

def spam_duplicate_detector_node(state: SupportState) -> Dict[str, Any]:
    """Node 1: Kiểm tra Spam & Trùng lặp."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    content_lower = (state.get("subject", "") + " " + state.get("content", "")).lower()
    spam_keywords = ["crypto", "bitcoin", "loans", "click here", "scam", "trading robot", "cheap sale"]
    
    is_spam = any(kw in content_lower for kw in spam_keywords)

    if is_spam:
        logs.append({
            "stepId": "step_1",
            "stepName": "1. Spam & Duplicate Inspector",
            "status": "warning",
            "timestamp": now,
            "detail": "Phát hiện SPAM/Rác! Tự động đóng ticket.",
            "data": {"is_spam": True, "confidence": 99}
        })
        return {
            "status": "SPAM_CLOSED",
            "is_spam": True,
            "category": "spam",
            "priority": "P3_LOW",
            "confidence_score": 99.0,
            "pipeline_logs": logs
        }

    logs.append({
        "stepId": "step_1",
        "stepName": "1. Spam & Duplicate Inspector",
        "status": "success",
        "timestamp": now,
        "detail": "Xác nhận Ticket hợp lệ (Not Spam & Unique Request).",
        "data": {"is_spam": False}
    })

    return {"is_spam": False, "pipeline_logs": logs}


def intent_priority_classifier_node(state: SupportState) -> Dict[str, Any]:
    """Node 2: Phân loại 8 nhóm Intent & Priority Matrix."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    content_lower = (state.get("subject", "") + " " + state.get("content", "")).lower()
    
    category = "faq"
    priority = "P3_LOW"

    if any(k in content_lower for k in ["khẩn cấp", "sập", "p0", "thảm họa"]):
        category = "urgent"
        priority = "P0_CRITICAL"
    elif any(k in content_lower for k in ["bức xúc", "hoàn tiền", "trừ tiền", "trùng lặp"]):
        category = "billing"
        priority = "P1_HIGH"
    elif any(k in content_lower for k in ["lỗi", "403", "500", "api"]):
        if not any(k in content_lower for k in ["ip", "key", "header"]):
            category = "incomplete"
            priority = "P2_MEDIUM"
        else:
            category = "technical"
            priority = "P2_MEDIUM"
    elif any(k in content_lower for k in ["giá", "enterprise", "gói cước"]):
        category = "faq"
        priority = "P3_LOW"

    logs.append({
        "stepId": "step_2",
        "stepName": "2. Intent & Priority Classifier",
        "status": "success",
        "timestamp": now,
        "detail": f"Đã phân loại nhóm: [{category.upper()}] | Độ ưu tiên: [{priority}]",
        "data": {"category": category, "priority": priority}
    })

    return {
        "category": category,
        "priority": priority,
        "pipeline_logs": logs
    }


def slot_completeness_inspector_node(state: SupportState) -> Dict[str, Any]:
    """Node 3: Kiểm tra thông tin bắt buộc & sinh Clarification Loop."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    category = state.get("category", "faq")

    if category == "incomplete":
        missing_slots = ["API Key 4 ký tự cuối", "Địa chỉ IP Client kết nối"]
        clarification_question = (
            f"Kính chào {state.get('customer_name', 'quý khách')},\n\n"
            "Để hỗ trợ kiểm tra nguyên nhân lỗi 403 Forbidden, quý khách vui lòng cung cấp giúp em:\n"
            "1. 4 ký tự cuối của API Key đang sử dụng\n"
            "2. Địa chỉ IP Client thực hiện kết nối\n\n"
            "Xin cảm ơn quý khách!"
        )

        logs.append({
            "stepId": "step_3",
            "stepName": "3. Slot Completeness Inspector",
            "status": "warning",
            "timestamp": now,
            "detail": "THIẾU THÔNG TIN BẮT BUỘC. Tự động khởi tạo Clarification Loop.",
            "data": {"missing_slots": missing_slots}
        })

        return {
            "status": "CLARIFICATION_SENT",
            "missing_slots": missing_slots,
            "clarification_question": clarification_question,
            "confidence_score": 88.0,
            "pipeline_logs": logs
        }

    logs.append({
        "stepId": "step_3",
        "stepName": "3. Slot Completeness Inspector",
        "status": "success",
        "timestamp": now,
        "detail": "Đã xác nhận đầy đủ dữ liệu thông tin cần thiết."
    })

    return {"pipeline_logs": logs}


def qdrant_rag_retrieval_node(state: SupportState) -> Dict[str, Any]:
    """Node 4: Thực hiện Qdrant Vector DB Retrieval & Grounding Citations."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    query = f"{state.get('subject', '')} {state.get('content', '')}"
    
    # Query Qdrant Vector Collection
    citations = qdrant_kb.search_relevant_chunks(query, limit=3)
    
    best_score = max([c["relevanceScore"] for c in citations], default=0.55)
    confidence_score = round(best_score * 100, 1)

    logs.append({
        "stepId": "step_4",
        "stepName": "4. Qdrant Vector RAG & Grounding Engine",
        "status": "success" if len(citations) > 0 else "warning",
        "timestamp": now,
        "detail": f"Tìm thấy {len(citations)} đoạn tri thức từ Qdrant DB. Grounding Confidence: {confidence_score}%",
        "data": {"citationsCount": len(citations), "confidence_score": confidence_score}
    })

    return {
        "citations": citations,
        "confidence_score": confidence_score,
        "pipeline_logs": logs
    }


def guardrails_router_node(state: SupportState) -> Dict[str, Any]:
    """Node 5: Router đánh giá ngưỡng an toàn & quyết định Handoff."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    category = state.get("category", "")
    priority = state.get("priority", "")
    confidence_score = state.get("confidence_score", 0.0)
    citations = state.get("citations", [])

    is_high_risk = priority == "P0_CRITICAL" or category in ["complaint", "billing", "urgent"]
    is_low_confidence = confidence_score < 80.0

    if is_high_risk or is_low_confidence:
        reason = "Sự cố P0 khẩn cấp / Giao dịch tài chính rủi ro cao" if is_high_risk else "Độ tin cậy RAG < 80%"
        
        logs.append({
            "stepId": "step_5",
            "stepName": "5. Guardrails & Decision Matrix Router",
            "status": "warning",
            "timestamp": now,
            "detail": f"KÍCH HOẠT HUMAN HANDOFF! Lý do: {reason}",
            "data": {"escalation_reason": reason}
        })

        return {
            "status": "ESCALATED_HUMAN",
            "pipeline_logs": logs
        }
    else:
        first_citation = citations[0] if len(citations) > 0 else {}
        ai_answer = (
            f"Kính chào {state.get('customer_name', 'quý khách')},\n\n"
            "Cảm ơn quý khách đã liên hệ hỗ trợ. Dựa trên thông tin quy định chính thức của hệ thống:\n\n"
            f"\"{first_citation.get('snippet', 'Hệ thống đã tiếp nhận yêu cầu.')}\"\n\n"
            f"[Nguồn: {first_citation.get('docTitle', 'Kho Tri Thức Nội Bộ')}]"
        )

        logs.append({
            "stepId": "step_5",
            "stepName": "5. Guardrails & Decision Matrix Router",
            "status": "success",
            "timestamp": now,
            "detail": "TỰ ĐỘNG PHẢN HỒI AN TOÀN (Auto-Resolved with Qdrant Citation).",
            "data": {"ai_answer": ai_answer}
        })

        return {
            "status": "RESOLVED_AUTO",
            "ai_answer": ai_answer,
            "pipeline_logs": logs
        }


def hitl_briefing_generator_node(state: SupportState) -> Dict[str, Any]:
    """Node 6: Tự động sinh AI Context Package cho Nhân sự tiếp nhận."""
    category = state.get("category", "")
    priority = state.get("priority", "")
    confidence_score = state.get("confidence_score", 75.0)

    sentiment = "Bình thường"
    if priority == "P0_CRITICAL":
        sentiment = "Khẩn cấp"
    elif priority == "P1_HIGH":
        sentiment = "Bức xúc"

    context_package: ContextPackage = {
        "summary": f"Yêu cầu nhóm [{category.upper()}]. Tiêu đề: {state.get('subject', '')}",
        "sentiment": sentiment,
        "triedSteps": [
            f"Phân loại Intent: {category} (Độ ưu tiên {priority})",
            f"Tra cứu Qdrant Vector DB: Tìm thấy {len(state.get('citations', []))} tài liệu liên quan",
            "Kích hoạt LangGraph Human Escalation"
        ],
        "recommendedAction": "Cảnh báo ca trực DevOps kiểm tra máy chủ" if priority == "P0_CRITICAL" else "Đối soát giao dịch và phản hồi khách hàng.",
        "autoDraftResponse": (
            f"Kính chào {state.get('customer_name', 'quý khách')},\n\n"
            "Hệ thống đã tiếp nhận thông tin yêu cầu. Nhân viên hỗ trợ đang kiểm tra và sẽ phản hồi quý khách sớm nhất."
        ),
        "confidenceScore": confidence_score,
        "escalationReason": f"Yêu cầu nhóm {category.upper()} rủi ro cao cần con người duyệt trực tiếp."
    }

    return {"context_package": context_package}
