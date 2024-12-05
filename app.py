import streamlit as st
import google.generativeai as genai
import re
import json
import time
import os
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
from pages.quiz1 import maini
from pages.quiz2 import mainy
st.set_page_config(
    page_title="Ratio Analysis Quiz ->(BEFA)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PAGES = {
    "Quiz1" : maini,
    "Quiz2" : mainy
}
# Sidebar navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Display the selected page
PAGES[selection]()
