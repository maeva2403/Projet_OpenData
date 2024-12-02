# pages/0_🏠_Home Page.py

import streamlit as st
from functions import initialize_session_state, show_cart_sidebar

# Initialize session state and display the cart sidebar
initialize_session_state()
show_cart_sidebar()

# Page styling with CSS
st.markdown(
    """
    <style>
    .title {
        color: #FF6F3C;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        font-family: Arial, sans-serif;
    }
    .subtitle {
        color: #FF6F3C;
        font-size: 1.3em;
        text-align: center;
        font-family: Arial, sans-serif;
        margin-bottom: 20px;
    }
    .description {
        color: #333333;
        font-size: 1.1em;
        text-align: justify;
        font-family: Arial, sans-serif;
        line-height: 1.6;
    }
    .footer {
        font-style: italic;
        text-align: center;
        margin-top: 50px;
        color: #555555;
        font-family: Arial, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True
)

# Page title
st.markdown("<h1 class='title'>📊 Food Analysis Dashboard</h1>", unsafe_allow_html=True)

# Subtitle description
st.markdown("<p class='subtitle'>Explore and analyze food products through various features:</p>", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="description">
<ul>
    <li><b>🛒 Products</b>: Search for products by name or category</li>
    <li><b>📈 YourDash</b>: Track your nutritional goals and analyze geographical distribution</li>
    <li><b>🆚 Compare</b>: Compare up to 5 products side by side</li>
    <li><b>🍲 Recipes</b>: Find recipes based on ingredients</li>
    <li><b>📊 Categories</b>: Analyze trends by category</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'><br><br>In the context of the Open Data project: Brice Grivet, Maéva Maïo, Houria Sayah.</div>", unsafe_allow_html=True)
