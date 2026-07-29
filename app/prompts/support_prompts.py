from typing import List, Dict

# =====================================================================
# SYSTEM PROMPTS
# =====================================================================

AUTO_REPLY_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Chăm sóc Khách hàng chuyên nghiệp. "
    "Hãy trả lời ngắn gọn, lịch sự, thân thiện và chính xác dựa trên tài liệu tri thức được cung cấp bên dưới."
)

HUMAN_DRAFT_SYSTEM_PROMPT = (
    "Bạn là AI hỗ trợ Nhân sự CSKH. "
    "Hãy soạn thảo một bản nháp câu trả lời chuyên nghiệp, thấu hiểu để Nhân sự duyệt trước khi gửi khách hàng."
)

# =====================================================================
# PROMPT MESSAGES BUILDERS
# =====================================================================

def build_auto_reply_messages(
    customer_name: str,
    subject: str,
    content: str,
    context_str: str
) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt cho mô hình LLM tự động phản hồi khách hàng kèm RAG context."""
    user_content = (
        f"Khách hàng: {customer_name}\n"
        f"Tiêu đề yêu cầu: {subject}\n"
        f"Nội dung chi tiết: {content}\n\n"
        f"Tài liệu tri thức liên quan từ Qdrant DB:\n{context_str}\n\n"
        "Hãy viết câu trả lời phản hồi khách hàng kèm trích dẫn nguồn tri thức liên quan."
    )
    
    return [
        {"role": "system", "content": AUTO_REPLY_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]


def build_human_draft_messages(
    subject: str,
    content: str,
    category: str
) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt cho mô hình LLM soạn thảo bản nháp trả lời cho Nhân sự (HITL)."""
    user_content = (
        f"Yêu cầu khách hàng: {subject} - {content}\n"
        f"Trạng thái: Cần con người can thiệp (Nhóm: {category.upper()})\n\n"
        "Hãy soạn bản nháp câu trả lời ngắn gọn, thấu hiểu và lịch sự cho Nhân sự duyệt."
    )

    return [
        {"role": "system", "content": HUMAN_DRAFT_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]


def build_clarification_question(customer_name: str) -> str:
    """Tạo mẫu câu hỏi tự động làm rõ thông tin thiếu (Clarification Loop)."""
    return (
        f"Kính chào {customer_name},\n\n"
        "Để hỗ trợ kiểm tra nguyên nhân lỗi 403 Forbidden, quý khách vui lòng cung cấp giúp em:\n"
        "1. 4 ký tự cuối của API Key đang sử dụng\n"
        "2. Địa chỉ IP Client thực hiện kết nối\n\n"
        "Xin cảm ơn quý khách!"
    )
