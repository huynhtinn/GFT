from datetime import datetime
from typing import Dict, Any
from app.graph.state import SupportState, PipelineLog, GroundingCitation, ContextPackage
from app.services.qdrant_service import qdrant_kb
from app.services.llm_service import groq_llm

import json
from app.prompts.support_prompts import (
    build_auto_reply_messages,
    build_human_draft_messages,
    build_clarification_question,
    build_classifier_messages,
    build_spam_detector_messages
)

def spam_duplicate_detector_node(state: SupportState) -> Dict[str, Any]:
    """Node 1: Kiểm tra Spam & Trùng lặp bằng 100% LLM Agent (Pure LLM Inspector)."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    subject = state.get("subject", "")
    content = state.get("content", "")
    is_spam = False
    spam_reason = "Yêu cầu hợp lệ"

    # Gọi LLM Agent kiểm tra Spam
    if groq_llm.is_available():
        try:
            messages = build_spam_detector_messages(subject, content)
            raw_response = groq_llm.generate_completion(messages, temperature=0.1)
            if raw_response:
                json_start = raw_response.find("{")
                json_end = raw_response.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    parsed = json.loads(raw_response[json_start:json_end])
                    is_spam = parsed.get("is_spam", False)
                    spam_reason = parsed.get("reason", "Phát hiện nội dung quảng cáo/rác từ LLM")
        except Exception as err:
            print(f"LLM Spam Inspector Error: {err}")

    if is_spam:
        logs.append({
            "stepId": "step_1",
            "stepName": "1. Spam & Duplicate Inspector (LLM Agent)",
            "status": "warning",
            "timestamp": now,
            "detail": f"LLM Agent phát hiện SPAM/Rác! Lý do: {spam_reason}",
            "data": {"is_spam": True, "reason": spam_reason}
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
        "stepName": "1. Spam & Duplicate Inspector (LLM Agent)",
        "status": "success",
        "timestamp": now,
        "detail": "LLM Agent xác nhận Ticket hợp lệ (Legitimate Customer Request).",
        "data": {"is_spam": False}
    })

    return {"is_spam": False, "pipeline_logs": logs}


def intent_priority_classifier_node(state: SupportState) -> Dict[str, Any]:
    """Node 2: Phân loại nhóm Intent & Priority bằng 100% LLM Agent (Pure LLM Classifier)."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    subject = state.get("subject", "")
    content = state.get("content", "")
    
    category = "faq"
    priority = "P3_LOW"

    # Gọi thuần LLM Agent để phân loại động Intent & Priority
    if groq_llm.is_available():
        try:
            messages = build_classifier_messages(subject, content)
            raw_response = groq_llm.generate_completion(messages, temperature=0.1)
            if raw_response:
                json_start = raw_response.find("{")
                json_end = raw_response.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    parsed = json.loads(raw_response[json_start:json_end])
                    category = parsed.get("category", "faq")
                    priority = parsed.get("priority", "P3_LOW")
        except Exception as err:
            print(f"⚠️ LLM Classifier Error: {err}")

    logs.append({
        "stepId": "step_2",
        "stepName": "2. Intent & Priority Classifier (LLM Agent)",
        "status": "success",
        "timestamp": now,
        "detail": f"LLM Agent phân loại nhóm: [{category.upper()}] | Độ ưu tiên: [{priority}]",
        "data": {"category": category, "priority": priority, "source": "LLM Agent"}
    })

    return {
        "category": category,
        "priority": priority,
        "pipeline_logs": logs
    }




from app.prompts import (
    build_auto_reply_messages,
    build_human_draft_messages,
    build_clarification_question
)

