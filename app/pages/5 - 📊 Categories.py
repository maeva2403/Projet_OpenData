# pages/5 - 📊 Categories.py

import streamlit as st
import plotly.express as px
import pandas as pd
from functions import (
   initialize_session_state, 
   show_cart_sidebar,
   search_product_by_category,
   process_products
)

# Initialize session state and sidebar
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
    </style>
    """, unsafe_allow_html=True
)

# Title of the page
st.markdown("<h1 class='title'>📊 Category Visualization</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Explore trends and visualize product data by category</p>", unsafe_allow_html=True)

# List of available categories
categories = ["Snacks", "Cereals and Potatoes", "Fruits", "Vegetables", "Dairy", "Beverages", "Waters"]

# Dropdown for category selection
st.markdown("<label class='input-label'>Select a category</label>", unsafe_allow_html=True)
selected_category = st.selectbox("", categories)

# Number input for number of items to display
st.markdown("<label class='input-label'>Number of products to display</label>", unsafe_allow_html=True)
nb_items = st.number_input("", min_value=10, max_value=100, value=20, step=5)

if selected_category:
   st.markdown(f"<p class='subtitle'>Loading products for category: {selected_category}...</p>", unsafe_allow_html=True)
   
   # Search for products by selected category and number of items
   products = search_product_by_category(selected_category, nb_items)
   
   if products:
       # Process the products and convert them into a dataframe
       df_processed = process_products(products)
       # Ensure the 'nova_group' column is treated as a string for proper display
       if 'nova_group' in df_processed.columns:
           df_processed['nova_group'] = df_processed['nova_group'].astype(str)
           
       st.markdown(f"<p class='subtitle'>Processed products for category: {selected_category}</p>", unsafe_allow_html=True)
       st.dataframe(df_processed)

       # List of columns available for graphing
       columns_list = ['nutriscore_grade', 'ecoscore_grade', 'nova_group'] + [
           'Energy kcal', 'Fat', 'Saturated fat', 'Carbohydrates', 
           'Sugars', 'Fiber', 'Proteins', 'Salt'
       ]
       # Check which columns are available in the processed dataframe
       available_columns = [col for col in columns_list if col in df_processed.columns]
       
       # Dropdown for variable selection
       st.markdown("<label class='input-label'>Select a variable for the chart</label>", unsafe_allow_html=True)
       selected_column = st.selectbox("", available_columns)

       if selected_column:
           if selected_column in ['nutriscore_grade', 'ecoscore_grade', 'nova_group']:
               # Create a bar chart for categorical columns (e.g., NutriScore, EcoScore, NOVA group)
               category_counts = df_processed[selected_column].value_counts()
               
               # Define custom order and colors for NOVA and NutriScore categories
               if selected_column == 'nova_group':
                   custom_order = ['1', '2', '3', '4']
                   color_scale = ['#27ae60', '#f1c40f', '#e67e22', '#c0392b']
               else:
                   custom_order = ['A-PLUS', 'A', 'B', 'C', 'D', 'E', 'F']
                   color_scale = ['#27ae60', '#2ecc71', '#f1c40f', '#f39c12', 
                               '#e67e22', '#d35400', '#c0392b']
               
               # Reorder the counts to ensure proper display
               ordered_counts = pd.Series(dtype='float64')
               for cat in custom_order:
                   if cat in category_counts.index:
                       ordered_counts[cat] = category_counts[cat]
               for cat in category_counts.index:
                   if cat not in custom_order:
                       ordered_counts[cat] = category_counts[cat]
                       
               # Plotting the bar chart
               fig = px.bar(ordered_counts,
                           title=f"Distribution of {selected_column}",
                           labels={'value': 'Product Quantity',
                                 'index': selected_column},
                           color=ordered_counts.index,
                           color_discrete_sequence=color_scale)
           else:
               # Sort the dataframe by the selected numerical column (e.g., Fat, Sugars, Energy)
               df_sorted = df_processed.sort_values(by=selected_column, ascending=False)
               # Create a bar chart for numerical columns
               fig = px.bar(df_sorted, x='product_name', y=selected_column,
                           title=f"Content of {selected_column}",
                           labels={'product_name': 'Products',
                                 selected_column: 'Amount in kcal' if selected_column == 'Energy kcal' 
                                               else 'Amount in g'},
                           color=selected_column,
                           color_continuous_scale='RdBu_r')

           # Rotate x-axis labels for better readability
           fig.update_layout(xaxis_tickangle=-45, showlegend=False)
           # Display the plot
           st.plotly_chart(fig)
   else:
       st.warning(f"No products found for category: {selected_category}.")
