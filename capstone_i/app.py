import streamlit as st
from utils import get_logger

logger = get_logger("genai_capstone_app")

st.set_page_config(page_title="GenAI Capstone Project", page_icon="🤖")

st.title("GenAI Capstone Project")
st.write("Work in progress")

logger.info("Streamlit app started")