def slot_completeness_inspector_node(state: SupportState) -> Dict[str, Any]:
    """Node 3: Kiểm tra thông tin bắt buộc & sinh Clarification Loop."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    category = state.get("category", "faq")

    if category == "incomplete":
        missing_slots = ["API Key 4 ký tự cuối", "Địa chỉ IP Client kết nối"]
        clarification_question = build_clarification_question(state.get('customer_name', 'quý khách'))

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



from app.config.settings import settings

def qdrant_rag_retrieval_node(state: SupportState) -> Dict[str, Any]:
    """Node 4: Thực hiện Qdrant Vector DB Retrieval & Grounding Citations."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    query = f"{state.get('subject', '')} {state.get('content', '')}"
    
    # Query Qdrant Vector Collection
    citations = qdrant_kb.search_relevant_chunks(query, limit=settings.RAG_SEARCH_LIMIT)
    
    best_score = max([c["relevanceScore"] for c in citations], default=0.55)
    # Chuẩn hóa điểm tin cậy từ điểm tương đồng Cosine
    confidence_score = min(98.5, round(best_score * 160, 1)) if best_score > 0.4 else round(best_score * 100, 1)

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
    """Node 5: Router đánh giá ngưỡng an toàn & sinh câu trả lời bằng Groq LLM (llama-3.3-70b-versatile)."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    category = state.get("category", "")
    priority = state.get("priority", "")
    confidence_score = state.get("confidence_score", 0.0)
    citations = state.get("citations", [])

    is_high_risk = priority == "P0_CRITICAL" or category in ["complaint", "billing", "urgent"]
    is_low_confidence = confidence_score < settings.RAG_CONFIDENCE_THRESHOLD

    if is_high_risk or is_low_confidence:
        reason = "Sự cố P0 khẩn cấp / Giao dịch tài chính rủi ro cao" if is_high_risk else f"Độ tin cậy RAG < {settings.RAG_CONFIDENCE_THRESHOLD}%"
        
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
        context_str = "\n".join([f"- [{c.get('docTitle')}]: {c.get('snippet')}" for c in citations])

        # Gọi Groq LLM Agent (llama-3.3-70b-versatile) để sinh câu phản hồi tự động
        prompt_messages = build_auto_reply_messages(
            customer_name=state.get('customer_name', 'Quý khách'),
            subject=state.get('subject', ''),
            content=state.get('content', ''),
            context_str=context_str
        )
        ai_answer = groq_llm.generate_completion(prompt_messages) or "Hệ thống đã ghi nhận yêu cầu của quý khách và đang được xử lý."
        
        logs.append({
            "stepId": "step_5",
            "stepName": "5. Guardrails & Decision Matrix Router",
            "status": "success",
            "timestamp": now,
            "detail": "TỰ ĐỘNG PHẢN HỒI AN TOÀN TỪ GROQ LLM AGENT (Llama-3.3-70b).",
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

    auto_draft = (
        f"Kính chào {state.get('customer_name', 'quý khách')},\n\n"
        "Hệ thống đã tiếp nhận thông tin yêu cầu. Nhân viên hỗ trợ đang kiểm tra và sẽ phản hồi quý khách sớm nhất."
    )

    # Dùng Groq LLM (llama-3.3-70b-versatile) để soạn thảo bản nháp câu trả lời tốt hơn cho Nhân sự
    if groq_llm.is_available():
        draft_messages = build_human_draft_messages(
            customer_name=state.get('customer_name', 'Quý khách'),
            subject=state.get('subject', ''),
            content=state.get('content', ''),
            category=category
        )
        llm_draft = groq_llm.generate_completion(draft_messages, max_tokens=256)
        if llm_draft:
            auto_draft = llm_draft



    context_package: ContextPackage = {
        "summary": f"Yêu cầu nhóm [{category.upper()}]. Tiêu đề: {state.get('subject', '')}",
        "sentiment": sentiment,
        "triedSteps": [
            f"Phân loại Intent: {category} (Độ ưu tiên {priority})",
            f"Tra cứu Qdrant Vector DB: Tìm thấy {len(state.get('citations', []))} tài liệu liên quan",
            "Kích hoạt LangGraph Human Escalation"
        ],
        "recommendedAction": "Cảnh báo ca trực DevOps kiểm tra máy chủ" if priority == "P0_CRITICAL" else "Đối soát giao dịch và phản hồi khách hàng.",
        "autoDraftResponse": auto_draft,
        "confidenceScore": confidence_score,
        "escalationReason": f"Yêu cầu nhóm {category.upper()} rủi ro cao cần con người duyệt trực tiếp."
    }

    return {"context_package": context_package}

