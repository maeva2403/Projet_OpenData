import streamlit as st
from src.data_processing import get_categories, get_products_by_category

def show():
    st.title("Application de Recettes Alimentaires")
    
    # Récupération des catégories
    categories = get_categories()
    
    # Sélection de la catégorie
    if categories:
        category = st.selectbox("Choisissez une catégorie", categories)
        st.write(f"Vous avez sélectionné la catégorie : {category}")
        
        # Bouton pour afficher les produits
        if st.button("Afficher les produits"):
            products = get_products_by_category(category)
            if products:
                for product in products:
                    st.write(f"Nom: {product.get('product_name', 'Inconnu')}")
                    st.write(f"Code-barres: {product.get('code', 'Inconnu')}")
                    st.write(f"Lien: [Détails du produit]({product.get('url', '#')})")
                    st.write("---")
    else:
        st.write("Impossible de récupérer les catégories.")