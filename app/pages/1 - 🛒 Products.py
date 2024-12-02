# pages/1 - 🛒 Products.py

import streamlit as st
from functions import initialize_session_state, show_cart_sidebar, search_product, search_product_by_category

# Initialize the session state
initialize_session_state()

# Display the cart sidebar
show_cart_sidebar()

# Main title of the page
st.markdown("<h1 class='title'>🛒 Product Search</h1>", unsafe_allow_html=True)

# Subtitle description
st.markdown("<p class='subtitle'>Find and add your favorite products to the cart</p>", unsafe_allow_html=True)

# Search mode selection
st.markdown("<label class='input-label'>Search Mode</label>", unsafe_allow_html=True)
search_mode = st.radio("", ["🔍 By name", "📂 By category"], horizontal=True)

# Handling "By name" search mode
if search_mode == "🔍 By name":
    product_search_query = st.text_input("Enter product name")
    if st.button("Search", key="search_by_name"):
        st.session_state.search_results = search_product(product_search_query)

# Handling "By category" search mode
elif search_mode == "📂 By category":
    category = st.selectbox(
        "Select a category", 
        ["Snacks", "Cereals and Potatoes", "Fruits", "Vegetables", "Dairy", "Beverages", "Waters"]
    )
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
        color: #333333;
        font-size: 1.3em;
        text-align: center;
        font-family: Arial, sans-serif;
        margin-bottom: 20px;
    }
    .input-label {
        color: #FF6F3C;
        font-size: 1.2em;
        font-weight: bold;
        font-family: Arial, sans-serif;
        margin-bottom: 10px;
    }
    .product-card {
        background-color: #FF6F3C;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    }
    .add-button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        margin-top: 15px;
    }
    .add-button:hover {
        background-color: #66BB6A;
        color: white;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True
)