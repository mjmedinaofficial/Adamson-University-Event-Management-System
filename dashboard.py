import streamlit as st
from utils import run_query

st.set_page_config(page_title="Event Management System",
                    layout="wide",
                )

st.title("Event Management System")
st.write("Welcome back, Admin!")
st.divider()

st.write("Event Summary")