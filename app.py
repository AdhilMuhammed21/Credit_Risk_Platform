import streamlit as st

from src.ml.predict import predict_risk
from src.talk_to_data.chatbot import ask

st.set_page_config(
    page_title="AI Credit Risk Platform",
    layout="wide"
)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Navigation")

page = st.sidebar.radio(

    [
        "Dashboard",
        "Prediction",
        "AI Chatbot"
    ]
)

# =========================
# DASHBOARD PAGE
# =========================

if page == "Dashboard":

    st.title("📊 Credit Risk Dashboard")

    st.subheader("Model Performance")

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

    st.subheader("Explainable AI")

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

# =========================
# PREDICTION PAGE
# =========================

elif page == "Prediction":

    st.title("⚠️ Credit Risk Prediction")

    st.subheader("Applicant Information")

    income = st.number_input(
        "Total Income",
        min_value=0.0,
        value=150000.0
    )

    credit = st.number_input(
        "Credit Amount",
        min_value=0.0,
        value=500000.0
    )

    annuity = st.number_input(
        "Annuity Amount",
        min_value=0.0,
        value=25000.0
    )

    if st.button("Predict Risk"):

        with st.spinner("Running ML model..."):

            result = predict_risk(
                income,
                credit,
                annuity
            )

        st.metric(
            "Risk Score",
            result["risk_score"]
        )

        st.success(
            f"Risk Category: {result['risk_band']}"
        )

        st.subheader("Business Interpretation")

        if result["risk_band"] == "High Risk":

            st.error(
                "Applicant shows elevated default probability."
            )

        elif result["risk_band"] == "Medium Risk":

            st.warning(
                "Applicant has moderate financial risk."
            )

        else:

            st.success(
                "Applicant appears financially stable."
            )

# =========================
# AI CHATBOT PAGE
# =========================

elif page == "AI Chatbot":

    st.title("🤖 AI Risk Analyst")

    st.write(
        "Ask natural language questions about customer risk data."
    )

    question = st.text_input(
        "Enter your question"
    )

    if st.button("Ask AI"):

        if question:

            with st.spinner("Analyzing data..."):

                response = ask(question)

            st.subheader("Generated SQL")

            st.code(
                response["sql"],
                language="sql"
            )

            st.subheader("Query Result")

            st.write(
                response["result"]
            )