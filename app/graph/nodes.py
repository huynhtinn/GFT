import json
from datetime import datetime
from typing import Dict, Any
from app.graph.state import SupportState, PipelineLog, GroundingCitation, ContextPackage
from app.services.qdrant_service import qdrant_kb
from app.services.llm_service import groq_llm, parse_json_response
from app.config.settings import settings
from app.prompts.support_prompts import (
    build_auto_reply_messages,
    build_human_draft_messages,
    build_clarification_question,
    build_classifier_messages,
    build_spam_detector_messages,
    build_query_optimizer_messages,
    build_supervisor_messages,
    build_reasoning_messages
)


def spam_duplicate_detector_node(state: SupportState) -> Dict[str, Any]:
    """Node 1: Kiểm tra Spam & Trùng lặp bằng LLM Agent (Pure LLM Inspector)."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    subject = state.get("subject", "")
    content = state.get("content", "")
    is_spam = False
    spam_reason = "Yêu cầu hợp lệ"

    # Gọi LLM Agent kiểm tra Spam với JSON Mode
    if groq_llm.is_available():
        try:
            messages = build_spam_detector_messages(subject, content)
            raw_response = groq_llm.generate_completion(messages, temperature=0.1, json_mode=True)
            parsed = parse_json_response(raw_response)
            if parsed:
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
    """Node 2: Phân loại nhóm Intent & Priority bằng LLM Agent (Pure LLM Classifier)."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    subject = state.get("subject", "")
    content = state.get("content", "")
    
    category = "faq"
    priority = "P3_LOW"

    # Gọi thuần LLM Agent để phân loại động Intent & Priority với JSON Mode
    if groq_llm.is_available():
        try:
            messages = build_classifier_messages(subject, content)
            raw_response = groq_llm.generate_completion(messages, temperature=0.1, json_mode=True)
            parsed = parse_json_response(raw_response)
            if parsed:
                category = parsed.get("category", "faq")
                priority = parsed.get("priority", "P3_LOW")
        except Exception as err:
            print(f"LLM Classifier Error: {err}")

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


def supervisor_node(state: SupportState) -> Dict[str, Any]:
    """Node: Agent Supervisor phân tích và điều phối luồng xử lý động."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    subject = state.get("subject", "")
    content = state.get("content", "")
    category = state.get("category", "")
    priority = state.get("priority", "")

    # Mặc định quyết định
    decision = {
        "reasoning": "Sử dụng cấu hình mặc định do LLM không phản hồi.",
        "response_style": "formal",
        "reasoning_depth": "shallow",
        "escalation_required": False
    }

    if groq_llm.is_available():
        try:
            messages = build_supervisor_messages(subject, content, category, priority)
            raw_response = groq_llm.generate_completion(messages, temperature=0.1, json_mode=True)
            parsed = parse_json_response(raw_response)
            if parsed:
                decision = parsed
        except Exception as err:
            print(f"Supervisor Agent Error: {err}")

    # Đồng bộ nếu thuộc nhóm cần escalation
    is_high_risk = priority == "P0_CRITICAL" or category in ["complaint", "billing", "urgent"]
    if is_high_risk:
        decision["escalation_required"] = True

    logs.append({
        "stepId": "step_supervisor",
        "stepName": "Supervisor Decision Coordinator",
        "status": "success",
        "timestamp": now,
        "detail": f"Supervisor đã điều phối. Chuyển tiếp con người: {decision.get('escalation_required')}, Phong cách: {decision.get('response_style')}",
        "data": {"decision": decision}
    })

    return {
        "supervisor_decision": decision,
        "pipeline_logs": logs
    }


def query_optimizer_node(state: SupportState) -> Dict[str, Any]:
    """Node: Tối ưu hóa câu hỏi (Query Rewriter & Query Expansion)."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    subject = state.get("subject", "")
    content = state.get("content", "")

    # Mặc định
    rewritten_query = f"{subject} {content}"
    expanded_queries = [subject, content]

    if groq_llm.is_available():
        try:
            messages = build_query_optimizer_messages(subject, content)
            raw_response = groq_llm.generate_completion(messages, temperature=0.1, json_mode=True)
            parsed = parse_json_response(raw_response)
            if parsed:
                rewritten_query = parsed.get("rewritten_query", rewritten_query)
                expanded_queries = parsed.get("expanded_queries", expanded_queries)
        except Exception as err:
            print(f"Query Optimizer Agent Error: {err}")

    logs.append({
        "stepId": "step_optimizer",
        "stepName": "Query Optimizer & Expander",
        "status": "success",
        "timestamp": now,
        "detail": f"Đã tối ưu truy vấn thành công. Viết lại: '{rewritten_query[:60]}...'",
        "data": {
            "rewritten_query": rewritten_query,
            "expanded_queries": expanded_queries
        }
    })

    return {
        "rewritten_query": rewritten_query,
        "expanded_queries": expanded_queries,
        "pipeline_logs": logs
    }


