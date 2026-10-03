import os
import streamlit as st

APP_TITLE = "🚀 AI Data Analyst"
APP_SUBTITLE = "Excel + SQL + Python + Power BI + Generative AI All-in-One Platform"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_SALES_PATH = os.path.join(BASE_DIR, "sample_data", "Sales_Data.xlsx")
SAMPLE_ECOMMERCE_PATH = os.path.join(BASE_DIR, "sample_data", "Ecommerce_Orders.csv")
CSS_PATH = os.path.join(BASE_DIR, "assets", "custom_style.css")

def load_css():
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
