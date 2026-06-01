import streamlit as st
from src.ml.predict import predict_risk
from src.talk_to_data.chatbot import ask

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Credit Risk Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0e1a !important;
    color: #e2e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #1e2738;
    padding-top: 8px;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 14px;
    font-weight: 500;
    padding: 6px 0;
    transition: color 0.15s;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #f1f5f9 !important;
}

/* ── Typography ── */
h1, h2, h3, h4 { color: #f1f5f9 !important; font-weight: 600; letter-spacing: -0.3px; }
p, span, label, div { color: #94a3b8; font-size: 14px; }

/* ── Page header band ── */
.page-header {
    background: linear-gradient(135deg, #0f2027 0%, #1a2a4a 50%, #0f2027 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    color: #3b82f6;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.page-header-title {
    font-size: 28px;
    font-weight: 600;
    color: #f1f5f9 !important;
    line-height: 1.2;
    margin-bottom: 6px;
}
.page-header-sub {
    font-size: 14px;
    color: #64748b;
    font-weight: 400;
}

/* ── Stat card ── */
.stat-card {
    background: #0d1117;
    border: 1px solid #1e2738;
    border-radius: 14px;
    padding: 22px 24px;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: #2d4a7a; }
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #475569;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.stat-value {
    font-size: 26px;
    font-weight: 600;
    color: #f1f5f9;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-sub {
    font-size: 12px;
    color: #475569;
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #3b82f6;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 14px;
    margin-top: 28px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2738;
}

/* ── Input fields ── */
.stNumberInput input, .stTextInput input, .stTextArea textarea {
    background-color: #0d1117 !important;
    border: 1px solid #1e2738 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
}
.stNumberInput input:focus, .stTextInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    outline: none !important;
}
.stNumberInput label, .stTextInput label, .stTextArea label {
    color: #64748b !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
}

/* ── Primary button ── */
div.stButton > button {
    background: #1d4ed8 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px !important;
    width: 100% !important;
    transition: background 0.2s, transform 0.1s !important;
    cursor: pointer !important;
}
div.stButton > button:hover {
    background: #2563eb !important;
    transform: translateY(-1px) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }

/* ── Risk badge ── */
.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.5px;
}
.risk-high   { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.risk-medium { background: rgba(234,179,8,0.12);  color: #fbbf24; border: 1px solid rgba(234,179,8,0.25); }
.risk-low    { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }

/* ── Score bar ── */
.score-track {
    background: #1e2738;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
    margin: 10px 0 4px;
}
.score-fill-high   { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #f87171, #ef4444); }
.score-fill-medium { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #fbbf24, #f59e0b); }
.score-fill-low    { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #4ade80, #22c55e); }

/* ── Result block ── */
.result-block {
    background: #0d1117;
    border: 1px solid #1e2738;
    border-radius: 14px;
    padding: 24px;
    margin-top: 20px;
}

/* ── Chat message ── */
.chat-user {
    background: #1e2738;
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 14px;
    color: #e2e8f0;
    max-width: 80%;
    margin-left: auto;
}
.chat-ai {
    background: #0d1117;
    border: 1px solid #1e2738;
    border-radius: 12px 12px 12px 4px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 14px;
    color: #cbd5e1;
    max-width: 90%;
}
.chat-ai-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #3b82f6;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.sql-box {
    background: #060b14;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: #7dd3fc;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Example chip ── */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.chip {
    background: #0d1117;
    border: 1px solid #1e2738;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    color: #64748b;
    cursor: default;
}

/* ── Divider ── */
hr { border-color: #1e2738 !important; margin: 24px 0 !important; }

/* ── Metric widget ── */
div[data-testid="metric-container"] {
    background: #0d1117 !important;
    border: 1px solid #1e2738 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
}
div[data-testid="metric-container"] label { color: #475569 !important; font-size: 12px !important; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-size: 22px !important;
    font-weight: 600 !important;
}

/* ── Checkbox ── */
.stCheckbox label { color: #64748b !important; font-size: 13px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #3b82f6 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e2738; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2d4a7a; }

/* ── Image card ── */
.img-card {
    background: #0d1117;
    border: 1px solid #1e2738;
    border-radius: 14px;
    padding: 16px;
    overflow: hidden;
}
.img-caption {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #475569;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 0 4px 20px;'>
        <div style='font-family:"DM Mono",monospace;font-size:10px;color:#3b82f6;
                    letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;'>Platform</div>
        <div style='font-size:18px;font-weight:600;color:#f1f5f9;'>Credit Risk AI</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Dashboard", "Prediction", "AI Chatbot"],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding:0 4px'>
        <div style='font-family:"DM Mono",monospace;font-size:10px;color:#475569;
                    letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;'>Stack</div>
        <div style='display:flex;flex-direction:column;gap:8px;'>
            <div style='font-size:13px;color:#64748b;'>⬡ LightGBM</div>
            <div style='font-size:13px;color:#64748b;'>◈ SHAP Explainability</div>
            <div style='font-size:13px;color:#64748b;'>◎ Gemini LLM</div>
            <div style='font-size:13px;color:#64748b;'>▦ SQLite Analytics</div>
            <div style='font-size:13px;color:#64748b;'>⬡ Streamlit UI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════
if page == "Dashboard":

    st.markdown("""
    <div class="page-header">
        <div class="page-header-label">Overview</div>
        <div class="page-header-title">Credit Risk Intelligence Platform</div>
        <div class="page-header-sub">Real-time default prediction · Explainable AI · Conversational analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # Stat row
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("MODEL", "LightGBM", "Gradient boosted trees"),
        ("AUC SCORE", "0.769", "ROC-AUC on test set"),
        ("FEATURES", "120+", "After engineering"),
        ("IMBALANCE", "11.4 : 1", "scale_pos_weight applied"),
    ]
    for col, (label, value, sub) in zip([c1, c2, c3, c4], stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
                <div class="stat-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # Model performance
    st.markdown('<div class="section-label">Model Performance</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for col, img, caption in [
        (col1, "assets/charts/confusion_matrix.png", "CONFUSION MATRIX"),
        (col2, "assets/charts/feature_importance.png", "FEATURE IMPORTANCE"),
    ]:
        with col:
            st.markdown('<div class="img-card">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.markdown(f'<div class="img-caption">{caption}</div></div>', unsafe_allow_html=True)

    # Explainability
    st.markdown('<div class="section-label">Explainable AI — SHAP</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for col, img, caption in [
        (col1, "assets/charts/shap_summary.png",   "SHAP SUMMARY"),
        (col2, "assets/charts/shap_waterfall.png", "SHAP WATERFALL"),
    ]:
        with col:
            st.markdown('<div class="img-card">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.markdown(f'<div class="img-caption">{caption}</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PREDICTION
# ═══════════════════════════════════════════════════════════════════
elif page == "Prediction":

    st.markdown("""
    <div class="page-header">
        <div class="page-header-label">Risk Scoring</div>
        <div class="page-header-title">Credit Risk Prediction</div>
        <div class="page-header-sub">Enter applicant financials to get an instant default probability score.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Applicant Financials</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        income = st.number_input("Total Annual Income (₹)", min_value=0.0, value=150000.0, step=10000.0)
    with c2:
        credit = st.number_input("Credit Amount Requested (₹)", min_value=0.0, value=500000.0, step=10000.0)
    with c3:
        annuity = st.number_input("Monthly Annuity (₹)", min_value=0.0, value=25000.0, step=1000.0)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button("Run Risk Assessment →")

    if predict_clicked:
        with st.spinner("Running model inference..."):
            result = predict_risk(income, credit, annuity)

        score = result["risk_score"]
        band  = result["risk_band"]
        pct   = int(score * 100)

        band_class = {
            "High Risk": "risk-high",
            "Medium Risk": "risk-medium",
            "Low Risk": "risk-low",
        }.get(band, "risk-low")

        fill_class = {
            "High Risk": "score-fill-high",
            "Medium Risk": "score-fill-medium",
            "Low Risk": "score-fill-low",
        }.get(band, "score-fill-low")

        dot = {"High Risk": "🔴", "Medium Risk": "🟡", "Low Risk": "🟢"}.get(band, "⚪")

        st.markdown(f"""
        <div class="result-block">
            <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;'>
                <div>
                    <div style='font-family:"DM Mono",monospace;font-size:10px;
                                color:#475569;letter-spacing:1.5px;text-transform:uppercase;
                                margin-bottom:6px;'>Default Probability</div>
                    <div style='font-size:42px;font-weight:600;color:#f1f5f9;
                                font-family:"DM Mono",monospace;line-height:1;'>{score:.4f}</div>
                </div>
                <span class="risk-badge {band_class}">{dot} {band}</span>
            </div>
            <div style='font-family:"DM Mono",monospace;font-size:10px;
                        color:#475569;letter-spacing:1px;margin-bottom:6px;'>
                RISK SCORE — {pct}%
            </div>
            <div class="score-track">
                <div class="{fill_class}" style="width:{pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Interpretation</div>', unsafe_allow_html=True)

        msgs = {
            "High Risk":   ("🔴", "#fca5a5", "#7f1d1d", "#fee2e2",
                            "Elevated default probability detected.",
                            "Applicant shows significant financial stress indicators. "
                            "Recommend manual review, collateral requirements, or decline."),
            "Medium Risk": ("🟡", "#fcd34d", "#78350f", "#fef3c7",
                            "Moderate risk — monitor carefully.",
                            "Applicant demonstrates borderline repayment capacity. "
                            "Consider reduced credit limit or additional documentation."),
            "Low Risk":    ("🟢", "#86efac", "#14532d", "#dcfce7",
                            "Financially stable applicant.",
                            "Low predicted default probability. "
                            "Applicant appears creditworthy based on available features."),
        }
        icon, tc, bg_dark, bg_light, title, body = msgs.get(band, msgs["Low Risk"])
        st.markdown(f"""
        <div style='background:{bg_dark}22;border:1px solid {bg_dark}55;
                    border-radius:12px;padding:18px 20px;'>
            <div style='font-size:15px;font-weight:600;color:{tc};margin-bottom:6px;'>
                {icon} {title}
            </div>
            <div style='font-size:13px;color:{tc}cc;'>{body}</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# AI CHATBOT (FIXED CONDITIONAL MARKDOWN LAYOUTS)
# ═══════════════════════════════════════════════════════════════════
elif page == "AI Chatbot":

    st.markdown("""
    <div class="page-header">
        <div class="page-header-label">Conversational Analytics</div>
        <div class="page-header-title">AI Risk Analyst</div>
        <div class="page-header-sub">Ask plain-English questions about your credit portfolio data.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-bottom:18px;'>
        <div style='font-family:"DM Mono",monospace;font-size:10px;color:#475569;
                    letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;'>
            Example Questions
        </div>
        <div class="chip-row">
            <span class="chip">What is the average income of defaulters?</span>
            <span class="chip">Top 10 highest income customers</span>
            <span class="chip">Average credit amount for non-defaulters</span>
            <span class="chip">Average annuity for high-risk customers</span>
            <span class="chip">Count of defaults by gender</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_input(
        "Your question",
        placeholder="e.g. What is the average income of defaulters?",
        label_visibility="collapsed"
    )
    c1, c2 = st.columns([4, 1])
    with c1:
        ask_clicked = st.button("Ask AI →")
    with c2:
        show_sql = st.checkbox("Show SQL", value=False)

    if ask_clicked and question:
        with st.spinner("Querying data..."):
            response = ask(question)

        st.markdown(f'<div class="chat-user">{question}</div>', unsafe_allow_html=True)

        result = response.get("result", "No result returned.")
        
        # Handle dataframe-like output cleanly
        if hasattr(result, "to_html"):
            result_text = result.to_html(
                index=False,
                classes="clean-table",
                border=0
            )
        else:
            result_text = str(result)

        # ── Isolated Execution Logic to prevent Streamlit Variable Escaping ──
        if show_sql and response.get("sql"):
            sql_html = f'<div class="sql-box">{response["sql"]}</div>'
            st.markdown(f"""
            <div class="chat-ai">
                <div class="chat-ai-label">AI Analyst</div>
                {sql_html}
                <div style="margin-top: 10px; font-size: 14px; color: #cbd5e1; line-height: 1.6;">
                    {result_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-ai">
                <div class="chat-ai-label">AI Analyst</div>
                <div style="font-size: 14px; color: #cbd5e1; line-height: 1.6;">
                    {result_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

    elif ask_clicked and not question:
        st.markdown("""
        <div style='color:#f87171;font-size:13px;margin-top:8px;'>
            Please enter a question first.
        </div>
        """, unsafe_allow_html=True)