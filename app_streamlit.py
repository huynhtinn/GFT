import streamlit as st
import json
from datetime import datetime
from app.graph.builder import support_agent_graph
from app.services.qdrant_service import qdrant_kb
from app.config.settings import settings
import os
# Cấu hình Trang Streamlit
st.set_page_config(
    page_title="Hệ Thống Hỗ Trợ Tự Vận Hành — LangGraph & Qdrant",
    # page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, p, span, label, button, input, textarea, select {
    font-family: 'Outfit', sans-serif;
}

/* Customize Radio Buttons in Sidebar (Theme Adaptive Pills) */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    padding: 6px 0 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 12px 16px !important;
    border-radius: 14px !important;
    background-color: var(--secondary-background-color, rgba(99, 102, 241, 0.06)) !important;
    color: var(--text-color, inherit) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    margin: 0 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
    font-size: 14px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    color: inherit !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background-color: rgba(99, 102, 241, 0.15) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked),
div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
    background: #2563eb !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    border-color: #2563eb !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
    color: #ffffff !important;
}

/* User Sidebar Profile Card */
.user-sidebar-card {
    background: var(--secondary-background-color, rgba(99, 102, 241, 0.08));
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.user-role-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78em;
    font-weight: 700;
    background: rgba(37, 99, 235, 0.15);
    color: #2563eb;
    border: 1px solid rgba(37, 99, 235, 0.3);
}

/* Metric Cards */
div[data-testid="stMetric"] {
    background: var(--secondary-background-color, rgba(99, 102, 241, 0.05));
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #6366f1;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
}
div[data-testid="stMetric"] label {
    font-size: 0.9em !important;
    font-weight: 600 !important;
    opacity: 0.85;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 1.8em !important;
    font-weight: 800 !important;
    color: var(--text-color, inherit) !important;
}

/* Expanders & Tabs */
details {
    border: 1px solid rgba(148, 163, 184, 0.25) !important;
    border-radius: 14px !important;
    background: var(--secondary-background-color, rgba(255, 255, 255, 0.02)) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    margin-top: 8px;
}
summary {
    font-weight: 600 !important;
    color: var(--text-color, inherit) !important;
}
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.95em !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #4f46e5 !important;
}

/* Titles and Headers */
h1 {
    background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}
h2, h3, h4 {
    color: var(--text-color, inherit) !important;
    font-weight: 700 !important;
}

/* Styled Badges */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.88em;
    font-weight: 700;
    text-align: center;
    border: 1px solid transparent;
}
.badge-auto {
    background: rgba(34, 197, 94, 0.15);
    color: #16a34a;
    border-color: rgba(34, 197, 94, 0.3);
}
.badge-human {
    background: rgba(239, 68, 68, 0.15);
    color: #dc2626;
    border-color: rgba(239, 68, 68, 0.3);
}
.badge-clarify {
    background: rgba(234, 179, 8, 0.15);
    color: #d97706;
    border-color: rgba(234, 179, 8, 0.3);
}
.badge-spam {
    background: rgba(107, 114, 128, 0.15);
    color: #4b5563;
    border-color: rgba(107, 114, 128, 0.3);
}