def qdrant_rag_retrieval_node(state: SupportState) -> Dict[str, Any]:
    """Node 4: Thực hiện Qdrant Vector DB Retrieval & Grounding Citations (Multi-Query + Rerank)."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    # Lấy các câu truy vấn từ Query Optimizer
    rewritten_query = state.get("rewritten_query")
    expanded_queries = state.get("expanded_queries", [])
    
    if not rewritten_query:
        rewritten_query = f"{state.get('subject', '')} {state.get('content', '')}"

    # Pool các truy vấn để tìm kiếm
    queries_to_run = [rewritten_query]
    if expanded_queries:
        queries_to_run.extend(expanded_queries)
    
    # Độc lập lấy API Key
    effective_api_key = state.get("cohere_api_key") or settings.COHERE_API_KEY
    use_rerank = settings.USE_RERANK and bool(effective_api_key)

    # Thực hiện Multi-Query Retrieval
    all_citations = []
    for q in queries_to_run[:4]:
        raw_chunks = qdrant_kb.search_relevant_chunks(q, limit=settings.RAG_SEARCH_LIMIT * 2, cohere_api_key=None)
        all_citations.extend(raw_chunks)

    # Loại bỏ trùng lặp (De-duplicate) bằng docId + snippet
    unique_citations = []
    seen_keys = set()
    for c in all_citations:
        key = f"{c.get('docId')}_{c.get('snippet')}"
        if key not in seen_keys:
            seen_keys.add(key)
            unique_citations.append(c)

    # Tái xếp hạng (Rerank) toàn bộ danh sách gộp bằng Cohere Rerank
    if use_rerank and unique_citations:
        citations = qdrant_kb.rerank_citations(rewritten_query, unique_citations, cohere_api_key=effective_api_key)
    else:
        citations = unique_citations
        citations.sort(key=lambda x: x.get("relevanceScore", 0.0), reverse=True)

    citations = citations[:settings.RAG_SEARCH_LIMIT]
    best_score = max([c["relevanceScore"] for c in citations], default=0.0)
    confidence_score = round(best_score * 100, 1)

    rerank_status_str = f" (Multi-Query Rerank: {len(queries_to_run)} queries)" if use_rerank else " (Không Rerank)"
    logs.append({
        "stepId": "step_4",
        "stepName": "4. Qdrant Vector RAG & Grounding Engine",
        "status": "success" if len(citations) > 0 else "warning",
        "timestamp": now,
        "detail": f"Tìm thấy {len(citations)} đoạn tri thức tối ưu{rerank_status_str}. Grounding Confidence: {confidence_score}%",
        "data": {
            "citationsCount": len(citations), 
            "confidence_score": confidence_score, 
            "rerank_active": use_rerank,
            "queries_run": queries_to_run
        }
    })

    return {
        "citations": citations,
        "confidence_score": confidence_score,
        "pipeline_logs": logs
    }


def reasoning_node(state: SupportState) -> Dict[str, Any]:
    """Node: Thực hiện Chain-of-Thought suy luận logic trước khi sinh câu trả lời."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    subject = state.get("subject", "")
    content = state.get("content", "")
    category = state.get("category", "")
    priority = state.get("priority", "")
    citations = state.get("citations", [])
    supervisor_decision = state.get("supervisor_decision", {})

    # Chuẩn bị context tri thức
    context_str = ""
    if citations:
        context_str = "\n".join([f"[{c['docId']}] {c['docTitle']} (Mục {c['section']}):\n{c['snippet']}" for c in citations])
    else:
        context_str = "Không tìm thấy tài liệu liên quan."

    # Lập luận mặc định
    reasoning_steps = ["Bước 1: Không có mô hình LLM để suy luận. Sử dụng phương án phản hồi mặc định."]
    reasoning_output = "Hệ thống đã nhận thông tin và đang xử lý yêu cầu."

    if groq_llm.is_available():
        try:
            messages = build_reasoning_messages(subject, content, category, priority, context_str, supervisor_decision)
            raw_response = groq_llm.generate_completion(messages, temperature=0.1, max_tokens=1536, json_mode=True)
            parsed = parse_json_response(raw_response)
            if parsed:
                reasoning_steps = parsed.get("reasoning_steps", reasoning_steps)
                reasoning_output = parsed.get("reasoning_output", reasoning_output)
        except Exception as err:
            print(f"Reasoning Agent Error: {err}")

    logs.append({
        "stepId": "step_reasoning",
        "stepName": "Reasoning & Thought Layer",
        "status": "success",
        "timestamp": now,
        "detail": f"AI hoàn thành {len(reasoning_steps)} bước lập luận logic thành công.",
        "data": {
            "reasoning_steps": reasoning_steps,
            "reasoning_output": reasoning_output
        }
    })

    return {
        "reasoning_trace": reasoning_steps,
        "reasoning_output": reasoning_output,
        "pipeline_logs": logs
    }


