# 📚 DỮ LIỆU MẪU VÀ TÀI LIỆU HỖ TRỢ (SAMPLE DATA & PRESETS)
## Autonomous Customer Support Agent System

---

## 1. CẤU TRÚC THƯ MỤC TRI THỨC (KNOWLEDGE BASE DỮ LIỆU MẪU)

Toàn bộ dữ liệu tri thức mẫu của hệ thống được lưu trữ trong thư mục `knowledge_base/` phân theo 4 chuyên mục nghiệp vụ chính:

```
knowledge_base/
├── billing/                                 # Chuyên mục Thanh toán & Hóa đơn
│   ├── chinh-sach-hoan-tien.txt            # Chính sách hủy dịch vụ và quy định hoàn tiền
│   ├── goi-cuoc-dich-vu.txt                # Chi tiết các gói Basic, Professional, Enterprise
│   └── hoa-don-va-thanh-toan.txt           # Hướng dẫn thanh toán, xuất hóa đơn VAT, double charge
│
├── emergency/                               # Chuyên mục Quy trình Khẩn cấp & Sự cố P0
│   ├── quy-trinh-leo-thang-boi-thuong.txt   # Quy trình khiếu nại và bồi thường thiệt hại
│   └── quy-trinh-xu-ly-su-co-p0.txt        # Quy trình ứng cứu sự cố sập hệ thống P0 24/7
│
├── faq/                                     # Chuyên mục Hỏi đáp Thông tin & SLA
│   ├── bao-cao-va-toi-uu-hieu-suat.txt      # Báo cáo hiệu suất CSAT, ART, FCR
│   ├── cam-ket-sla-dieu-khoan-dich-vu.txt  # Cam kết thời gian khắc phục sự cố P0/P1/P2
│   ├── cau-hoi-thuong-gap-tong-hop.txt      # FAQ tổng hợp câu hỏi thường gặp
│   ├── chinh-sach-bao-mat-quyen-rieng-tu.txt# Chính sách bảo mật dữ liệu khách hàng
│   └── huong-dan-onboarding-bat-dau.txt    # Hướng dẫn thiết lập tài khoản mới
│
└── technical/                               # Chuyên mục Kỹ thuật & Tích hợp API
    ├── huong-dan-tich-hop-api.txt           # RESTful API endpoints và mã lỗi
    ├── khac-phuc-su-co-ket-noi.txt          # Xử lý lỗi timeout và rò rỉ kết nối
    ├── quan-ly-api-key.txt                 # Hướng dẫn cấp lại API Key khi bị rò rỉ
    ├── tich-hop-webhook-zalo-zns.txt        # Hướng dẫn xác thực chữ ký signature Webhook
    └── xu-ly-loi-api-http.txt               # Giải thích nguyên nhân và khắc phục lỗi 403/500/503
```

---

## 2. DƠN VỊ AUTO-SEEDING TỰ ĐỘNG NẠP DỮ LIỆU
Hệ thống tích hợp cơ chế tự động quét tất cả 15 file `.txt` trên (`seed_initial_kb()`) khi khởi chạy. Dữ liệu được cắt đoạn ngữ nghĩa bằng `RecursiveCharacterTextSplitter` (800 ký tự / chunk, 150 ký tự overlap) và tạo index vector 384 dimensions lưu vào collection `knowledge_base` trong Qdrant Vector DB.

---

## 3. DANH SÁCH 12 KỊCH BẢN MẪU TÍCH HỢP TRÊN GIAO DIỆN (UI PRESETS)

Để hỗ trợ kiểm thử và demo nhanh, ứng dụng Streamlit được tích hợp 12 kịch bản test mẫu chia làm 2 nhóm đại diện cho các tính năng cốt lõi:

### Nhóm 1: Các Kịch Bản Kiểm Thử Phản Hồi Tự Động (Auto-Resolve & Semantic Search)

1. **FAQ Giá Cước**:
   * **Nội dung**: *"Công ty chúng tôi là startup, trung bình phát sinh khoảng 300 ticket hỗ trợ mỗi tháng. Chúng tôi nên chọn gói cước nào phù hợp, chi phí bao nhiêu và có cam kết thời gian phản hồi không?"*
   * **Kỳ vọng**: AI tự động trả lời tư vấn GÓI PROFESSIONAL (5.000.000 VNĐ/tháng) hoặc BASIC, trích dẫn chuẩn SLA phản hồi. Trạng thái `RESOLVED_AUTO`.

2. **Lỗi API 403 (Thiếu Thông Tin - Slot Loop)**:
   * **Nội dung**: *"Khi tôi gọi API tới endpoint /v1/orders thì nhận về mã lỗi HTTP 403 Forbidden liên tục từ sáng nay. API Key vẫn đang hoạt động. Nhờ kiểm tra giúp."*
   * **Kỳ vọng**: Slot Inspector phát hiện thiếu dữ liệu 4 ký tự cuối API Key & Client IP ➔ Trạng thái `CLARIFICATION_SENT`.

