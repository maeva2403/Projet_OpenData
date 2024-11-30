# pages/0_🏠_Home Page.py

import streamlit as st

from functions import initialize_session_state, show_cart_sidebar # etc...

initialize_session_state()
show_cart_sidebar()

# Reste du code spécifique à la page

st.title("📊 Food Analysis Dashboard")

# Introduction
st.markdown("""
Explorez et analysez les produits alimentaires à travers différentes fonctionnalités:
- **🛒 Products**: Recherchez des produits par nom ou catégorie
- **📈 YourDash**:Suivez vos objectifs nutritionnels et analysez la répartition géographique
- **🆚 Compare**: Comparez jusqu'à 5 produits côte à côte
- **🍲 Recipes**: Trouvez des recettes à partir d'ingrédients
- **📊 Categories**: Analysez les tendances par catégorie
- **🌐 Global**: Vue d'ensemble des données mondiales
""")