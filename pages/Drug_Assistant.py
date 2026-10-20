import os

import streamlit as st
import google.generativeai as genai


def get_google_api_key():
    try:
        key = (
            st.secrets.get("google_api_key")
            or st.secrets.get("GEMINI_API_KEY")
        )
    except Exception:
        key = None

    return (
        key
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
    )


st.title("💊 PharmaVision: Drug Assistant")
st.write(
    "Ask general questions about medications, uses, side effects, "
    "and potential drug interactions."
)

medications_input = st.text_area(
    "Enter medication names or a medication-related question:"
)


def get_drug_info(query):
    api_key = get_google_api_key()

    if not api_key:
        st.error(
            "Google Gemini API key is not configured. "
            "Set it in Streamlit secrets or the GOOGLE_API_KEY "
            "environment variable."
        )
        return None

    try:
        genai.configure(api_key=api_key)
        model_name = os.environ.get(
            "GEMINI_MODEL", "gemini-2.5-flash"
        )
        model = genai.GenerativeModel(model_name)

        response = model.generate_content(
            "Provide a clear, cautious, evidence-aware explanation "
            "of the following medication-related question. Discuss "
            "relevant uses, side effects, and potential interactions "
            "where appropriate. Identify uncertainty and advise "
            "consulting a qualified healthcare professional for "
            "individual medical decisions.\n\n"
            f"Question: {query}"
        )

        return response.text

    except Exception:
        st.error(
            "The Gemini request failed. Check your API key, model "
            "availability, network connection, and API quota."
        )
        return None


if st.button("Analyze"):
    if not medications_input.strip():
        st.warning("Please enter a medication-related question.")
    else:
        with st.spinner("Analyzing with Gemini AI..."):
            result = get_drug_info(medications_input.strip())

        if result:
            st.success("Response received.")
            st.write(result)
        elif result == "":
            st.warning("The model returned an empty response.")

st.caption(
    "For informational use only. AI responses may be inaccurate and "
    "must not replace professional medical advice or pharmacist review."
)
