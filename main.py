import streamlit as st
from pages import page1

st.set_page_config(page_title="Application Recettes", layout="wide")

# Menu dans la sidebar
page = st.sidebar.selectbox(
    "Navigation",
    ["Recherche de Produits"]
)

# Affichage de la page
if page == "Recherche de Produits":
    page1.show()