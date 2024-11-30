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

initialize_session_state()
show_cart_sidebar()

st.title("Visualisation des Données OpenFoodFacts")

categories = ["Snacks", "Beverages", "Dairy", "Fruits", "Vegetables"]
selected_category = st.selectbox("Sélectionnez une catégorie", categories)

# Ajout du nombre d'items à afficher
nb_items = st.number_input("Nombre de produits à afficher", min_value=10, max_value=100, value=20, step=5)

if selected_category:
   st.write(f"Chargement des produits pour la catégorie : {selected_category}...")
   products = search_product_by_category(selected_category, nb_items)
   
   if products:
       df_processed = process_products(products)
       if 'nova_group' in df_processed.columns:
           df_processed['nova_group'] = df_processed['nova_group'].astype(str)
           
       st.write(f"Produits traités pour la catégorie : {selected_category}")
       st.dataframe(df_processed)

       columns_list = ['nutriscore_grade', 'ecoscore_grade', 'nova_group'] + [
           'Energy kcal', 'Fat', 'Saturated fat', 'Carbohydrates', 
           'Sugars', 'Fiber', 'Proteins', 'Salt'
       ]
       available_columns = [col for col in columns_list if col in df_processed.columns]
       selected_column = st.selectbox("Sélectionnez une variable pour le graphique", available_columns)

       if selected_column:
           if selected_column in ['nutriscore_grade', 'ecoscore_grade', 'nova_group']:
               category_counts = df_processed[selected_column].value_counts()
               
               if selected_column == 'nova_group':
                   custom_order = ['1', '2', '3', '4']
                   color_scale = ['#27ae60', '#f1c40f', '#e67e22', '#c0392b']
               else:
                   custom_order = ['A-PLUS', 'A', 'B', 'C', 'D', 'E', 'F']
                   color_scale = ['#27ae60', '#2ecc71', '#f1c40f', '#f39c12', 
                               '#e67e22', '#d35400', '#c0392b']
               
               ordered_counts = pd.Series(dtype='float64')
               for cat in custom_order:
                   if cat in category_counts.index:
                       ordered_counts[cat] = category_counts[cat]
               for cat in category_counts.index:
                   if cat not in custom_order:
                       ordered_counts[cat] = category_counts[cat]
                       
               fig = px.bar(ordered_counts,
                           title=f"Distribution de {selected_column}",
                           labels={'value': 'Quantité de produits',
                                 'index': selected_column},
                           color=ordered_counts.index,
                           color_discrete_sequence=color_scale)
           else:
               df_sorted = df_processed.sort_values(by=selected_column, ascending=False)
               fig = px.bar(df_sorted, x='product_name', y=selected_column,
                           title=f"Apports de {selected_column}",
                           labels={'product_name': 'Produits',
                                 selected_column: 'Quantité en kcal' if selected_column == 'Energy kcal' 
                                               else 'Quantité en g'},
                           color=selected_column,
                           color_continuous_scale='RdBu_r')

           fig.update_layout(xaxis_tickangle=-45, showlegend=False)
           st.plotly_chart(fig)
   else:
       st.warning(f"Aucun produit trouvé pour la catégorie : {selected_category}.")