.citation-card {
    background: var(--secondary-background-color, rgba(99, 102, 241, 0.05));
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-left: 4px solid #6366f1;
    padding: 14px 18px;
    border-radius: 12px;
    margin-top: 10px;
    color: var(--text-color, inherit);
}
.citation-title {
    color: var(--primary-color, #6366f1) !important;
    font-weight: 700;
}
.citation-meta {
    color: var(--text-color, inherit) !important;
    opacity: 0.65;
    font-style: italic;
}
.citation-snippet {
    color: var(--text-color, inherit) !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

.log-step {
    border-left: 3px solid #6366f1;
    padding-left: 12px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

from app.services.auth_service import auth_service

# Khởi tạo Session State cho User & Tickets (Lưu trữ bền vững trên SQLite DB)
if "tickets_db" not in st.session_state:
    st.session_state["tickets_db"] = auth_service.load_all_tickets()
if "user" not in st.session_state:
    st.session_state["user"] = None


# GIAO DIỆN XÁC THỰC ĐĂNG NHẬP / ĐĂNG KÝ (NẾU CHƯA ĐĂNG NHẬP)
if not st.session_state["user"]:
    st.title("Đăng Nhập / Đăng Ký")
    st.caption("Vui lòng đăng nhập hoặc đăng ký tài khoản để trải nghiệm ứng dụng Tổng đài Hỗ trợ Multi-Agent.")

    tab_login, tab_register = st.tabs(["Đăng Nhập", "Đăng Ký Tài Khoản Mới"])

    with tab_login:
        st.markdown("### Đăng Nhập Nhanh Với Tài Khoản Demo")
        c_demo1, c_demo2 = st.columns(2)
        if c_demo1.button("Admin / Nhân Sự (`admin` / `123`)", use_container_width=True):
            user = auth_service.authenticate_user("admin", "123")
            if user:
                st.session_state["user"] = user
                st.rerun()
        if c_demo2.button("Khách hàng (`customer` / `123`)", use_container_width=True):
            user = auth_service.authenticate_user("customer", "123")
            if user:
                st.session_state["user"] = user
                st.rerun()

        st.markdown("---")
        with st.form("login_form"):
            login_username = st.text_input("Tên đăng nhập")
            login_password = st.text_input("Mật khẩu", type="password")
            login_submit = st.form_submit_button("Đăng Nhập", type="primary", use_container_width=True)

        if login_submit:
            user = auth_service.authenticate_user(login_username, login_password)
            if user:
                st.session_state["user"] = user
                st.success(f"Xin chào **{user['full_name']}**! Đăng nhập thành công.")
                st.rerun()
            else:
                st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

    with tab_register:
        with st.form("register_form"):
            reg_username = st.text_input("Tên đăng nhập mới (VD: user123)")
            reg_password = st.text_input("Mật khẩu mới", type="password")
            reg_email = st.text_input("Email liên hệ", value="user123@gmail.com")
            reg_fullname = st.text_input("Họ và tên hiển thị", value="Nguyễn Văn User")
            reg_role = st.selectbox("Vai trò tài khoản", ["Khách hàng (customer)", "Nhân sự hỗ trợ / Admin (admin)"])
            
            reg_submit = st.form_submit_button("Đăng Ký Tài Khoản Mới", type="primary", use_container_width=True)

        if reg_submit:
            role_code = "admin" if "admin" in reg_role.lower() else "customer"
            res = auth_service.register_user(
                username=reg_username,
                password=reg_password,
                email=reg_email,
                full_name=reg_fullname,
                role=role_code
            )
            if res["success"]:
                st.success(f" {res['message']} Vui lòng chuyển qua tab Đăng Nhập để vào hệ thống.")
            else:
                st.error(f" {res['message']}")

    st.stop()

# ── SIDEBAR NAVIGATION ────────────────────────────────────────────────
current_user = st.session_state.get("user")
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>TỔNG ĐÀI HỖ TRỢ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.85em; opacity: 0.85; margin-top: 2px;'>Tổng Đài Hỗ Trợ Tự Vận Hành</p>", unsafe_allow_html=True)
    st.divider()

    if current_user:
        role_label = "Quản Trị Viên / Admin" if current_user.get("role") == "admin" else "Khách Hàng (Customer)"
        st.markdown(f"""
        <div class="user-sidebar-card">
            <div style="font-size: 0.78em; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.75;">Xin chào</div>
            <div style="font-size: 1.15em; font-weight: 700; color: #4f46e5; margin: 2px 0;"> {current_user.get('full_name')}</div>
            <div style="font-size: 0.82em; opacity: 0.85; word-break: break-all;"> {current_user.get('email')}</div>
            <div style="margin-top: 8px;">
                <span class="user-role-badge">{role_label}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Đăng Xuất", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()
        st.divider()


    # Phân quyền menu theo vai trò người dùng (Admin vs Customer)
    user_role = current_user.get("role", "customer") if current_user else "customer"
    if user_role == "admin":
        available_pages = [
            "Tiếp Nhận Ticket",
            "Giao Diện Nhân Sự",
            "Tra Cứu Tri Thức"
        ]
    else:
        available_pages = [
            "Tiếp Nhận Ticket"
        ]

    page = st.radio("Navigation", available_pages, label_visibility="collapsed")



    st.divider()
    

# -----------------------------------------------------------------------------
# TAB 1: TIẾP NHẬN TICKET & MULTI-AGENT PIPELINE
# -----------------------------------------------------------------------------
if "Tiếp Nhận Ticket" in page:
    st.title(" Tiếp Nhận Yêu Cầu")
    
    st.markdown("### Kịch Bản Mẫu")
    
    # Khởi tạo dữ liệu kịch bản mặc định trong Session State
    if "active_preset" not in st.session_state:
        st.session_state["active_preset"] = {
            "name": "Nguyễn Văn A",
            "email": "khachhang@gmail.com",
            "channel": "web",
            "subject": "Hỏi về bảng giá gói Enterprise",
            "content": "Cho tôi xin thông tin bảng giá dịch vụ gói Enterprise."
        }

    # Hàng 1
    col_r1_1, col_r1_2, col_r1_3, col_r1_4, col_r1_5, col_r1_6 = st.columns(6)
    
    if col_r1_1.button("FAQ Giá Cước", use_container_width=True, help="Tư vấn gói cước Standard và Premium"):
        st.session_state["active_preset"] = {
            "name": "Nguyễn Văn A",
            "email": "nva@company.com",
            "channel": "web",
            "subject": "Tư vấn lựa chọn gói cước và cam kết SLA",
            "content": "Công ty chúng tôi là startup, trung bình phát sinh khoảng 300 ticket hỗ trợ mỗi tháng. Chúng tôi nên chọn gói cước nào phù hợp, chi phí bao nhiêu và có cam kết thời gian phản hồi không?"
        }
        st.rerun()

    if col_r1_2.button("Lỗi API 403", use_container_width=True, help="Lỗi HTTP 403 Forbidden khi Gọi API"):
        st.session_state["active_preset"] = {
            "name": "Trần Thị B",
            "email": "dev@partner.com",
            "channel": "email",
            "subject": "Lỗi 403 Forbidden khi kết nối API tạo đơn hàng",
            "content": "Chào đội ngũ hỗ trợ. Khi tôi gọi API tới endpoint /v1/orders thì nhận về mã lỗi HTTP 403 Forbidden liên tục từ sáng nay. API Key vẫn đang hoạt động. Nhờ kiểm tra giúp."
        }
        st.rerun()

    if col_r1_3.button("Sự Cố P0 Sập DB", use_container_width=True, help="Sự cố P0 khẩn cấp mất kết nối Database"):
        st.session_state["active_preset"] = {
            "name": "Lê Văn C",
            "email": "admin@client.com",
            "channel": "internal",
            "subject": "KHẨN CẤP P0: Toàn bộ hệ thống API báo lỗi 500 và sập kết nối Database",
            "content": "Toàn bộ hệ thống production bị sập không thể kết nối. Khách hàng của chúng tôi không thể thanh toán hay tạo đơn, log báo lỗi sập database hoặc rò rỉ kết nối nghiêm trọng. Yêu cầu xử lý khẩn cấp!"
        }
        st.rerun()

    if col_r1_4.button("Đòi Hoàn Tiền 2 Lần", use_container_width=True, help="Yêu cầu hoàn tiền do Double Billing"):
        st.session_state["active_preset"] = {
            "name": "Phạm Thị D",
            "email": "dpham@gmail.com",
            "channel": "zalo",
            "subject": "Bức xúc bị trừ tiền 2 lần trên hóa đơn tháng 7",
            "content": "Hệ thống của các bạn tự động trừ tiền 2 lần cho cùng một gói Standard trong chu kỳ thanh toán tháng 7 này trên tài khoản ví của tôi. Yêu cầu hoàn tiền gấp, dịch vụ làm ăn quá thiếu chuyên nghiệp!"
        }
        st.rerun()

    if col_r1_5.button("Spam / Rác", use_container_width=True, help="Tin nhắn quảng cáo rác"):
        st.session_state["active_preset"] = {
            "name": "Bot Spammer",
            "email": "scam@crypto.io",
            "channel": "web",
            "subject": "Cheap sale crypto trading robot 100% profit click here",
            "content": "Invest in our bitcoin trading robot now for free crypto loans and 1000% daily profit! Guaranteed return on investment. Click here to register: http://spam-scam-link.xyz"
        }
        st.rerun()

    if col_r1_6.button("Hoàn FlashSale", use_container_width=True, help="Từ chối hoàn tiền gói khuyến mãi đặc biệt"):
        st.session_state["active_preset"] = {
            "name": "Hoàng Văn E",
            "email": "hve@gmail.com",
            "channel": "email",
            "subject": "Muốn hoàn tiền mua gói Standard trong đợt khuyến mãi Flash Sale",
            "content": "Tháng trước tôi có mua gói Standard theo chương trình Flash Sale giảm giá 50%. Nay tôi không dùng hết nhu cầu nên muốn hủy dịch vụ và yêu cầu hoàn trả lại số tiền còn thừa của những ngày chưa sử dụng."
        }
        st.rerun()

    # Hàng 2
    col_r2_1, col_r2_2, col_r2_3, col_r2_4, col_r2_5, col_r2_6 = st.columns(6)

    if col_r2_1.button("Cam Kết SLA", use_container_width=True, help="Chính sách SLA phản hồi và khắc phục"):
        st.session_state["active_preset"] = {
            "name": "Vũ Minh F",
            "email": "vmf@enterprise.vn",
            "channel": "web",
            "subject": "Thời gian tối đa để khắc phục lỗi P1 và P2 theo cam kết SLA?",
            "content": "Cho hỏi nếu hệ thống tích hợp của chúng tôi gặp sự cố nghiêm trọng (mức P1 hoặc P2) do lỗi hệ thống của các bạn, thì thời gian tối đa để các bạn khắc phục xong hoàn toàn và đưa dịch vụ hoạt động bình thường là bao lâu?"
        }
        st.rerun()

    if col_r2_2.button("Webhook Zalo", use_container_width=True, help="Xác thực chữ ký Webhook Zalo ZNS"):
        st.session_state["active_preset"] = {
            "name": "Đỗ Thị G",
            "email": "gdo@techcorp.com",
            "channel": "web",
            "subject": "Cách kiểm tra chữ ký signature của Webhook Zalo ZNS",
            "content": "Tôi đang tích hợp webhook để nhận trạng thái tin nhắn ZNS gửi từ hệ thống của các bạn. Làm sao để xác thực chữ ký (signature) đính kèm trong header của payload để đảm bảo an toàn, tránh tin tặc giả mạo?"
        }
        st.rerun()

    if col_r2_3.button("API Key Bị Lộ", use_container_width=True, help="Thu hồi và cấp lại API Key"):
        st.session_state["active_preset"] = {
            "name": "Ngô Văn H",
            "email": "hngo@startup.io",
            "channel": "web",
            "subject": "API Key bị lộ trên kho lưu trữ công khai GitHub",
            "content": "Chào hỗ trợ, lập trình viên của bên tôi vô tình đẩy source code chứa API Key của production lên GitHub công khai. Bây giờ tôi cần thu hồi key này ngay lập tức và cấp lại key mới thì làm thế nào?"
        }
        st.rerun()

    if col_r2_4.button("Lỗi API Timeout", use_container_width=True, help="Yêu cầu làm rõ thông tin sự cố kết nối"):
        st.session_state["active_preset"] = {
            "name": "Phan Văn I",
            "email": "iphan@dev.net",
            "channel": "email",
            "subject": "Lỗi kết nối timeout khi gọi dịch vụ",
            "content": "Hệ thống của tôi liên tục bị lỗi timeout khi kết nối sang bên các bạn. Nhờ kiểm tra giùm."
        }
        st.rerun()

    if col_r2_5.button("Bồi Thường SLA", use_container_width=True, help="Yêu cầu bồi thường do vi phạm SLA"):
        st.session_state["active_preset"] = {
            "name": "Bùi Thị K",
            "email": "kby@corporation.com",
            "channel": "email",
            "subject": "Yêu cầu bồi thường thiệt hại do gián đoạn dịch vụ hơn 48 giờ liên tiếp",
            "content": "Vào tuần trước, hệ thống API của các bạn bị mất kết nối liên tục từ ngày 20/07 đến 23/07 khiến chúng tôi không thể bán hàng cho khách. Thời gian gián đoạn vượt quá 48 giờ quy định. Yêu cầu bồi thường thiệt hại thực tế theo quy trình bồi thường SLA."
        }
        st.rerun()

    if col_r2_6.button("Onboarding Mới", use_container_width=True, help="Hướng dẫn các bước thiết lập tài khoản mới"):
        st.session_state["active_preset"] = {
            "name": "Lâm Văn L",
            "email": "llam@newbiz.com",
            "channel": "web",
            "subject": "Hướng dẫn các bước khởi đầu (onboarding) cho thành viên mới",
            "content": "Tôi vừa đăng ký tài khoản doanh nghiệp thành công trên hệ thống. Xin hỏi các bước tiếp theo cần phải thiết lập và làm những gì để có thể kết nối thử nghiệm dịch vụ của bên các bạn?"
        }
        st.rerun()

    preset = st.session_state["active_preset"]
    user_name_default = current_user.get("full_name") if current_user else preset["name"]
    user_email_default = current_user.get("email") if current_user else preset["email"]

    is_admin_mode = (user_role == "admin")

    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Tên khách hàng (Đã xác thực)", value=user_name_default, disabled=bool(current_user), help="Tự động lấy theo tài khoản đăng nhập")
            customer_email = st.text_input("Email liên hệ (Đã xác thực)", value=user_email_default, disabled=bool(current_user), help="Tự động lấy theo tài khoản đăng nhập")
            if is_admin_mode:
                channel_options = ["internal"]
                channel_idx = 0
            else:
                channel_options = ["web", "email", "zalo"]
                channel_idx = channel_options.index(preset["channel"]) if preset["channel"] in channel_options else 0
            channel = st.selectbox("Kênh tiếp nhận", channel_options, index=channel_idx, disabled=is_admin_mode)
        with col2:
            subject = st.text_input("Tiêu đề yêu cầu", value=preset["subject"])
            content = st.text_area("Nội dung yêu cầu chi tiết", value=preset["content"], height=110)
        
        submitted = st.form_submit_button("Gửi Yêu Cầu & Thực Thi", type="primary", use_container_width=True)



    if submitted:
        ticket_id = f"TCK-{hash(datetime.now().isoformat()) % 9000 + 1000}"
        
        initial_state = {
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "channel": channel,
            "subject": subject,
            "content": content,
            "status": "NEW",
            "cohere_api_key": st.session_state.get("cohere_api_key", ""),
            "pipeline_logs": []
        }

        with st.spinner("Hệ thống đang thực thi luồng xử lý..."):
            config = {"configurable": {"thread_id": ticket_id}}
            final_state = support_agent_graph.invoke(initial_state, config=config)

        # Lưu vào Session State DB & Lưu bền vững vào SQLite user.db
        ticket_item = {
            "id": ticket_id,
            "customerName": customer_name,
            "customerEmail": customer_email,
            "channel": channel,
            "subject": subject,
            "content": content,
            "category": final_state.get("category", "faq"),
            "priority": final_state.get("priority", "P3_LOW"),
            "status": final_state.get("status", "NEW"),
            "confidenceScore": final_state.get("confidence_score", 0.0),
            "citations": final_state.get("citations", []),
            "aiAnswer": final_state.get("ai_answer"),
            "clarificationQuestion": final_state.get("clarification_question"),
            "missingSlots": final_state.get("missing_slots"),
            "contextPackage": final_state.get("context_package"),
            "logs": final_state.get("pipeline_logs", []),
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.session_state["tickets_db"][ticket_id] = ticket_item
        auth_service.save_ticket(ticket_item)

        st.success(f"Đã xử lý xong Ticket mã **[{ticket_id}]**!")

        
        # Hiển thị Kết quả Xử lý
        st.markdown("---")
        st.markdown("### Kết Quả Phân Tích & Phản Hồi Từ AI Agent")
        
        status = final_state.get("status")
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.metric("Mã Ticket", ticket_id)
            st.write(f"**Nhóm (Category):** `{final_state.get('category', 'N/A').upper()}`")
        with col_res2:
            st.metric("Độ Ưu Tiên", final_state.get('priority', 'N/A'))
            st.write(f"**Confidence Score:** `{final_state.get('confidence_score', 0.0)}%`")
        with col_res3:
            if status == "RESOLVED_AUTO":
                st.markdown('<span class="badge badge-auto">RESOLVED_AUTO (Tự động trả lời)</span>', unsafe_allow_html=True)
            elif status == "ESCALATED_HUMAN":
                st.markdown('<span class="badge badge-human">ESCALATED_HUMAN (Chuyển Nhân sự)</span>', unsafe_allow_html=True)
            elif status == "CLARIFICATION_SENT":
                st.markdown('<span class="badge badge-clarify">CLARIFICATION_SENT (Chờ làm rõ)</span>', unsafe_allow_html=True)
            elif status == "SPAM_CLOSED":
                st.markdown('<span class="badge badge-spam">SPAM_CLOSED (Đã đóng Ticket rác)</span>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Nếu là Admin, hiển thị đầy đủ thông tin điều phối và tối ưu hóa truy vấn
        if is_admin_mode:
            if final_state.get("supervisor_decision") or final_state.get("rewritten_query"):
                st.markdown("#### 🧭 Bộ Điều Phối & Tối Ưu Truy Vấn")
                col_opt1, col_opt2 = st.columns(2)
                with col_opt1:
                    dec = final_state.get("supervisor_decision", {})
                    if dec:
                        st.markdown(f"""
                        <div style="background: rgba(99, 102, 241, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.15);">
                            <strong style="color: #6366f1;">Supervisor Agent decisions:</strong><br>
                            • Phong cách: <code>{dec.get('response_style', 'N/A').upper()}</code><br>
                            • Độ sâu lập luận: <code>{dec.get('reasoning_depth', 'N/A').upper()}</code><br>
                            • Yêu cầu chuyển người: <code>{str(dec.get('escalation_required', False)).upper()}</code><br>
                            • Lập luận: <span style="font-size: 0.9em; opacity: 0.85;">{dec.get('reasoning', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                with col_opt2:
                    rewritten = final_state.get("rewritten_query")
                    exp = final_state.get("expanded_queries", [])
                    if rewritten:
                        exp_html = "<br>".join([f"&nbsp;&nbsp;+ <code>'{q}'</code>" for q in exp]) if exp else "&nbsp;&nbsp;Không có"
                        st.markdown(f"""
                        <div style="background: rgba(59, 130, 246, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.15);">
                            <strong style="color: #3b82f6;">Query Optimizer & Expander:</strong><br>
                            • Truy vấn viết lại: <code>"{rewritten}"</code><br>
                            • Truy vấn mở rộng:<br>
                            {exp_html}
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

        # Lập luận hệ thống CoT
        reasoning_trace = final_state.get("reasoning_trace", [])
        if reasoning_trace:
            with st.expander("🔬 Quá Trình Lập Luận Hệ Thống (Chain-of-Thought reasoning)", expanded=True):
                for step in reasoning_trace:
                    st.markdown(f"**{step}**")
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Phản hồi chi tiết
        if final_state.get("ai_answer"):
            st.info(f"**Câu Phản Hồi Tự Động:**\n\n{final_state.get('ai_answer')}")
        
        if final_state.get("clarification_question"):
            st.warning(f"**Câu Hỏi Tự Động Làm Rõ Thông Tin:**\n\n{final_state.get('clarification_question')}")

        # Nếu là Admin, hiển thị Trích Dẫn Tri Thức Dẫn Nguồn
        if is_admin_mode:
            citations = final_state.get("citations", [])
            if citations:
                st.markdown("#### Trích Dẫn Tri Thức Dẫn Nguồn (Qdrant Grounding Citations):")
                for c in citations:
                    st.markdown(f"""
                    <div class="citation-card">
                        <strong class="citation-title">[{c.get('docId')}] {c.get('docTitle')}</strong> — <em class="citation-meta">Mục: {c.get('section')} (Độ tương đồng: {round(c.get('relevanceScore', 0)*100, 1)}%)</em><br>
                        <code class="citation-snippet">"{c.get('snippet')}"</code>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Logs chi tiết
        st.markdown("---")
        with st.expander("Xem Chi Tiết Nhật Ký Xử Lý Multi-Agent (Pipeline Audit Logs)", expanded=True):
            logs = final_state.get("pipeline_logs", [])
            for log in logs:
                st.markdown(f"""
                <div class="log-step">
                    <strong style="color: #818cf8;">[{log.get('stepName')}]</strong> — <span style="color: #94a3b8;">{log.get('timestamp')}</span><br>
                    Status: <code style="color: #38bdf8;">{log.get('status').upper()}</code> | Chi tiết: {log.get('detail')}
                </div>
                """, unsafe_allow_html=True)

    # ── PHẦN TRA CỨU LỊCH SỬ TICKET & CÂU TRẢ LỜI CỦA NHÂN SỰ DÀNH CHO KHÁCH HÀNG ──
    st.markdown("---")
    st.markdown("### Lịch Sử Ticket & Kết Quả Phản Hồi Của Bạn")
    st.caption("Theo dõi tiến độ xử lý và xem trực tiếp câu trả lời do Nhân sự CSKH đã duyệt.")

    user_email = current_user.get("email") if current_user else ""
    user_fullname = current_user.get("full_name") if current_user else ""

    user_tickets = [
        t for t in st.session_state["tickets_db"].values()
        if (user_email and t.get("customerEmail") == user_email) or (user_fullname and t.get("customerName") == user_fullname)
    ]

    if not user_tickets:
        st.info("Bạn chưa gửi ticket nào. Hãy gửi yêu cầu ở trên để hệ thống ghi nhận và theo dõi tiến độ.")
    else:
        for tk in reversed(user_tickets):
            status_code = tk.get("status")
            with st.expander(f"Ticket [{tk['id']}] — {tk['subject']} ({tk.get('createdAt', '')})", expanded=(status_code in ["RESOLVED_HUMAN", "RESOLVED_AUTO"])):
                c_info1, c_info2 = st.columns(2)
                with c_info1:
                    st.write(f"**Mã Ticket:** `{tk['id']}`")
                    st.write(f"**Kênh gửi:** `{tk.get('channel', 'web')}`")
                with c_info2:
                    if status_code == "RESOLVED_AUTO":
                        st.markdown('<span class="badge badge-auto">RESOLVED_AUTO (AI Tự Động Trả Lời)</span>', unsafe_allow_html=True)
                    elif status_code == "RESOLVED_HUMAN":
                        st.markdown('<span class="badge badge-auto" style="background:#0284c7; color:#fff;">RESOLVED_HUMAN (Nhân Sự Đã Phản Hồi)</span>', unsafe_allow_html=True)
                    elif status_code == "ESCALATED_HUMAN":
                        st.markdown('<span class="badge badge-human">ESCALATED_HUMAN (Đang Chờ Nhân Sự Duyệt)</span>', unsafe_allow_html=True)
                    elif status_code == "CLARIFICATION_SENT":
                        st.markdown('<span class="badge badge-spam">CLARIFICATION_SENT (Cần Bổ Sung Thông Tin)</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'`{status_code}`')

                st.markdown("**Nội dung yêu cầu:**")
                st.info(tk.get("content", ""))

                st.markdown("---")
                if status_code == "RESOLVED_HUMAN":
                    st.markdown("#### Câu Trả Lời Trực Tiếp Từ Nhân Sự CSKH:")
                    st.success(tk.get("aiAnswer", "Chưa có nội dung phản hồi."))
                    if tk.get("resolvedAt"):
                        st.caption(f"Thời gian nhân sự phê duyệt & phản hồi: {tk.get('resolvedAt')}")
                elif status_code == "RESOLVED_AUTO":
                    # Trích xuất reasoning_trace và rewritten_query từ logs nếu không có trực tiếp
                    r_trace = tk.get("reasoningTrace", [])
                    r_query = tk.get("rewrittenQuery")
                    s_dec = tk.get("supervisorDecision")
                    if not r_trace or not r_query:
                        for log in tk.get("logs", []):
                            if log.get("stepId") == "step_reasoning":
                                r_trace = log.get("data", {}).get("reasoning_steps", [])
                            if log.get("stepId") == "step_optimizer":
                                r_query = log.get("data", {}).get("rewritten_query")
                            if log.get("stepId") == "step_supervisor":
                                s_dec = log.get("data", {}).get("decision")

                    if user_role == "admin" and (s_dec or r_query):
                        st.markdown("**Bộ tối ưu & Điều phối:**")
                        col_hist1, col_hist2 = st.columns(2)
                        with col_hist1:
                            if s_dec:
                                st.markdown(f"• Phong cách: `{s_dec.get('response_style')}` | Lập luận: {s_dec.get('reasoning')}")
                        with col_hist2:
                            if r_query:
                                st.markdown(f"• Truy vấn tối ưu: `{r_query}`")

                    if r_trace:
                        with st.expander("🔬 Vết suy luận của AI (Reasoning Trace)", expanded=False):
                            for step in r_trace:
                                st.markdown(f"- {step}")

                    st.markdown("#### Câu Trả Lời Từ Trợ Lý AI Agent:")
                    st.success(tk.get("aiAnswer", "Chưa có nội dung phản hồi."))
                elif status_code == "CLARIFICATION_SENT":
                    st.markdown("#### Yêu Cầu Bổ Sung Thông Tin:")
                    st.warning(tk.get("clarificationQuestion", "Vui lòng cung cấp thêm thông tin."))
                elif status_code == "ESCALATED_HUMAN":
                    st.warning("**Yêu cầu đang nằm trong hàng chờ:** Ticket của bạn đã được gửi tới Nhân sự CSKH. Vui lòng quay lại kiểm tra câu trả lời tại đây sau ít phút!")


# -----------------------------------------------------------------------------
# TAB 2: GIAO DIỆN NHÂN SỰ 
# -----------------------------------------------------------------------------
elif "Giao Diện Nhân Sự" in page:
    st.title("Workspace Nhân Sự")
    st.caption("Hòm thư xử lý và phê duyệt dành cho Nhân sự hỗ trợ.")
    
    st.markdown("### 📥 Hàng Chờ Phê Duyệt Ticket (Escalations Queue)")
    escalated_tickets = [t for t in st.session_state["tickets_db"].values() if t.get("status") == "ESCALATED_HUMAN"]
    
    if not escalated_tickets:
        st.info("Hiện không có Ticket nào cần con người can thiệp trong Workspace Nhân sự.")
    else:
        st.warning(f"Đang có **{len(escalated_tickets)}** ticket cần nhân sự kiểm tra và phê duyệt.")
        
        selected_ticket_id = st.selectbox("Chọn Ticket cần duyệt:", [t["id"] for t in escalated_tickets])
        ticket = next(t for t in escalated_tickets if t["id"] == selected_ticket_id)
        
        st.markdown("---")
        col_t1, col_t2 = st.columns([1, 1])
        
        with col_t1:
            st.markdown(f"### Thông Tin Ticket `[{ticket['id']}]`")
            st.write(f"**Khách hàng:** {ticket['customerName']} ({ticket['customerEmail']})")
            st.write(f"**Kênh:** `{ticket['channel']}` | **Độ ưu tiên:** `{ticket['priority']}`")
            st.write(f"**Tiêu đề:** {ticket['subject']}")
            st.text_area("Nội dung yêu cầu từ khách", ticket['content'], height=130, disabled=True)
        
        with col_t2:
            st.markdown("### AI Context Briefing Package")
            pkg = ticket.get("contextPackage") or {}
            if pkg:
                st.markdown(f"**Tóm tắt:** {pkg.get('summary')}")
                st.markdown(f"**Thái độ (Sentiment):** `{pkg.get('sentiment')}`")
                st.markdown(f"**Hành động đề xuất:** `{pkg.get('recommendedAction')}`")
                st.markdown(f"**Lý do chuyển giao:** {pkg.get('escalationReason')}")
                st.markdown("**Các bước AI đã xử lý:**")
                for step in pkg.get("triedSteps", []):
                    st.markdown(f"- {step}")
            else:
                st.write("Chưa có gói briefing.")

        # Hiển thị đầy đủ thông tin phân tích AI cho Nhân sự duyệt
        st.markdown("---")
        st.markdown("### 🔍 Phân Tích Chi Tiết Từ AI Agent")
        
        # Trích xuất dữ liệu từ ticket logs
        r_trace = ticket.get("reasoningTrace", [])
        r_query = ticket.get("rewrittenQuery")
        s_dec = ticket.get("supervisorDecision")
        if not r_trace or not r_query:
            for log in ticket.get("logs", []):
                if log.get("stepId") == "step_reasoning":
                    r_trace = log.get("data", {}).get("reasoning_steps", [])
                if log.get("stepId") == "step_optimizer":
                    r_query = log.get("data", {}).get("rewritten_query")
                if log.get("stepId") == "step_supervisor":
                    s_dec = log.get("data", {}).get("decision")
        
        col_an1, col_an2 = st.columns(2)
        with col_an1:
            if s_dec:
                st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.15);">
                    <strong style="color: #6366f1;">Supervisor Agent decisions:</strong><br>
                    • Phong cách: <code>{s_dec.get('response_style', 'N/A').upper()}</code><br>
                    • Yêu cầu chuyển người: <code>{str(s_dec.get('escalation_required', False)).upper()}</code><br>
                    • Lập luận: <span style="font-size: 0.9em; opacity: 0.85;">{s_dec.get('reasoning', '')}</span>
                </div>
                """, unsafe_allow_html=True)
        with col_an2:
            if r_query:
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.15);">
                    <strong style="color: #3b82f6;">Query Optimizer:</strong><br>
                    • Truy vấn tối ưu: <code>"{r_query}"</code>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if r_trace:
            with st.expander("🔬 Vết suy luận của AI (Reasoning Trace)", expanded=False):
                for step in r_trace:
                    st.markdown(f"- {step}")
        
        citations = ticket.get("citations", [])
        if citations:
            with st.expander("📚 Trích Dẫn Tri Thức Dẫn Nguồn (Grounding Citations)", expanded=False):
                for c in citations:
                    st.markdown(f"""
                    <div class="citation-card">
                        <strong class="citation-title">[{c.get('docId')}] {c.get('docTitle')}</strong> — <em class="citation-meta">Mục: {c.get('section')} (Độ tương đồng: {round(c.get('relevanceScore', 0)*100, 1)}%)</em><br>
                        <code class="citation-snippet">"{c.get('snippet')}"</code>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Phê Duyệt & Chỉnh Sửa Câu Trả Lời Gửi Khách Hàng")
        
        default_reply = pkg.get("autoDraftResponse") if pkg else "Kính gửi [Tên khách hàng],\n\nNhân viên hỗ trợ đã tiếp nhận yêu cầu và xử lý thành công cho quý khách.\n\nTrân trọng,\n[Tên Nhân Sự]"
        
        # Tự động điền Tên khách hàng và Tên nhân sự vào bản nháp
        cust_name = ticket.get("customerName", "Quý khách")
        staff_name = current_user.get("full_name", "Nhân sự hỗ trợ") if current_user else "Nhân sự hỗ trợ"

        for ph in ["[Tên khách hàng]", "[Tên Khách Hàng]", "[Tên khách]", "[Tên Khách]"]:
            default_reply = default_reply.replace(ph, cust_name)

        for ph in ["[Tên nhân sự]", "[Tên Nhân sự]", "[Tên Nhân Sự]", "[Tên nhân viên]", "[Tên Nhân Viên]", "[Tên Nhân viên]", "[Tên Nhân sư]"]:
            default_reply = default_reply.replace(ph, staff_name)

        final_reply = st.text_area("Nội dung câu trả lời chính thức:", value=default_reply, height=140)

        
        if st.button("Phê Duyệt & Gửi Phản Hồi Cho Khách Hàng", type="primary", use_container_width=True):
            ticket["status"] = "RESOLVED_HUMAN"
            ticket["aiAnswer"] = final_reply
            ticket["resolvedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            auth_service.save_ticket(ticket)
            st.success(f"Đã phê duyệt và phản hồi cho Ticket [{ticket['id']}] thành công!")
            st.rerun()



# -----------------------------------------------------------------------------
# TAB 3: TRA CỨU TRI THỨC QDRANT KB
# -----------------------------------------------------------------------------
elif "Tra Cứu Tri Thức" in page:
    st.title("Tra Cứu Tri Thức Vector Database")

    st.caption("Quản lý và tra cứu ngữ nghĩa dữ liệu trong Qdrant Vector Collection.")
    
    tab_search, tab_add = st.tabs(["Tìm Kiếm Ngữ Nghĩa (RAG Search)", "Thêm Tài Liệu Mới"])
    
    with tab_search:
        search_query = st.text_input("Nhập câu hỏi hoặc từ khóa cần tìm kiếm ngữ nghĩa:", value="Chính sách hoàn tiền lỗi 403")
        top_k = st.slider("Số lượng kết quả (Top K):", 1, 5, 3)
        
        if st.button("Tra Cứu Vector Search", type="primary"):
            with st.spinner("Đang truy vấn Qdrant Vector Collection..."):
                citations = qdrant_kb.search_relevant_chunks(
                    search_query, 
                    limit=top_k, 
                    cohere_api_key=st.session_state.get("cohere_api_key", "")
                )
            
            st.markdown(f"#### Tìm thấy **{len(citations)}** đoạn tri thức tương đồng nhất:")
            for idx, c in enumerate(citations):
                st.markdown(f"""
                <div class="citation-card">
                    <strong class="citation-title">#{idx+1} [{c.get('docId')}] {c.get('docTitle')}</strong> — <em class="citation-meta">Mục: {c.get('section')} (Độ tương đồng: {round(c.get('relevanceScore', 0)*100, 1)}%)</em><br>
                    <p class="citation-snippet">{c.get('snippet')}</p>
                </div>
                """, unsafe_allow_html=True)
                
    with tab_add:
        sub_upload, sub_manual = st.tabs(["Upload File Tài Liệu", "Nhập Văn Bản Thủ Công"])

        with sub_upload:
            st.markdown("### Upload Nhiều Tệp Tài Liệu Tri Thức (.txt, .pdf, .docx)")
            uploaded_files = st.file_uploader(
                "Tải file tài liệu từ máy tính của bạn:",
                type=["txt", "pdf", "docx"],
                accept_multiple_files=True,
            )

            if uploaded_files:
                st.info(f"Đã chọn **{len(uploaded_files)}** tệp tài liệu để nạp.")
                
                c_opt1, c_opt2 = st.columns(2)
                with c_opt1:
                    batch_cat = st.selectbox("Chuyên mục chung cho các file", ["Thanh toán & Hóa đơn", "Kỹ thuật & Tích hợp", "Hỏi đáp Thông tin", "Quy trình Khẩn cấp"], key="batch_cat")
                with c_opt2:
                    batch_tags = st.text_input("Thẻ từ khóa chung (phân cách bằng dấu phẩy)", value="batch_upload, KB_doc", key="batch_tags")

                st.markdown("#### Danh sách tệp xem trước:")
                processed_docs = []
                for idx, file_obj in enumerate(uploaded_files):
                    file_title = os.path.splitext(file_obj.name)[0]
                    # Trích xuất văn bản từ file
                    raw_bytes = file_obj.getvalue()
                    file_text = ""
                    fname_lower = file_obj.name.lower()
                    if fname_lower.endswith(".json"):
                        try:
                            parsed_json = json.loads(raw_bytes.decode("utf-8"))
                            file_text = json.dumps(parsed_json, ensure_ascii=False, indent=2)
                        except Exception:
                            file_text = raw_bytes.decode("utf-8", errors="ignore")
                    elif fname_lower.endswith(".pdf"):
                        try:
                            import pypdf
                            reader = pypdf.PdfReader(file_obj)
                            file_text = "\n".join([page.extract_text() or "" for page in reader.pages])
                        except Exception:
                            file_text = raw_bytes.decode("utf-8", errors="ignore")
                    elif fname_lower.endswith(".docx"):
                        try:
                            import docx
                            doc = docx.Document(file_obj)
                            file_text = "\n".join([p.text for p in doc.paragraphs if p.text])
                        except Exception:
                            file_text = raw_bytes.decode("utf-8", errors="ignore")
                    else:
                        file_text = raw_bytes.decode("utf-8", errors="ignore")

                    processed_docs.append({
                        "filename": file_obj.name,
                        "title": file_title,
                        "content": file_text
                    })
                    
                    with st.expander(f"#{idx+1} {file_obj.name} ({round(file_obj.size/1024, 2)} KB)", expanded=(idx==0)):
                        st.text_area(f"Nội dung trích xuất ({file_obj.name})", value=file_text[:500] + ("..." if len(file_text) > 500 else ""), height=100, key=f"preview_{idx}")

                st.markdown("---")
                if st.button(f"Vectorize & Index Tất Cả {len(uploaded_files)} File Vào Qdrant DB", type="primary", use_container_width=True):
                    progress_bar = st.progress(0)
                    tags_list = [t.strip() for t in batch_tags.split(",") if t.strip()]
                    success_count = 0

                    for idx, doc in enumerate(processed_docs):
                        doc_id = f"KB-FILE-{hash(doc['title'] + str(idx)) % 9000 + 1000}"
                        qdrant_kb.upsert_document(
                            doc_id=doc_id,
                            title=doc['title'],
                            category=batch_cat,
                            content=doc['content'],
                            tags=tags_list
                        )
                        success_count += 1
                        progress_bar.progress((idx + 1) / len(processed_docs))

                    st.success(f"Đã nạp thành công tất cả **{success_count}/{len(uploaded_files)}** tài liệu vào Qdrant Vector DB!")


        with sub_manual:
            with st.form("add_kb_form"):
                doc_title = st.text_input("Tiêu đề tài liệu", "Hướng dẫn Cấu hình Webhook Zalo ZNS v3")
                doc_cat = st.selectbox("Chuyên mục", ["Thanh toán & Hóa đơn", "Kỹ thuật & Tích hợp", "Hỏi đáp Thông tin", "Quy trình Khẩn cấp"], key="man_cat")
                doc_tags = st.text_input("Thẻ từ khóa (phân cách bằng dấu phẩy)", "zalo, zns, webhook, api, v3", key="man_tags")
                doc_content = st.text_area("Nội dung tài liệu", "Cấu hình Zalo ZNS API v3 cần secret key và xác thực OAuth2 token. Thời gian timeout là 5 giây.", height=120)
                
                submit_kb = st.form_submit_button("Vectorize & Index vào Qdrant", type="primary", use_container_width=True)
                
            if submit_kb:
                doc_id = f"KB-CUST-{hash(doc_title) % 900 + 100}"
                tags_list = [t.strip() for t in doc_tags.split(",") if t.strip()]
                qdrant_kb.upsert_document(
                    doc_id=doc_id,
                    title=doc_title,
                    category=doc_cat,
                    content=doc_content,
                    tags=tags_list
                )
                st.success(f"Đã nạp và tạo Vector Index cho tài liệu mã **[{doc_id}]** vào Qdrant DB thành công!")
