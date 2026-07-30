from typing import List, Dict

AUTO_REPLY_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Chăm sóc Khách hàng chuyên nghiệp. "
    "Hãy trả lời ngắn gọn, lịch sự, thân thiện và chính xác dựa trên tài liệu tri thức được cung cấp bên dưới."
)

HUMAN_DRAFT_SYSTEM_PROMPT = (
    "Bạn là AI hỗ trợ Nhân sự CSKH. "
    "Hãy soạn thảo một bản nháp câu trả lời chuyên nghiệp, thấu hiểu để Nhân sự duyệt trước khi gửi khách hàng."
)

CLASSIFIER_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Phân loại Yêu cầu (Intent & Priority Classifier).\n"
    "Nhiệm vụ: Phân tích Tiêu đề và Nội dung ticket để trả về JSON định dạng:\n"
    "{\"category\": \"<urgent|billing|technical|incomplete|faq|spam>\", \"priority\": \"<P0_CRITICAL|P1_HIGH|P2_MEDIUM|P3_LOW>\"}\n\n"
    "Quy tắc độ ưu tiên:\n"
    "- P0_CRITICAL: Khẩn cấp, sập hệ thống, thảm họa.\n"
    "- P1_HIGH: Bức xúc, khiếu nại tiền bạc, lỗi thanh toán.\n"
    "- P2_MEDIUM: Lỗi kỹ thuật 403/500, lỗi kết nối API hoặc thiếu info debug.\n"
    "- P3_LOW: Hỏi đáp FAQ, tư vấn giá gói cước hoặc spam."
)

SPAM_DETECTOR_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Kiểm tra Spam & Nội dung Độc hại (Spam Inspector).\n"
    "Nhiệm vụ: Phân tích Tiêu đề và Nội dung ticket xem có phải là spam, quảng cáo lừa đảo, rác, bối rối không có nghĩa hay không.\n"
    "Trả về kết quả định dạng JSON duy nhất:\n"
    "{\"is_spam\": true/false, \"reason\": \"<Lý do ngắn gọn>\"}"
)



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
    customer_name: str,
    subject: str,
    content: str,
    category: str
) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt cho mô hình LLM soạn thảo bản nháp trả lời cho Nhân sự (HITL)."""
    user_content = (
        f"Tên khách hàng: {customer_name}\n"
        f"Tiêu đề yêu cầu: {subject}\n"
        f"Nội dung chi tiết: {content}\n"
        f"Nhóm sự cố: {category.upper()}\n\n"
        f"Hãy soạn thảo câu trả lời mẫu hoàn chỉnh. Mở đầu bằng lời chào 'Kính gửi {customer_name},' và kết bài bằng 'Trân trọng, [Tên Nhân Sự]'."
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


def build_classifier_messages(subject: str, content: str) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt gửi LLM để phân loại Intent & Priority."""
    return [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Tiêu đề: {subject}\nNội dung: {content}"}
    ]


def build_spam_detector_messages(subject: str, content: str) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt gửi LLM để kiểm tra Spam/Rác."""
    return [
        {"role": "system", "content": SPAM_DETECTOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"Tiêu đề: {subject}\nNội dung: {content}"}
    ]


