import streamlit as st
import base64

def show_pdf(file_bytes):
    """Display PDF in Streamlit"""
    b64 = base64.b64encode(file_bytes).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" width="700" height="1000"></iframe>',
        unsafe_allow_html=True
    )
