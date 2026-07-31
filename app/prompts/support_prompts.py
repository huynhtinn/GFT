from typing import List, Dict, Any

AUTO_REPLY_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Chăm sóc Khách hàng chuyên nghiệp. "
    "Hãy trả lời ngắn gọn, lịch sự, thân thiện và chính xác dựa trên tài liệu tri thức được cung cấp bên dưới. "
    "LƯU Ý QUAN TRỌNG: Tuyệt đối không đề cập đến các thuật ngữ kỹ thuật nội bộ như 'RAG', 'tài liệu RAG', 'Qdrant', 'Vector DB', 'LLM', 'AI', 'Prompt', 'Supervisor' trong câu phản hồi gửi khách hàng. Hãy xưng hô và trả lời như một nhân viên hỗ trợ khách hàng bằng con người bình thường, tự nhiên và hữu ích."
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

QUERY_OPTIMIZER_SYSTEM_PROMPT = (
    "Bạn là AI chuyên tối ưu hóa truy vấn tìm kiếm tri thức (Query Optimizer).\n"
    "Nhiệm vụ: Phân tích Tiêu đề và Nội dung ticket của người dùng để trả về JSON định dạng duy nhất:\n"
    "{\n"
    "  \"rewritten_query\": \"<câu truy vấn rút gọn, tập trung vào bản chất lỗi để tìm kiếm tốt nhất>\",\n"
    "  \"expanded_queries\": [\n"
    "    \"<câu truy vấn phụ 1, tìm kiếm bằng thuật ngữ tương đương>\",\n"
    "    \"<câu truy vấn phụ 2, tập trung vào giải pháp kỹ thuật liên quan>\",\n"
    "    \"<câu truy vấn phụ 3, tìm kiếm theo từ khóa lỗi/sự cố chính>\"\n"
    "  ]\n"
    "}\n\n"
    "Yêu cầu: Viết các câu truy vấn bằng tiếng Việt (hoặc tiếng Anh nếu chứa thuật ngữ kỹ thuật) để tối ưu việc tìm kiếm ngữ nghĩa trong Vector DB."
)

SUPERVISOR_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Điều phối Luồng xử lý (Supervisor Agent).\n"
    "Nhiệm vụ: Dựa trên thông tin Ticket, Category và Priority, lập luận đưa ra quyết định điều phối luồng hỗ trợ dưới định dạng JSON duy nhất:\n"
    "{\n"
    "  \"reasoning\": \"<Lập luận ngắn gọn về lý do chọn chiến lược điều phối này>\",\n"
    "  \"response_style\": \"<formal|technical|empathetic>\",\n"
    "  \"reasoning_depth\": \"<shallow|deep>\",\n"
    "  \"escalation_required\": true/false\n"
    "}\n\n"
    "Quy tắc:\n"
    "- escalation_required đặt là true nếu priority là P0_CRITICAL hoặc thuộc nhóm khiếu nại (complaint).\n"
    "- Đối với nhóm billing: Nếu là yêu cầu thanh toán lỗi, đòi tiền, tranh chấp, bồi thường, hãy đặt escalation_required là true. Nếu chỉ là câu hỏi hỏi giá, tư vấn lựa chọn gói cước dịch vụ thông thường, hãy đặt escalation_required là false để AI tự động trả lời khách hàng."
)

REASONING_SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Lập luận Hỗ trợ (Reasoning Agent).\n"
    "Nhiệm vụ: Dựa trên thông tin Ticket, Quyết định của Supervisor, và Tài liệu tri thức RAG được cung cấp, hãy lập luận từng bước để giải quyết vấn đề.\n"
    "Trả về kết quả định dạng JSON duy nhất:\n"
    "{\n"
    "  \"reasoning_steps\": [\n"
    "    \"Bước 1: <Phân tích thực tế lỗi từ thông tin khách hàng cung cấp>\",\n"
    "    \"Bước 2: <Đối chiếu các thông tin này với dữ liệu tri thức RAG tìm được>\",\n"
    "    \"Bước 3: <Xác định giải pháp hoặc quyết định xem có cần nhân sự xử lý thêm không>\"\n"
    "  ],\n"
    "  \"reasoning_output\": \"<Dự thảo chi tiết câu trả lời hoàn chỉnh dựa trên lập luận trên. LƯU Ý QUAN TRỌNG: TUYỆT ĐỐI không đề cập đến các từ khóa kỹ thuật nội bộ như 'RAG', 'tài liệu RAG', 'Qdrant', 'Vector DB', 'LLM', 'AI Agent', 'Supervisor', 'Prompt' trong phần này. Hãy viết câu trả lời tự nhiên, thân thiện và chuyên nghiệp đóng vai là nhân viên CSKH con người hỗ trợ khách hàng.>\"\n"
    "}"
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


def build_query_optimizer_messages(subject: str, content: str) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt gửi LLM để tối ưu hóa & mở rộng câu truy vấn."""
    return [
        {"role": "system", "content": QUERY_OPTIMIZER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Tiêu đề: {subject}\nNội dung: {content}"}
    ]


def build_supervisor_messages(subject: str, content: str, category: str, priority: str) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt gửi LLM để Agent Supervisor đưa ra quyết định điều phối."""
    user_content = (
        f"Thông tin Ticket:\n"
        f"- Tiêu đề: {subject}\n"
        f"- Nội dung: {content}\n"
        f"- Phân nhóm: {category}\n"
        f"- Độ ưu tiên: {priority}"
    )
    return [
        {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]


def build_reasoning_messages(
    subject: str,
    content: str,
    category: str,
    priority: str,
    context_str: str,
    supervisor_decision: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Tạo bộ tin nhắn Prompt gửi LLM để thực hiện suy luận lập luận giải quyết Ticket."""
    user_content = (
        f"Thông tin Ticket:\n"
        f"- Tiêu đề: {subject}\n"
        f"- Nội dung: {content}\n"
        f"- Phân nhóm: {category}\n"
        f"- Độ ưu tiên: {priority}\n\n"
        f"Quyết định điều phối của Supervisor:\n"
        f"- Phân tích: {supervisor_decision.get('reasoning', 'Không có')}\n"
        f"- Phong cách phản hồi: {supervisor_decision.get('response_style', 'formal')}\n"
        f"- Độ sâu lập luận: {supervisor_decision.get('reasoning_depth', 'shallow')}\n\n"
        f"Tài liệu tri thức RAG tham khảo:\n{context_str}\n\n"
        f"Hãy lập luận từng bước để chuẩn bị câu trả lời."
    )
    return [
        {"role": "system", "content": REASONING_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]


