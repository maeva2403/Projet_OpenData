# pages/0_🏠_Home Page.py

import streamlit as st

from functions import initialize_session_state, show_cart_sidebar # etc...

# Initialize session state and display the cart sidebar
initialize_session_state()
show_cart_sidebar()

# Page title
st.title("📊 Food Analysis Dashboard")

# Introduction
st.markdown("""
Explore and analyze food products through various features:
- **🛒 Products**: Search for products by name or category
- **📈 YourDash**: Track your nutritional goals and analyze geographical distribution
- **🆚 Compare**: Compare up to 5 products side by side
- **🍲 Recipes**: Find recipes based on ingredients
- **📊 Categories**: Analyze trends by category
""")

# Footer with project attribution in italics
st.markdown("<br><br><i>In the context of the Open Data project: Brice Grivet, Maéva Maïo, Houria Sayah.</i>", unsafe_allow_html=True)