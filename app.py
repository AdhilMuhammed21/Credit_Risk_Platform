
import streamlit as st

from src.ml.predict import predict_risk
from src.talk_to_data.chatbot import ask

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Credit Risk Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(to bottom right, #0f172a, #111827);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    h1, h2, h3, h4, h5 {
        color: white !important;
    }

    p, label, div {
        color: #e5e7eb;
    }

    .hero-box {
        background: linear-gradient(to right, #1d4ed8, #2563eb);
        padding: 35px;
        border-radius: 22px;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: white;
    }

    .hero-sub {
        font-size: 18px;
        color: #dbeafe;
        margin-top: 10px;
    }

    .metric-card {
        background: #111827;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #1f2937;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }

    .info-card {
        background: #1e293b;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 15px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.2em;
        font-size: 16px;
        font-weight: 600;
        background-color: #2563eb;
        color: white;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }

    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 18px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏦 AI Credit Risk")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Prediction",
        "AI Chatbot"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
    Built using:
    - LightGBM
    - SHAP
    - Streamlit
    - SQLite
    - LLM-powered analytics
    """
)

# =========================================================
# DASHBOARD PAGE
# =========================================================

if page == "Dashboard":

    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">
                AI Credit Risk Intelligence Platform
            </div>

            <div class="hero-sub">
                Real-time risk prediction, explainable AI, and conversational analytics.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <h3>Model</h3>
                <h2>LightGBM</h2>
                <p>Gradient Boosted Trees</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <h3>Explainability</h3>
                <h2>SHAP AI</h2>
                <p>Transparent Risk Decisions</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <h3>Analytics</h3>
                <h2>NL → SQL</h2>
                <p>Conversational Intelligence</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## 📊 Model Performance")

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            "assets/charts/confusion_matrix.png",
            caption="Confusion Matrix",
            use_container_width=True
        )

    with col2:
        st.image(
            "assets/charts/feature_importance.png",
            caption="Feature Importance",
            use_container_width=True
        )

    st.markdown("## 🧠 Explainable AI")

    st.image(
        "assets/charts/shap_summary.png",
        caption="SHAP Summary Plot",
        use_container_width=True
    )

    st.image(
        "assets/charts/shap_waterfall.png",
        caption="SHAP Waterfall Plot",
        use_container_width=True
    )

# =========================================================
# PREDICTION PAGE
# =========================================================

elif page == "Prediction":

    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">
                Credit Risk Prediction
            </div>

            <div class="hero-sub">
                Predict customer default probability using machine learning.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        income = st.number_input(
            "💰 Total Income",
            min_value=0.0,
            value=150000.0
        )

    with col2:
        credit = st.number_input(
            "🏦 Credit Amount",
            min_value=0.0,
            value=500000.0
        )

    with col3:
        annuity = st.number_input(
            "📅 Annuity Amount",
            min_value=0.0,
            value=25000.0
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Predict Credit Risk"):

        with st.spinner("Running ML model..."):

            result = predict_risk(
                income,
                credit,
                annuity
            )

        score = result["risk_score"]
        band = result["risk_band"]

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Risk Score",
                value=f"{score:.4f}"
            )

        with col2:
            st.metric(
                label="Risk Category",
                value=band
            )

        st.markdown("## 📌 Business Interpretation")

        if band == "High Risk":

            st.error(
                "Applicant shows elevated default probability and financial stress indicators."
            )

        elif band == "Medium Risk":

            st.warning(
                "Applicant demonstrates moderate repayment risk and should be monitored carefully."
            )

        else:

            st.success(
                "Applicant appears financially stable with lower predicted default probability."
            )

# =========================================================
# CHATBOT PAGE
# =========================================================

elif page == "AI Chatbot":

    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">
                AI Risk Analyst
            </div>

            <div class="hero-sub">
                Ask natural language questions about customer credit data.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info-card">

        <b>Example Questions</b><br><br>

        • What is the average income of defaulters?<br>
        • Show top 10 highest income customers<br>
        • What is the average credit amount for non-defaulters?<br>
        • Show average annuity for risky customers

        </div>
        """,
        unsafe_allow_html=True
    )

    question = st.text_input(
        "Ask your question"
    )

    show_sql = st.checkbox("Show Generated SQL")

    if st.button("Ask AI"):

        if question:

            with st.spinner("Analyzing data..."):

                response = ask(question)

            if show_sql:

                st.subheader("Generated SQL")

                st.code(
                    response["sql"],
                    language="sql"
                )

            st.subheader("Query Result")

            st.write(
                response["result"]
            )

