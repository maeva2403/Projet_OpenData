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

# Title of the page
st.title("Category Visualization")

# List of available categories
categories = ["Snacks", "Cereals and Potatoes", "Fruits", "Vegetables", "Dairy", "Beverages", "Waters"]
# User selects a category from the dropdown
selected_category = st.selectbox("Select a category", categories)

# Input for the number of items to display
nb_items = st.number_input("Number of products to display", min_value=10, max_value=100, value=20, step=5)

if selected_category:
   st.write(f"Loading products for category: {selected_category}...")
   # Search for products by selected category and number of items
   products = search_product_by_category(selected_category, nb_items)
   
   if products:
       # Process the products and convert them into a dataframe
       df_processed = process_products(products)
       # Ensure the 'nova_group' column is treated as a string for proper display
       if 'nova_group' in df_processed.columns:
           df_processed['nova_group'] = df_processed['nova_group'].astype(str)
           
       st.write(f"Processed products for category: {selected_category}")
       st.dataframe(df_processed)

       # List of columns available for graphing
       columns_list = ['nutriscore_grade', 'ecoscore_grade', 'nova_group'] + [
           'Energy kcal', 'Fat', 'Saturated fat', 'Carbohydrates', 
           'Sugars', 'Fiber', 'Proteins', 'Salt'
       ]
       # Check which columns are available in the processed dataframe
       available_columns = [col for col in columns_list if col in df_processed.columns]
       # Let the user select a column for plotting
       selected_column = st.selectbox("Select a variable for the chart", available_columns)

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
