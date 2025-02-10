import streamlit as st

def set_black_background():
    st.markdown(
        """
        <style>
        body {
            background-color: black;  # Set the background color to black
            color: white;  # Set the text color to white for contrast
        }
        .css-1d391kg {color: white;}  # Adjusts the default text color for Streamlit widgets
        </style>
        """,
        unsafe_allow_html=True
    )
