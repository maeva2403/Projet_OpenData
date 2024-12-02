# pages/1 - 🛒 Products.py

import streamlit as st
from functions import initialize_session_state, show_cart_sidebar, search_product, search_product_by_category

# Initialize the session state
initialize_session_state()

# Display the cart sidebar
show_cart_sidebar()

# Set the title for the page
st.title("Product Search")

# Option for selecting the search mode
search_mode = st.radio("Search Mode", ["By name", "By category"])

# If the user selects "By name" mode
if search_mode == "By name":
    product_search_query = st.text_input("Search for a product")
    if st.button("Search", key="search_by_name"):
        st.session_state.search_results = search_product(product_search_query)

# If the user selects "By category" mode
else:
    category = st.selectbox("Category", ["Snacks", "Cereals and Potatoes", "Fruits", "Vegetables", "Dairy", "Beverages", "Waters"])
    if st.button("Search", key="search_by_category"):
        st.session_state.search_results = search_product_by_category(category)

# If there are search results, display them
if st.session_state.search_results:
    columns = st.columns(3)
    for index, product in enumerate(st.session_state.search_results[:10]):
        with columns[index % 3]:
            product_name = product.get('product_name', 'Unknown')
            st.write(f"### {product_name}")
            
            if image_url := product.get('image_url'):
                st.image(image_url, width=150)
            
            # Button to add the product to the cart
            if st.button(f"Add {product_name}", key=f"add_product_{index}", use_container_width=True):
                if len(st.session_state.selected_products) < 5:
                    st.session_state.selected_products.append(product)
                    st.success(f"{product_name} added")
                    st.rerun()
                else:
                    st.warning("Maximum 5 products")
                    st.rerun()
