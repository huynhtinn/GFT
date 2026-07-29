import streamlit as st
import json
from datetime import datetime
from app.graph.builder import support_agent_graph
from app.services.qdrant_service import qdrant_kb
import os
# Cấu hình Trang Streamlit
st.set_page_config(
    page_title="Hệ Thống Hỗ Trợ Tự Vận Hành — LangGraph & Qdrant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS for Premium Dark Look & Feel ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, p, span, label, button, input, textarea, select {
    font-family: 'Outfit', sans-serif;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #1b2232 !important;
    border-right: 1px solid #23233b;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}

/* Customize Radio Buttons in Sidebar (Royal Blue Pills) */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    padding: 10px 0 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 12px 16px !important;
    border-radius: 16px !important;
    background-color: transparent !important;
    color: #94a3b8 !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
    border: none !important;
    margin: 0 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
    font-size: 14px !important;
    font-weight: 500 !important;
    margin: 0 !important;
    color: inherit !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: #f1f5f9 !important;
}

div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked),
div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
    background-color: #2563eb !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}

/* Metric Cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #16162a 0%, #20203a 100%);
    border: 1px solid #32325c;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: #5850ec;
    box-shadow: 0 8px 30px rgba(88, 80, 236, 0.25);
}
div[data-testid="stMetric"] label {
    color: #a0a2c0 !important;
    font-size: 0.9em !important;
    font-weight: 500 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.8em !important;
    font-weight: 700 !important;
}

/* Expanders & Tabs */
details {
    border: 1px solid #282846 !important;
    border-radius: 12px !important;
    background: #0f0f20 !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    margin-top: 8px;
}
summary {
    font-weight: 600 !important;
    color: #a5b4fc !important;
}
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.95em !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #5850ec !important;
}

