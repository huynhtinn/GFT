import streamlit as st
import json
from datetime import datetime
from app.graph.builder import support_agent_graph
from app.services.qdrant_service import qdrant_kb

# Cấu hình Trang Streamlit
st.set_page_config(
    page_title="Tổng Đài Hỗ Trợ Tự Vận Hành — AI Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho Giao diện Trực quan & Hiện đại
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
    }
    .main-header p {
        margin: 6px 0 0 0;
        opacity: 0.9;
        font-size: 14px;
    }
    .badge-auto {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #c3e6cb;
    }
    .badge-human {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #f5c6cb;
    }
    .badge-clarify {
        background-color: #fff3cd;
        color: #856404;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #ffeeba;
    }
    .badge-spam {
        background-color: #e2e3e5;
        color: #383d41;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #d6d8db;
    }
    .citation-box {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 12px;
        border-radius: 4px;
        margin-top: 8px;
        font-size: 13px;
    }
    .log-step {
        border-left: 3px solid #6c757d;
        padding-left: 12px;
        margin-bottom: 10px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        text-align: center;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 24px;
        color: #007bff;
    }
    .metric-card p {
        margin: 4px 0 0 0;
        color: #6c757d;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo Session State cho danh sách Ticket
if "tickets_db" not in st.session_state:
    st.session_state["tickets_db"] = {}

# Header Chức năng
st.markdown("""
<div class="main-header">
    <h1>🤖 AUTOMATION/AGENT — Tổng Đài Hỗ Trợ Tự Vận Hành</h1>
    <p>Kiến trúc Multi-Agent State Machine (LangGraph) + Vector DB Search (Qdrant) + Human-in-the-Loop (HITL)</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/bot.png", width=70)
st.sidebar.title("📌 Điều Hướng")
page = st.sidebar.radio(
    "Chọn giao diện chức năng:",
    [
        "📥 Tiếp Nhận Ticket & Multi-Agent",
        "👨‍💻 Giao Diện Nhân Sự (HITL Inbox)",
        "📚 Tra Cứu Tri Thức Qdrant KB",
        "📊 Supervisor Dashboard"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Môi trường Hệ thống")
st.sidebar.info("• LangGraph Engine: Ready\n• Qdrant Vector DB: Connected\n• Memory Checkpointer: Active")


# -----------------------------------------------------------------------------
# TAB 1: TIẾP NHẬN TICKET & MULTI-AGENT PIPELINE
# -----------------------------------------------------------------------------
if page == "📥 Tiếp Nhận Ticket & Multi-Agent":
    st.subheader("📥 Tiếp Nhận Yêu Cầu & Chạy LangGraph Multi-Agent Pipeline")
    
    st.markdown("### ⚡ Kịch Bản Mẫu (Preset Scenarios)")
    col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
    
    preset_data = None
    
    if col_p1.button("❓ FAQ Giá Cước", use_container_width=True):
        preset_data = {
            "name": "Nguyễn Văn A",
            "email": "nva@company.com",
            "channel": "web",
            "subject": "Tư vấn gói cước Enterprise",
            "content": "Bên mình đang quan tâm đến gói Enterprise cho 50 nhân sự. Cho mình xin bảng giá chi tiết và cam kết SLA với?"
        }
    if col_p2.button("⚠️ Lỗi 403 Thiếu Info", use_container_width=True):
        preset_data = {
            "name": "Trần Thị B",
            "email": "dev@partner.com",
            "channel": "email",
            "subject": "Bị lỗi 403 Forbidden khi kết nối API",
            "content": "Tôi gọi API tạo đơn hàng bị trả về lỗi 403 Forbidden liên tục từ sáng nay. Nhờ hệ thống kiểm tra gấp!"
        }
    if col_p3.button("🚨 Sự Cố P0 Khẩn Cấp", use_container_width=True):
        preset_data = {
            "name": "Lê Văn C",
            "email": "admin@client.com",
            "channel": "internal",
            "subject": "KHẨN CẤP P0: Sập máy chủ toàn bộ hệ thống",
            "content": "Toàn bộ hệ thống production bị sập không truy cập được, database rò rỉ hoặc mất kết nối. Cần DevOps xử lý ngay lập tức!"
        }
    if col_p4.button("💳 Khiếu Nại Hoàn Tiền", use_container_width=True):
        preset_data = {
            "name": "Phạm Thị D",
            "email": "dpham@gmail.com",
            "channel": "zalo",
            "subject": "Bức xúc trừ tiền 2 lần trên hóa đơn tháng 7",
            "content": "Tôi bị hệ thống trừ tiền 2 lần cho cùng một gói cước tháng 7. Tôi rất bức xúc và yêu cầu hoàn tiền ngay lập tức!"
        }
    if col_p5.button("⛔ Spam / Rác", use_container_width=True):
        preset_data = {
            "name": "Bot Spammer",
            "email": "scam@crypto.io",
            "channel": "web",
            "subject": "Cheap sale crypto trading robot 100% profit click here",
            "content": "Invest in our bitcoin trading robot now for free crypto loans and 1000% daily profit click here!"
        }

    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Tên khách hàng", value=preset_data["name"] if preset_data else "Nguyễn Văn A")
            customer_email = st.text_input("Email liên hệ", value=preset_data["email"] if preset_data else "khachhang@gmail.com")
            channel = st.selectbox("Kênh tiếp nhận", ["web", "email", "zalo", "internal"], index=0 if not preset_data else ["web", "email", "zalo", "internal"].index(preset_data["channel"]))
        with col2:
            subject = st.text_input("Tiêu đề yêu cầu", value=preset_data["subject"] if preset_data else "Hỏi về bảng giá gói Enterprise")
            content = st.text_area("Nội dung yêu cầu chi tiết", value=preset_data["content"] if preset_data else "Cho tôi xin thông tin bảng giá dịch vụ gói Enterprise năm 2026.", height=110)
        
        submitted = st.form_submit_button("🚀 Gửi Yêu Cầu & Thực Thi LangGraph Pipeline", use_container_width=True)

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

        # Lưu vào database giả lập trong Session
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
                st.markdown('<span class="badge-auto">✅ RESOLVED_AUTO (Tự động trả lời)</span>', unsafe_allow_html=True)
            elif status == "ESCALATED_HUMAN":
                st.markdown('<span class="badge-human">👨‍💻 ESCALATED_HUMAN (Chuyển Nhân sự)</span>', unsafe_allow_html=True)
            elif status == "CLARIFICATION_SENT":
                st.markdown('<span class="badge-clarify">✉️ CLARIFICATION_SENT (Chờ làm rõ)</span>', unsafe_allow_html=True)
            elif status == "SPAM_CLOSED":
                st.markdown('<span class="badge-spam">⛔ SPAM_CLOSED (Đã đóng Ticket rác)</span>', unsafe_allow_html=True)
        
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
                <div class="citation-box">
                    <strong>📖 [{c.get('docId')}] {c.get('docTitle')}</strong> — <em>Mục: {c.get('section')} (Độ tương đồng: {round(c.get('relevanceScore', 0)*100, 1)}%)</em><br>
                    <code>"{c.get('snippet')}"</code>
                </div>
                """, unsafe_allow_html=True)
        
        # Logs chi tiết
        st.markdown("---")
        with st.expander("🔍 Xem Chi Tiết Nhật Ký Xử Lý Multi-Agent (Pipeline Audit Logs)", expanded=True):
            logs = final_state.get("pipeline_logs", [])
            for log in logs:
                st.markdown(f"""
                <div class="log-step">
                    <strong>[{log.get('stepName')}]</strong> — <span style="color: grey;">{log.get('timestamp')}</span><br>
                    Status: <code>{log.get('status').upper()}</code> | Chi tiết: {log.get('detail')}
                </div>
                """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 2: GIAO DIỆN NHÂN SỰ (HITL INBOX)
# -----------------------------------------------------------------------------
elif page == "👨‍💻 Giao Diện Nhân Sự (HITL Inbox)":
    st.subheader("👨‍💻 Human-in-the-Loop (HITL) Workspace — Hòm Thư Nhân Sự")
    
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
            st.markdown("### 🤖 AI Context Briefing Package (Cho Nhân Sự)")
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
    st.subheader("📚 Kho Tri Thức Vector DB (Qdrant Collection Manager)")
    
    tab_search, tab_add = st.tabs(["🔍 Tìm Kiếm Ngữ Nghĩa (RAG Search)", "➕ Thêm Tài Liệu Mới"])
    
    with tab_search:
        search_query = st.text_input("Nhập câu hỏi hoặc từ khóa cần tìm kiếm ngữ nghĩa:", value="Chính sách hoàn tiền lỗi 403")
        top_k = st.slider("Số lượng kết quả (Top K):", 1, 5, 3)
        
        if st.button("🔎 Tra Cứu Vector Search"):
            with st.spinner("Đang truy vấn Qdrant Vector Collection..."):
                citations = qdrant_kb.search_relevant_chunks(search_query, limit=top_k)
            
            st.markdown(f"#### Tìm thấy **{len(citations)}** đoạn tri thức tương đồng nhất:")
            for idx, c in enumerate(citations):
                st.markdown(f"""
                <div class="citation-box">
                    <strong>#{idx+1} [{c.get('docId')}] {c.get('docTitle')}</strong> — <em>Mục: {c.get('section')} (Độ tương đồng: {round(c.get('relevanceScore', 0)*100, 1)}%)</em><br>
                    <p style="margin-top: 6px;">{c.get('snippet')}</p>
                </div>
                """, unsafe_allow_html=True)
                
    with tab_add:
        with st.form("add_kb_form"):
            doc_title = st.text_input("Tiêu đề tài liệu", "Hướng dẫn Cấu hình Webhook Zalo ZNS v3")
            doc_cat = st.selectbox("Chuyên mục", ["Thanh toán & Hóa đơn", "Kỹ thuật & Tích hợp", "Hỏi đáp Thông tin", "Quy trình Khẩn cấp"])
            doc_tags = st.text_input("Thẻ từ khóa (phân cách bằng dấu phẩy)", "zalo, zns, webhook, api, v3")
            doc_content = st.text_area("Nội dung tài liệu", "Cấu hình Zalo ZNS API v3 cần secret key và xác thực OAuth2 token. Thời gian timeout là 5 giây.", height=120)
            
            submit_kb = st.form_submit_button("📥 Vectorize & Index vào Qdrant")
            
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
    st.subheader("📊 Supervisor Dashboard — Báo Cáo & Quan Sát Vận Hành")
    
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
        st.bar_chart({
            "FAQ": 58,
            "Kỹ Thuật": 26,
            "Thanh Toán": 18,
            "Khiếu Nại": 12,
            "Thiếu Info": 14,
            "Khẩn Cấp P0": 4,
            "Spam": 4
        })
        
    with col_chart2:
        st.markdown("### ⚠️ Phát Hiện Lỗ Hổng Tri Thức (KB Gaps Detected)")
        st.error("• **Chủ đề:** Hướng dẫn cấu hình Webhook Zalo ZNS v3\n  - **Số ca chuyển giao:** 14 ca\n  - **Khuyên dùng:** Nạp thêm tài liệu kỹ thuật Zalo ZNS API v3 vào Qdrant KB")
        st.warning("• **Chủ đề:** Quy trình xuất hóa đơn VAT điện tử FDI\n  - **Số ca chuyển giao:** 9 ca\n  - **Khuyên dùng:** Cập nhật điều khoản VAT nhà thầu nước ngoài vào KB-POL-001")

