# app/pages/page3.py

import streamlit as st
import pandas as pd
import re
import requests
import time

# Titre de la page
st.title("Visualisation des Données OpenFoodFacts")

# Fonction de nettoyage des préfixes
def clean_prefixes(items):
    formatted_items = []
    for item in items:
        item_cleaned = re.sub(r'^.*?:', '', item)
        formatted_item = ' '.join([part.capitalize() for part in re.split(r'[- ]', item_cleaned)])
        formatted_items.append(formatted_item.replace(" ", "-"))
    return formatted_items

# Utiliser @st.cache_data pour mettre en cache les données récupérées
@st.cache_data
def fetch_data(category):
    url = f"https://world.openfoodfacts.org/category/{category}.json"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    products = []
    page = 1  # Commence à la première page
    required_keys = [
        "product_name", "code", "quantity", "origins", "categories", 
        "countries_tags", "nutriments", "nutriscore_grade", 
        "nova_group", "nutrition_data_per", "allergens", "traces", "labels"
    ]

    while len(products) < 30 and page <= 5:  # Limite à 30 produits ou 5 pages
        try:
            response = requests.get(f"{url}?page={page}", headers=headers, timeout=10)  # Timeout de 10 secondes
            
            if response.status_code == 200:
                data = response.json()
                new_products = data.get('products', [])
                if not new_products:  # Si aucun nouveau produit n'est trouvé, sortir de la boucle
                    break
                
                for product in new_products:
                    if all(product.get(key) not in [None, ''] for key in required_keys):
                        products.append(product)
                        if len(products) >= 30:
                            break
                
                page += 1
            
            elif response.status_code == 429:
                st.warning("Limite de requêtes atteinte. Attente avant de réessayer...")
                time.sleep(10)  # Pause de 10 secondes
            elif response.status_code == 504:
                st.warning("Erreur 504 : Timeout du serveur. Réessai dans quelques secondes...")
                time.sleep(5)  # Réessayer après 5 secondes
            else:
                st.error(f"Erreur lors de la récupération des produits : {response.status_code}")
                break

        except requests.exceptions.Timeout:
            st.warning("Le délai d'attente pour la requête a été dépassé. Nouvelle tentative...")
            time.sleep(5)  # Réessayer après 5 secondes
        except requests.exceptions.RequestException as e:
            st.error(f"Une erreur réseau s'est produite : {e}")
            break

    return products[:30]

# Utiliser @st.cache_data pour mettre en cache le traitement des produits
@st.cache_data
def process_products(products):
    processed_data = []
    
    for product in products:
        product_data = {
            "product_name": product.get("product_name", "Inconnu"),
            "code": product.get("code", "Inconnu"),
            "url": product.get("url", "#"),
            "quantity": product.get("quantity", "Information non disponible"),
            "categories": product.get("categories", "Information non disponible"),
            "origins": product.get("origins", "Information non disponible"),
            "nutriscore_grade": product.get("nutriscore_grade", "Non disponible").upper(),
            "nova_group": product.get("nova_group", "Non disponible"),
            "nutrition_data_per": product.get("nutrition_data_per", "Non disponible"),
            "image_url": product.get("image_front_small_url", None)
        }
        
        # Liste des nutriments spécifiques
        selected_nutrients = [
            'carbohydrates_100g',
            'energy-kcal_100g',
            'fat_100g',
            'fiber_100g',
            'proteins_100g',
            'salt_100g',
            'saturated-fat_100g',
            'sugars_100g'
        ]

        # Extraction des nutriments
        nutriments = product.get("nutriments", {})
        for nutrient_key in selected_nutrients:
            nutrient_value = nutriments.get(nutrient_key)
            # Transforme le nom du nutriment pour le rendre plus lisible dans le DataFrame
            nutrient_name = nutrient_key.replace('_100g', '').replace('_unit', '').replace('-', ' ').capitalize()
            product_data[nutrient_name] = nutrient_value
        
        # Nettoyage des allergènes et des labels
        allergens = product.get("allergens", "")
        product_data["allergens"] = ", ".join(clean_prefixes(allergens.split(","))) if allergens else "Non disponible"
        
        labels = product.get("labels", "")
        product_data["labels"] = ", ".join(clean_prefixes(labels.split(","))) if labels else "Non disponible"

        categories = product.get("categories", "")
        product_data["categories"] = ", ".join(clean_prefixes(categories.split(","))) if categories else "Non disponible"

        origins = product.get("origins", "")
        product_data["origins"] = ", ".join(clean_prefixes(origins.split(","))) if origins else "Non disponible"
        
        # Nettoyage des pays de vente
        countries = product.get("countries_tags", [])
        product_data["countries"] = ", ".join(clean_prefixes(countries)) if countries else "Non disponible"
        
        processed_data.append(product_data)
    
    return pd.DataFrame(processed_data)

# Interface utilisateur dans Streamlit

# Liste des catégories disponibles
categories = ["Snacks", "Beverages", "Dairy", "Fruits", "Vegetables"]

# Sélection de la catégorie par l'utilisateur
selected_category = st.selectbox("Sélectionnez une catégorie", categories)

if selected_category:
    st.write(f"Chargement des produits pour la catégorie : {selected_category}...")

    # Récupérer les produits de la catégorie sélectionnée
    products = fetch_data(selected_category)
    if products:
        # Traiter les produits
        df_processed = process_products(products)
        st.write(f"Produits traités pour la catégorie : {selected_category}")
        st.dataframe(df_processed)  # Afficher tous les produits

        # Liste des colonnes disponibles pour la sélection (inclut toutes les colonnes pertinentes)
        columns_list = ['nutriscore_grade', 'nova_group'] + [
            'Carbohydrates', 'Energy kcal', 'Fat', 'Fiber', 'Proteins', 'Salt', 'Saturated fat', 'Sugars'
        ]

        # Vérifier les colonnes réellement présentes dans le DataFrame
        available_columns = [col for col in columns_list if col in df_processed.columns]

        # Sélection de la colonne pour le graphique
        selected_column = st.selectbox("Sélectionnez une colonne pour le graphique", available_columns)

        if selected_column:
            # Vérifier le type de la colonne sélectionnée
            if df_processed[selected_column].dtype in ['float64', 'int64']:
                # Colonne numérique
                # Créer un DataFrame pour le graphique
                chart_data = df_processed[['product_name', selected_column]].set_index('product_name')
                # Afficher le graphique en barres avec product_name sur l'axe x
                st.write(f"Graphique de {selected_column} par produit")
                st.bar_chart(chart_data)
            else:
                # Colonne catégorielle
                # Compter les occurrences de chaque catégorie
                category_counts = df_processed[selected_column].value_counts()
                # Créer un DataFrame pour le graphique
                chart_data = pd.DataFrame({selected_column: category_counts.index, 'Counts': category_counts.values})
                # Afficher le graphique en barres
                st.write(f"Distribution de {selected_column}")
                st.bar_chart(chart_data.set_index(selected_column))
    else:
        st.warning(f"Aucun produit trouvé pour la catégorie : {selected_category}.")
