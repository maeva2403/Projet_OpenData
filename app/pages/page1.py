import streamlit as st
import json
import os

def load_categories():
    try:
        with open('data/raw/categories.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erreur lors du chargement des catégories : {e}")
        return []

def load_products(category):
    try:
        with open(f'data/raw/products/{category}/products.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erreur lors du chargement des produits : {e}")
        return []

def show():
    st.title("Application de Recettes Alimentaires")

    # CSS personnalisé
    st.markdown("""
        <style>
            .main {
                background-color: white;
                color: black;
            }
            .separator {
                border-top: 2px solid orange;
                margin: 10px 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Chargement des catégories
    categories = load_categories()

    if categories:
        category = st.selectbox("Choisissez une catégorie", categories)
        st.write(f"Vous avez sélectionné la catégorie : {category}")

        if st.button("Afficher les produits"):
            products = load_products(category)
            if products:
                for product in products:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Nom:** {product.get('product_name', 'Inconnu')}")
                        st.write(f"**Code-barres:** {product.get('code', 'Inconnu')}")
                        st.write(f"**Lien:** [Détails du produit]({product.get('url', '#')})")
                    
                    with col2:
                        image_url = product.get('image_front_small_url', None)
                        if image_url:
                            st.image(image_url, caption=product.get('product_name', 'Inconnu'), width=150)
                        else:
                            st.write("Aucune image disponible.")
                    
                    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            else:
                st.write("Aucun produit trouvé.")
    else:
        st.write("Impossible de récupérer les catégories.")