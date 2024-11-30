import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Initialize session state
if "objectifs" not in st.session_state:
    st.session_state.objectifs = {"graisses": 70, "sucres": 50, "sel": 6, "calories": 2000}

if "selected_products" not in st.session_state:
    st.session_state.selected_products = []

def create_nutrient_comparison(products):
    nutrients = [
        'energy-kcal', 'fat', 'saturated-fat', 'carbohydrates', 
        'sugars', 'fiber', 'proteins', 'salt'
    ]
    data = []
    
    for product in products:
        nutriments = product.get('nutriments', {})
        product_data = {
            'Product': product.get('product_name', 'Unknown'),
            **{nutrient: nutriments.get(nutrient, 0) for nutrient in nutrients}
        }
        data.append(product_data)
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    for product in df['Product'].unique():
        product_data = df[df['Product'] == product]
        fig.add_trace(go.Bar(
            name=product,
            x=nutrients,
            y=product_data[nutrients].values.flatten(),
            text=product_data[nutrients].values.flatten(),
            textposition='auto',
        ))

    fig.update_layout(
        title="Nutrients comparison per product",
        barmode='group',
        yaxis_title="Quantity",
        xaxis_title="Nutrients",
        xaxis_tickangle=-45
    )
    
    return fig

def convert_letter_score_to_number(letter):
    score_mapping = {
        'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1,
        'a': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1
    }
    return score_mapping.get(str(letter), 0)

def create_radar_comparison(products):
    data = []
    
    for product in products:
        nutriscore = convert_letter_score_to_number(product.get('nutriscore_grade', 'e'))
        ecoscore = convert_letter_score_to_number(product.get('ecoscore_grade', 'e'))
        nova = product.get('nova_group', 4)
        # Convertir NOVA sur une échelle de 5 pour correspondre aux autres scores
        nova_converted = 5 - ((nova - 1) * (4/3)) if nova else 0
        
        product_data = {
            'Product': product.get('product_name', 'Unknown'),
            'Nutriscore': nutriscore,
            'Ecoscore': ecoscore,
            'NOVA': nova_converted
        }
        data.append(product_data)
    
    fig = go.Figure()
    
    for product in data:
        fig.add_trace(go.Scatterpolar(
            r=[product['Nutriscore'], product['Ecoscore'], product['NOVA']],
            theta=['Nutriscore', 'Ecoscore', 'NOVA'],
            fill='toself',
            name=product['Product']
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        title="Comparaison des scores (5 = meilleur score)"
    )
    
    return fig

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