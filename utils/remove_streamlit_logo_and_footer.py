import streamlit as st

def remove_streamlit_logo_and_footer():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}  # Hides the Streamlit logo in the top-left corner
        footer {visibility: hidden;}  # Hides the footer
        </style>
        """,
        unsafe_allow_html=True
    )
