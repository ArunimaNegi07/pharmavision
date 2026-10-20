import streamlit as st

# load css file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("styles.css")

st.header("Welcome to PharmaVision")

st.subheader("Decode Doctor's Handwriting Instantly!")
st.text("Are you tired of struggling with illegible prescriptions? Our AI-powered solution converts handwritten doctor's prescriptions into clear, structured text in seconds!")
st.text("Just head over to the Read Prescription page and upload an image of the prescription to get instant ressults.")

st.subheader("Wanna know more about your medicine?")
st.text("Head to the Drug Assistant page and ask away! Know all about the side effects and other details of your prescription.")