3. **Spam / Tin Rác (Spam Detection)**:
   * **Nội dung**: *"Invest in our bitcoin trading robot now for free crypto loans and 1000% daily profit! Guaranteed return on investment. Click here to register: http://spam-scam-link.xyz"*
   * **Kỳ vọng**: LLM Spam Inspector phát hiện quảng cáo rác ➔ Trạng thái `SPAM_CLOSED`.

4. **Cam Kết SLA (SLA Inquiry)**:
   * **Nội dung**: *"Cho hỏi nếu hệ thống tích hợp của chúng tôi gặp sự cố nghiêm trọng (mức P1 hoặc P2) do lỗi hệ thống của các bạn, thì thời gian tối đa để các bạn khắc phục xong hoàn toàn là bao lâu?"*
   * **Kỳ vọng**: Trích dẫn tài liệu SLA, trả lời tự động `RESOLVED_AUTO`.

5. **Webhook Zalo ZNS (Technical Query)**:
   * **Nội dung**: *"Tôi đang tích hợp webhook để nhận trạng thái tin nhắn ZNS gửi từ hệ thống của các bạn. Làm sao để xác thực chữ ký (signature) đính kèm trong header để tránh tin tặc?"*
   * **Kỳ vọng**: Trích dẫn tài liệu `tich-hop-webhook-zalo-zns.txt`, trả lời kỹ thuật tự động.

6. **API Key Bị Lộ (Security Procedure)**:
   * **Nội dung**: *"Chào hỗ trợ, lập trình viên của bên tôi vô tình đẩy source code chứa API Key của production lên GitHub công khai. Bây giờ tôi cần thu hồi key này ngay lập tức thì làm thế nào?"*
   * **Kỳ vọng**: Hướng dẫn quy trình thu hồi API Key khẩn cấp từ tài liệu kỹ thuật.

7. **Lỗi API Timeout (Network Connection)**:
   * **Nội dung**: *"Hệ thống của tôi liên tục bị lỗi timeout khi kết nối sang bên các bạn. Nhờ kiểm tra giùm."*
   * **Kỳ vọng**: Trích dẫn tài liệu khắc phục sự cố kết nối.

8. **Onboarding Mới (Onboarding Steps)**:
   * **Nội dung**: *"Hướng dẫn các bước khởi đầu (onboarding) cho thành viên mới thiết lập tài khoản dịch vụ."*
   * **Kỳ vọng**: Trích dẫn tài liệu onboarding hướng dẫn 4 bước thiết lập.

---

### Nhóm 2: Các Kịch Bản Kiểm Thử Chuyển Giao Nhân Sự (Guardrails & Human Escalations)

9. **Đòi Hoàn Tiền 2 Lần (Double Billing Refund)**:
   * **Nội dung**: *"Hệ thống của các bạn tự động trừ tiền 2 lần cho cùng một gói Standard trong chu kỳ thanh toán tháng 7 này trên tài khoản ví của tôi. Yêu cầu hoàn tiền gấp!"*
   * **Kỳ vọng**: Confidence Score cao (91.3%), nhưng Supervisor Agent & Guardrails Router nhận diện rủi ro tranh chấp tài chính `BILLING / P1_HIGH` ➔ Trạng thái `ESCALATED_HUMAN`. Tự động tạo AI Briefing Package cho Admin duyệt.

10. **Sự Cố P0 Sập DB (Critical Outage)**:
    * **Nội dung**: *"KHẨN CẤP P0: Toàn bộ hệ thống API báo lỗi 500 và sập kết nối Database. Khách hàng của chúng tôi không thể thanh toán hay tạo đơn!"*
    * **Kỳ vọng**: Nhận diện mức độ `P0_CRITICAL` ➔ Trạng thái `ESCALATED_HUMAN`. Cảnh báo ca trực DevOps ứng cứu khẩn cấp.

11. **Từ Chối Hoàn FlashSale (Policy Exception)**:
    * **Nội dung**: *"Tháng trước tôi có mua gói Standard theo chương trình Flash Sale giảm giá 50%. Nay tôi không dùng hết nhu cầu nên muốn hủy dịch vụ và yêu cầu hoàn trả lại số tiền còn thừa."*
    * **Kỳ vọng**: Đối chiếu điều khoản không hoàn tiền đợt Flash Sale ➔ Chuyển Nhân sự phê duyệt từ chối.

12. **Bồi Thường SLA (SLA Compensation Demand)**:
    * **Nội dung**: *"Vào tuần trước, hệ thống API bị mất kết nối hơn 48 giờ liên tiếp. Yêu cầu bồi thường thiệt hại thực tế theo quy trình bồi thường SLA."*
    * **Kỳ vọng**: Nhận diện yêu cầu bồi thường thiệt hại rủi ro cao ➔ Chuyển Nhân sự xử lý.
