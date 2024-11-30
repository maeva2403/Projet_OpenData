# pages/1 - 🛒 Products.py

import streamlit as st
from functions import initialize_session_state, show_cart_sidebar, search_product, search_product_by_category

initialize_session_state()
show_cart_sidebar()

st.title("Recherche de Produits")

search_mode = st.radio("Mode de recherche", ["Par nom", "Par catégorie"])

if search_mode == "Par nom":
    product_search_query = st.text_input("Rechercher un produit")
    if st.button("Rechercher", key="search_by_name"):
        st.session_state.search_results = search_product(product_search_query)

else:
    category = st.selectbox("Catégorie", ["Beverages", "Snacks", "Pastas", "Fruits", "Cereals and potatos", "Vegetables", "Water"])
    if st.button("Rechercher", key="search_by_category"):
        st.session_state.search_results = search_product_by_category(category)

if st.session_state.search_results:
    columns = st.columns(3)
    for index, product in enumerate(st.session_state.search_results[:10]):
        with columns[index % 3]:
            product_name = product.get('product_name', 'Inconnu')
            st.write(f"### {product_name}")
            
            if image_url := product.get('image_url'):
                st.image(image_url, width=150)
            
            if st.button(f"Ajouter {product_name}", key=f"add_product_{index}", use_container_width=True):
                if len(st.session_state.selected_products) < 5:
                    st.session_state.selected_products.append(product)
                    st.success(f"{product_name} ajouté")
                    st.rerun()
                else:
                    st.warning("Maximum 5 produits")
                    st.rerun()