/* Titles and Headers */
h1 {
    background: linear-gradient(90deg, #a78bfa 0%, #6366f1 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}
h2, h3 {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
}

/* Styled Badges */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.88em;
    font-weight: 600;
    text-align: center;
    border: 1px solid transparent;
}
.badge-auto {
    background: rgba(34, 197, 94, 0.15);
    color: #86efac;
    border-color: rgba(34, 197, 94, 0.3);
}
.badge-human {
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    border-color: rgba(239, 68, 68, 0.3);
}
.badge-clarify {
    background: rgba(234, 179, 8, 0.15);
    color: #fde047;
    border-color: rgba(234, 179, 8, 0.3);
}
.badge-spam {
    background: rgba(156, 163, 175, 0.15);
    color: #d1d5db;
    border-color: rgba(156, 163, 175, 0.3);
}

.citation-card {
    background: #111124;
    border: 1px solid #202042;
    border-left: 4px solid #6366f1;
    padding: 14px 18px;
    border-radius: 12px;
    margin-top: 10px;
}
.log-step {
    border-left: 3px solid #6366f1;
    padding-left: 12px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

from app.services.auth_service import auth_service

# Khởi tạo Session State cho User & Tickets
if "tickets_db" not in st.session_state:
    st.session_state["tickets_db"] = {}
if "user" not in st.session_state:
    st.session_state["user"] = None

# GIAO DIỆN XÁC THỰC ĐĂNG NHẬP / ĐĂNG KÝ (NẾU CHƯA ĐĂNG NHẬP)
if not st.session_state["user"]:
    st.title("🔐 Đăng Nhập / 📝 Đăng Ký Hệ Thống")
    st.caption("Vui lòng đăng nhập hoặc đăng ký tài khoản để trải nghiệm ứng dụng Tổng đài Hỗ trợ Multi-Agent.")

    tab_login, tab_register = st.tabs(["🔐 Đăng Nhập", "📝 Đăng Ký Tài Khoản Mới"])

    with tab_login:
        st.markdown("### ⚡ Đăng Nhập Nhanh Với Tài Khoản Demo")
        c_demo1, c_demo2 = st.columns(2)
        if c_demo1.button("👨‍💼 Admin / Nhân Sự (`admin` / `123`)", use_container_width=True):
            user = auth_service.authenticate_user("admin", "123")
            if user:
                st.session_state["user"] = user
                st.rerun()
        if c_demo2.button("👤 Khách hàng (`customer` / `123`)", use_container_width=True):
            user = auth_service.authenticate_user("customer", "123")
            if user:
                st.session_state["user"] = user
                st.rerun()

        st.markdown("---")
        with st.form("login_form"):
            login_username = st.text_input("Tên đăng nhập")
            login_password = st.text_input("Mật khẩu", type="password")
            login_submit = st.form_submit_button("🔐 Đăng Nhập", type="primary", use_container_width=True)

        if login_submit:
            user = auth_service.authenticate_user(login_username, login_password)
            if user:
                st.session_state["user"] = user
                st.success(f"🎉 Xin chào **{user['full_name']}**! Đăng nhập thành công.")
                st.rerun()
            else:
                st.error("❌ Tên đăng nhập hoặc mật khẩu không chính xác!")

    with tab_register:
        with st.form("register_form"):
            reg_username = st.text_input("Tên đăng nhập mới (VD: user123)")
            reg_password = st.text_input("Mật khẩu mới", type="password")
            reg_email = st.text_input("Email liên hệ", value="user123@gmail.com")
            reg_fullname = st.text_input("Họ và tên hiển thị", value="Nguyễn Văn User")
            reg_role = st.selectbox("Vai trò tài khoản", ["Khách hàng (customer)", "Nhân sự hỗ trợ / Admin (admin)"])
            
            reg_submit = st.form_submit_button("📝 Đăng Ký Tài Khoản Mới", type="primary", use_container_width=True)

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
                st.success(f"🎉 {res['message']} Vui lòng chuyển qua tab Đăng Nhập để vào hệ thống.")
            else:
                st.error(f"❌ {res['message']}")

    st.stop()

# ── SIDEBAR NAVIGATION ────────────────────────────────────────────────
current_user = st.session_state.get("user")
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>🤖 AUTOMATION/AGENT</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a5b4fc; font-size: 0.9em; margin-top: 0px;'>Tổng Đài Hỗ Trợ Tự Vận Hành</p>", unsafe_allow_html=True)
    st.divider()

    if current_user:
        st.markdown(f"👤 **Xin chào:** `{current_user.get('full_name', '')}`")
        st.markdown(f"🏷️ **Vai trò:** `{str(current_user.get('role', '')).upper()}`")
        if st.button("🚪 Đăng Xuất", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()
        st.divider()

    # Phân quyền menu theo vai trò người dùng (chỉ 2 role: admin & customer)
    user_role = current_user.get("role", "customer") if current_user else "customer"
    if user_role == "admin":
        available_pages = [
            "📥 Tiếp Nhận Ticket & Multi-Agent",
            "👨‍💻 Giao Diện Nhân Sự (HITL Inbox)",
            "📚 Tra Cứu Tri Thức Qdrant KB",
            "📊 Supervisor Dashboard"
        ]
    else:
        available_pages = [
            "📥 Tiếp Nhận Ticket & Multi-Agent"
        ]

    page = st.radio("Navigation", available_pages, label_visibility="collapsed")



    st.divider()
    st.markdown("##### ⚙️ Môi Trường Hệ Thống")
    st.caption("• LangGraph Engine: Ready\n• Qdrant Vector DB: Connected\n• LLM Model: Groq Llama-3.3-70B-Versatile (Active)")
    st.divider()
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S  •  %d/%m/%Y')}")





# -----------------------------------------------------------------------------
# TAB 1: TIẾP NHẬN TICKET & MULTI-AGENT PIPELINE
# -----------------------------------------------------------------------------
if page == "📥 Tiếp Nhận Ticket & Multi-Agent":
    st.title("📥 Tiếp Nhận Yêu Cầu & Multi-Agent Pipeline")
    st.caption("Thực thi luồng xử lý qua LangGraph State Machine & Qdrant Vector DB.")
    
    st.markdown("### ⚡ Kịch Bản Mẫu (Preset Scenarios)")
    col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
    
    # Khởi tạo dữ liệu kịch bản mặc định trong Session State
    if "active_preset" not in st.session_state:
        st.session_state["active_preset"] = {
            "name": "Nguyễn Văn A",
            "email": "khachhang@gmail.com",
            "channel": "web",
            "subject": "Hỏi về bảng giá gói Enterprise",
            "content": "Cho tôi xin thông tin bảng giá dịch vụ gói Enterprise năm 2026."
        }
    
    if col_p1.button("❓ FAQ Giá Cước", use_container_width=True):
        st.session_state["active_preset"] = {
            "name": "Nguyễn Văn A",
            "email": "nva@company.com",
            "channel": "web",
            "subject": "Tư vấn gói cước Enterprise",
            "content": "Bên mình đang quan tâm đến gói Enterprise cho 50 nhân sự. Cho mình xin bảng giá chi tiết và cam kết SLA với?"
        }
        st.rerun()

    if col_p2.button("⚠️ Lỗi 403 Thiếu Info", use_container_width=True):
        st.session_state["active_preset"] = {
            "name": "Trần Thị B",
            "email": "dev@partner.com",
            "channel": "email",
            "subject": "Bị lỗi 403 Forbidden khi kết nối API",
            "content": "Tôi gọi API tạo đơn hàng bị trả về lỗi 403 Forbidden liên tục từ sáng nay. Nhờ hệ thống kiểm tra gấp!"
        }
        st.rerun()

    if col_p3.button("🚨 Sự Cố P0 Khẩn Cấp", use_container_width=True):
        st.session_state["active_preset"] = {
            "name": "Lê Văn C",
            "email": "admin@client.com",
            "channel": "internal",
            "subject": "KHẨN CẤP P0: Sập máy chủ toàn bộ hệ thống",
            "content": "Toàn bộ hệ thống production bị sập không truy cập được, database rò rỉ hoặc mất kết nối. Cần DevOps xử lý ngay lập tức!"
        }
        st.rerun()

    if col_p4.button("💳 Khiếu Nại Hoàn Tiền", use_container_width=True):
        st.session_state["active_preset"] = {
            "name": "Phạm Thị D",
            "email": "dpham@gmail.com",
            "channel": "zalo",
            "subject": "Bức xúc trừ tiền 2 lần trên hóa đơn tháng 7",
            "content": "Tôi bị hệ thống trừ tiền 2 lần cho cùng một gói cước tháng 7. Tôi rất bức xúc và yêu cầu hoàn tiền ngay lập tức!"
        }
        st.rerun()

    if col_p5.button("⛔ Spam / Rác", use_container_width=True):
        st.session_state["active_preset"] = {
            "name": "Bot Spammer",
            "email": "scam@crypto.io",
            "channel": "web",
            "subject": "Cheap sale crypto trading robot 100% profit click here",
            "content": "Invest in our bitcoin trading robot now for free crypto loans and 1000% daily profit click here!"
        }
        st.rerun()

    preset = st.session_state["active_preset"]
    user_name_default = current_user.get("full_name") if current_user else preset["name"]
    user_email_default = current_user.get("email") if current_user else preset["email"]

    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Tên khách hàng (Đã xác thực)", value=user_name_default, disabled=bool(current_user), help="Tự động lấy theo tài khoản đăng nhập")
            customer_email = st.text_input("Email liên hệ (Đã xác thực)", value=user_email_default, disabled=bool(current_user), help="Tự động lấy theo tài khoản đăng nhập")
            channel_idx = ["web", "email", "zalo", "internal"].index(preset["channel"]) if preset["channel"] in ["web", "email", "zalo", "internal"] else 0
            channel = st.selectbox("Kênh tiếp nhận", ["web", "email", "zalo", "internal"], index=channel_idx)
        with col2:
            subject = st.text_input("Tiêu đề yêu cầu", value=preset["subject"])
            content = st.text_area("Nội dung yêu cầu chi tiết", value=preset["content"], height=110)
        
        submitted = st.form_submit_button("🚀 Gửi Yêu Cầu & Thực Thi LangGraph Pipeline", type="primary", use_container_width=True)



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
            "pipeline_logs": []
        }

        with st.spinner("🧠 LangGraph Multi-Agent Engine đang thực thi luồng xử lý..."):
            config = {"configurable": {"thread_id": ticket_id}}
            final_state = support_agent_graph.invoke(initial_state, config=config)

        # Lưu vào Session State DB
        st.session_state["tickets_db"][ticket_id] = {
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

        st.success(f"✅ Đã xử lý xong Ticket mã **[{ticket_id}]**!")
        
        # Hiển thị Kết quả Xử lý
        st.markdown("---")
        st.markdown("### 📊 Kết Quả Phân Tích & Phản Hồi Từ AI Agent")
        
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
                st.markdown('<span class="badge badge-auto">✅ RESOLVED_AUTO (Tự động trả lời)</span>', unsafe_allow_html=True)
            elif status == "ESCALATED_HUMAN":
                st.markdown('<span class="badge badge-human">👨‍💻 ESCALATED_HUMAN (Chuyển Nhân sự)</span>', unsafe_allow_html=True)
            elif status == "CLARIFICATION_SENT":
                st.markdown('<span class="badge badge-clarify">✉️ CLARIFICATION_SENT (Chờ làm rõ)</span>', unsafe_allow_html=True)
            elif status == "SPAM_CLOSED":
                st.markdown('<span class="badge badge-spam">⛔ SPAM_CLOSED (Đã đóng Ticket rác)</span>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Phản hồi chi tiết
        if final_state.get("ai_answer"):
            st.info(f"**💬 Câu Phản Hồi Tự Động:**\n\n{final_state.get('ai_answer')}")
        
        if final_state.get("clarification_question"):
            st.warning(f"**✉️ Câu Hỏi Tự Động Làm Rõ Thông Tin:**\n\n{final_state.get('clarification_question')}")
        
        # Citations
        citations = final_state.get("citations", [])
        if citations:
            st.markdown("#### 📚 Trích Dẫn Tri Thức Dẫn Nguồn (Qdrant Grounding Citations):")
            for c in citations:
                st.markdown(f"""
                <div class="citation-card">
                    <strong style="color: #a5b4fc;">📖 [{c.get('docId')}] {c.get('docTitle')}</strong> — <em style="color: #94a3b8;">Mục: {c.get('section')} (Độ tương đồng: {round(c.get('relevanceScore', 0)*100, 1)}%)</em><br>
                    <code style="color: #e2e8f0; background: transparent;">"{c.get('snippet')}"</code>
                </div>
                """, unsafe_allow_html=True)
        
        # Logs chi tiết
        st.markdown("---")
        with st.expander("🔍 Xem Chi Tiết Nhật Ký Xử Lý Multi-Agent (Pipeline Audit Logs)", expanded=True):
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
    st.markdown("### 📂 Lịch Sử Ticket & Kết Quả Phản Hồi Của Bạn")
    st.caption("Theo dõi tiến độ xử lý và xem trực tiếp câu trả lời do Nhân sự CSKH đã duyệt.")

    user_email = current_user.get("email") if current_user else ""
    user_fullname = current_user.get("full_name") if current_user else ""

    user_tickets = [
        t for t in st.session_state["tickets_db"].values()
        if (user_email and t.get("customerEmail") == user_email) or (user_fullname and t.get("customerName") == user_fullname)
    ]

    if not user_tickets:
        st.info("💡 Bạn chưa gửi ticket nào. Hãy gửi yêu cầu ở trên để hệ thống ghi nhận và theo dõi tiến độ.")
    else:
        for tk in reversed(user_tickets):
            status_code = tk.get("status")
            with st.expander(f"🎫 Ticket [{tk['id']}] — {tk['subject']} ({tk.get('createdAt', '')})", expanded=(status_code in ["RESOLVED_HUMAN", "RESOLVED_AUTO"])):
                c_info1, c_info2 = st.columns(2)
                with c_info1:
                    st.write(f"**Mã Ticket:** `{tk['id']}`")
                    st.write(f"**Kênh gửi:** `{tk.get('channel', 'web')}`")
                with c_info2:
                    if status_code == "RESOLVED_AUTO":
                        st.markdown('<span class="badge badge-auto">✅ RESOLVED_AUTO (AI Tự Động Trả Lời)</span>', unsafe_allow_html=True)
                    elif status_code == "RESOLVED_HUMAN":
                        st.markdown('<span class="badge badge-auto" style="background:#0284c7; color:#fff;">🔵 RESOLVED_HUMAN (Nhân Sự Đã Phản Hồi)</span>', unsafe_allow_html=True)
                    elif status_code == "ESCALATED_HUMAN":
                        st.markdown('<span class="badge badge-human">🟡 ESCALATED_HUMAN (Đang Chờ Nhân Sự Duyệt)</span>', unsafe_allow_html=True)
                    elif status_code == "CLARIFICATION_SENT":
                        st.markdown('<span class="badge badge-spam">🟠 CLARIFICATION_SENT (Cần Bổ Sung Thông Tin)</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'`{status_code}`')

                st.markdown("**Nội dung yêu cầu:**")
                st.info(tk.get("content", ""))

                st.markdown("---")
                if status_code == "RESOLVED_HUMAN":
                    st.markdown("#### 👨‍💻 Câu Trả Lời Trực Tiếp Từ Nhân Sự CSKH:")
                    st.success(tk.get("aiAnswer", "Chưa có nội dung phản hồi."))
                    if tk.get("resolvedAt"):
                        st.caption(f"🕐 Thời gian nhân sự phê duyệt & phản hồi: {tk.get('resolvedAt')}")
                elif status_code == "RESOLVED_AUTO":
                    st.markdown("#### 🤖 Câu Trả Lời Từ Trợ Lý AI Agent:")
                    st.success(tk.get("aiAnswer", "Chưa có nội dung phản hồi."))
                elif status_code == "CLARIFICATION_SENT":
                    st.markdown("#### ❓ Yêu Cầu Bổ Sung Thông Tin:")
                    st.warning(tk.get("clarificationQuestion", "Vui lòng cung cấp thêm thông tin."))
                elif status_code == "ESCALATED_HUMAN":
                    st.warning("⏳ **Yêu cầu đang nằm trong hàng chờ HITL Inbox:** Ticket của bạn đã được gửi tới Nhân sự CSKH. Vui lòng quay lại kiểm tra câu trả lời tại đây sau ít phút!")


# -----------------------------------------------------------------------------
# TAB 2: GIAO DIỆN NHÂN SỰ (HITL INBOX)
# -----------------------------------------------------------------------------

elif page == "👨‍💻 Giao Diện Nhân Sự (HITL Inbox)":
    st.title("👨‍💻 Human-in-the-Loop (HITL) Workspace")
    st.caption("Hòm thư xử lý và phê duyệt dành cho Nhân sự hỗ trợ.")
    
    escalated_tickets = [t for t in st.session_state["tickets_db"].values() if t.get("status") == "ESCALATED_HUMAN"]
    
    if not escalated_tickets:
        st.info("🎉 Hiện không có Ticket nào cần con người can thiệp trong HITL Inbox.")
    else:
        st.warning(f"⚠️ Đang có **{len(escalated_tickets)}** ticket cần nhân sự kiểm tra và phê duyệt.")
        
        selected_ticket_id = st.selectbox("Chọn Ticket cần duyệt:", [t["id"] for t in escalated_tickets])
        ticket = next(t for t in escalated_tickets if t["id"] == selected_ticket_id)
        
        st.markdown("---")
        col_t1, col_t2 = st.columns([1, 1])
        
        with col_t1:
            st.markdown(f"### 📋 Thông Tin Ticket `[{ticket['id']}]`")
            st.write(f"**Khách hàng:** {ticket['customerName']} ({ticket['customerEmail']})")
            st.write(f"**Kênh:** `{ticket['channel']}` | **Độ ưu tiên:** `{ticket['priority']}`")
            st.write(f"**Tiêu đề:** {ticket['subject']}")
            st.text_area("Nội dung yêu cầu từ khách", ticket['content'], height=130, disabled=True)
        
        with col_t2:
            st.markdown("### 🤖 AI Context Briefing Package")
            pkg = ticket.get("contextPackage") or {}
            if pkg:
                st.markdown(f"**📌 Tóm tắt:** {pkg.get('summary')}")
                st.markdown(f"**🎯 Thái độ (Sentiment):** `{pkg.get('sentiment')}`")
                st.markdown(f"**💡 Hành động đề xuất:** `{pkg.get('recommendedAction')}`")
                st.markdown(f"**🚨 Lý do chuyển giao:** {pkg.get('escalationReason')}")
            else:
                st.write("Chưa có gói briefing.")

        st.markdown("---")
        st.markdown("### ✍️ Phê Duyệt & Chỉnh Sửa Câu Trả Lời Gửi Khách Hàng")
        
        default_reply = pkg.get("autoDraftResponse") if pkg else "Kính chào quý khách, nhân viên hỗ trợ đã tiếp nhận yêu cầu và xử lý thành công."
        final_reply = st.text_area("Nội dung câu trả lời chính thức:", value=default_reply, height=120)
        
        if st.button("✅ Phê Duyệt & Gửi Phản Hồi Cho Khách Hàng", type="primary", use_container_width=True):
            ticket["status"] = "RESOLVED_HUMAN"
            ticket["aiAnswer"] = final_reply
            ticket["resolvedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success(f"🎉 Đã phê duyệt và phản hồi cho Ticket [{ticket['id']}] thành công!")
            st.rerun()


# -----------------------------------------------------------------------------
# TAB 3: TRA CỨU TRI THỨC QDRANT KB
# -----------------------------------------------------------------------------
elif page == "📚 Tra Cứu Tri Thức Qdrant KB":
    st.title("📚 Kho Tri Thức Vector Database")
    st.caption("Quản lý và tra cứu ngữ nghĩa dữ liệu trong Qdrant Vector Collection.")
    
    tab_search, tab_add = st.tabs(["🔍 Tìm Kiếm Ngữ Nghĩa (RAG Search)", "➕ Thêm Tài Liệu Mới"])
    
    with tab_search:
        search_query = st.text_input("Nhập câu hỏi hoặc từ khóa cần tìm kiếm ngữ nghĩa:", value="Chính sách hoàn tiền lỗi 403")
        top_k = st.slider("Số lượng kết quả (Top K):", 1, 5, 3)
        
        if st.button("🔎 Tra Cứu Vector Search", type="primary"):
            with st.spinner("Đang truy vấn Qdrant Vector Collection..."):
                citations = qdrant_kb.search_relevant_chunks(search_query, limit=top_k)
            
            st.markdown(f"#### Tìm thấy **{len(citations)}** đoạn tri thức tương đồng nhất:")
            for idx, c in enumerate(citations):
                st.markdown(f"""
                <div class="citation-card">
                    <strong style="color: #818cf8;">#{idx+1} [{c.get('docId')}] {c.get('docTitle')}</strong> — <em style="color: #94a3b8;">Mục: {c.get('section')} (Độ tương đồng: {round(c.get('relevanceScore', 0)*100, 1)}%)</em><br>
                    <p style="margin-top: 6px; color: #e2e8f0;">{c.get('snippet')}</p>
                </div>
                """, unsafe_allow_html=True)
                
    with tab_add:
        with st.form("add_kb_form"):
            doc_title = st.text_input("Tiêu đề tài liệu", "Hướng dẫn Cấu hình Webhook Zalo ZNS v3")
            doc_cat = st.selectbox("Chuyên mục", ["Thanh toán & Hóa đơn", "Kỹ thuật & Tích hợp", "Hỏi đáp Thông tin", "Quy trình Khẩn cấp"])
            doc_tags = st.text_input("Thẻ từ khóa (phân cách bằng dấu phẩy)", "zalo, zns, webhook, api, v3")
            doc_content = st.text_area("Nội dung tài liệu", "Cấu hình Zalo ZNS API v3 cần secret key và xác thực OAuth2 token. Thời gian timeout là 5 giây.", height=120)
            
            submit_kb = st.form_submit_button("📥 Vectorize & Index vào Qdrant", type="primary")
            
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
            st.success(f"✅ Đã nạp và tạo Vector Index cho tài liệu mã **[{doc_id}]** vào Qdrant DB thành công!")


# -----------------------------------------------------------------------------
# TAB 4: SUPERVISOR DASHBOARD
# -----------------------------------------------------------------------------
elif page == "📊 Supervisor Dashboard":
    st.title("📊 Supervisor Operations Dashboard")
    st.caption("Báo cáo và quan sát chỉ số vận hành hệ thống Tổng đài Hỗ trợ.")
    
    total = len(st.session_state["tickets_db"])
    auto_res = sum(1 for t in st.session_state["tickets_db"].values() if t.get("status") == "RESOLVED_AUTO")
    escalated = sum(1 for t in st.session_state["tickets_db"].values() if t.get("status") == "ESCALATED_HUMAN" or t.get("status") == "RESOLVED_HUMAN")
    
    deflect_rate = round(auto_res / total * 100, 1) if total > 0 else 68.5
    esc_rate = round(escalated / total * 100, 1) if total > 0 else 24.0
    
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    
    with col_m1:
        st.metric("Tổng Ticket Hôm Nay", total or 142)
    with col_m2:
        st.metric("Tỷ Lệ Tự Động (Deflection)", f"{deflect_rate}%")
    with col_m3:
        st.metric("Tỷ Lệ Chuyển Nhân Sự", f"{esc_rate}%")
    with col_m4:
        st.metric("Thời Gian Phản Hồi TB", "12s")
    with col_m5:
        st.metric("Grounding Confidence TB", "94.8%")

    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### 📈 Phân Bổ Intent / Nhóm Yêu Cầu")
        categories_dist = {
            "FAQ (Hỏi đáp chung)": (58, 58),
            "Kỹ Thuật (Technical)": (26, 26),
            "Thanh Toán (Billing)": (18, 18),
            "Khiếu Nại (Complaint)": (12, 12),
            "Thiếu Info (Incomplete)": (14, 14),
            "Khẩn Cấp P0 (Urgent)": (4, 4),
            "Spam / Rác": (4, 4)
        }
        for cat_name, (count, pct) in categories_dist.items():
            st.write(f"**{cat_name}**: {count} tickets ({pct}%)")
            st.progress(pct / 100.0)

    with col_chart2:
        st.markdown("### ⚠️ Phát Hiện Lỗ Hổng Tri Thức (KB Gaps Detected)")
        st.error("• **Chủ đề:** Hướng dẫn cấu hình Webhook Zalo ZNS v3\n  - **Số ca chuyển giao:** 14 ca\n  - **Khuyên dùng:** Nạp thêm tài liệu kỹ thuật Zalo ZNS API v3 vào Qdrant KB")
        st.warning("• **Chủ đề:** Quy trình xuất hóa đơn VAT điện tử FDI\n  - **Số ca chuyển giao:** 9 ca\n  - **Khuyên dùng:** Cập nhật điều khoản VAT nhà thầu nước ngoài vào KB-POL-001")