def guardrails_router_node(state: SupportState) -> Dict[str, Any]:
    """Node 5: Router đánh giá ngưỡng an toàn & sinh câu trả lời."""
    now = datetime.now().isoformat()
    logs = list(state.get("pipeline_logs", []))

    category = state.get("category", "")
    priority = state.get("priority", "")
    confidence_score = state.get("confidence_score", 0.0)
    supervisor_decision = state.get("supervisor_decision", {})
    reasoning_output = state.get("reasoning_output", "")

    # Đọc quyết định từ Supervisor Agent
    escalation_required = supervisor_decision.get("escalation_required", False)
    is_high_risk = escalation_required or priority == "P0_CRITICAL" or category in ["complaint", "urgent"]
    is_low_confidence = confidence_score < settings.RAG_CONFIDENCE_THRESHOLD

    if is_high_risk or is_low_confidence:
        reason = "Supervisor quyết định chuyển tiếp / Sự cố P0 / Khiếu nại / Khẩn cấp" if is_high_risk else f"Độ tin cậy RAG < {settings.RAG_CONFIDENCE_THRESHOLD}%"
        
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
        ai_answer = reasoning_output if reasoning_output else "Hệ thống đã ghi nhận yêu cầu của quý khách và đang được xử lý."
        
        logs.append({
            "stepId": "step_5",
            "stepName": "5. Guardrails & Decision Matrix Router",
            "status": "success",
            "timestamp": now,
            "detail": f"TỰ ĐỘNG PHẢN HỒI AN TOÀN DỰA TRÊN LẬP LUẬN (Phong cách: {supervisor_decision.get('response_style', 'formal')}).",
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
    reasoning_output = state.get("reasoning_output", "")
    reasoning_trace = state.get("reasoning_trace", [])

    sentiment = "Bình thường"
    if priority == "P0_CRITICAL":
        sentiment = "Khẩn cấp"
    elif priority == "P1_HIGH":
        sentiment = "Bức xúc"

    auto_draft = reasoning_output
    if not auto_draft:
        auto_draft = (
            f"Kính chào {state.get('customer_name', 'quý khách')},\n\n"
            "Hệ thống đã tiếp nhận thông tin yêu cầu. Nhân viên hỗ trợ đang kiểm tra và sẽ phản hồi quý khách sớm nhất."
        )
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
            f"Đã tối ưu và mở rộng các truy vấn phụ",
            f"Tra cứu Qdrant + Rerank: Lấy Top {len(state.get('citations', []))} tài liệu tri thức",
            f"Lập luận hệ thống CoT: Hoàn thành {len(reasoning_trace)} bước suy luận",
            "Kích hoạt LangGraph Human Escalation"
        ],
        "recommendedAction": "Cảnh báo ca trực DevOps kiểm tra máy chủ" if priority == "P0_CRITICAL" else "Đối soát giao dịch và phản hồi khách hàng.",
        "autoDraftResponse": auto_draft,
        "confidenceScore": confidence_score,
        "escalationReason": f"Yêu cầu nhóm {category.upper()} rủi ro cao cần con người duyệt trực tiếp."
    }

    return {"context_package": context_package}
