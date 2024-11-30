# pages/3 - 🆚 Compare.py

import streamlit as st
import pandas as pd

from functions import (
    initialize_session_state, 
    show_cart_sidebar,
    create_nutrient_comparison,
    create_radar_comparison
)

initialize_session_state()
show_cart_sidebar()

st.title("🆚 Comparez vos Produits")

if len(st.session_state.selected_products) < 2:
    st.warning("Sélectionnez au moins 2 produits pour les comparer.")
else:
    # Création de deux colonnes pour la comparaison
    col1, col2 = st.columns(2)
    
    # Informations de base
    with st.container():
        for idx, product in enumerate(st.session_state.selected_products):
            with col1 if idx % 2 == 0 else col2:
                st.subheader(product.get('product_name', 'Unknown'))
                st.image(product.get('image_url', 'placeholder.png'), width=200)
                
                # Scores
                scores_col1, scores_col2, scores_col3 = st.columns(3)
                with scores_col1:
                    st.metric("Nutriscore", product.get('nutriscore_grade', '?').upper())
                with scores_col2:
                    st.metric("Ecoscore", product.get('ecoscore_grade', '?').upper())
                with scores_col3:
                    st.metric("NOVA", product.get('nova_group', '?'))
    
    # Graphiques de comparaison
    st.plotly_chart(create_nutrient_comparison(st.session_state.selected_products))
    st.plotly_chart(create_radar_comparison(st.session_state.selected_products))
    
    # Tableau comparatif détaillé
    comparison_data = []
    for product in st.session_state.selected_products:
        nutriments = product.get('nutriments', {})
        comparison_data.append({
            'Product': product.get('product_name', 'Unknown'),
            'Energy': f"{nutriments.get('energy-kcal', 0):.1f} kcal",
            'Fat': f"{nutriments.get('fat', 0):.1f}g",
            'Saturated fat': f"{nutriments.get('saturated-fat', 0):.1f}g",
            'Carbohydrates': f"{nutriments.get('carbohydrates', 0):.1f}g",
            'Sugars': f"{nutriments.get('sugars', 0):.1f}g",
            'Fiber': f"{nutriments.get('fiber', 0):.1f}g",
            'Proteins': f"{nutriments.get('proteins', 0):.1f}g",
            'Salt': f"{nutriments.get('salt', 0):.2f}g",
            'Price': product.get('price', 'N/A'),
            'Origin': product.get('origins', 'N/A'),
            'Brand': product.get('brands', 'N/A'),
            'Categories': product.get('categories', 'N/A'),
            'Labels': product.get('labels', 'N/A'),
            'Nutriscore': product.get('nutriscore_grade', '?').upper(),
            'Ecoscore': product.get('ecoscore_grade', '?').upper(),
            'NOVA': product.get('nova_group', '?')
        })
    
    st.subheader("Tableau comparatif détaillé")
    st.dataframe(pd.DataFrame(comparison_data))