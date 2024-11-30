import streamlit as st
import requests
import time
import pandas as pd
import re
import os
from pathlib import Path

# Utiliser @st.cache_data pour mettre en cache les données traitées
@st.cache_data
def fetch_data(category):
    url = f"https://world.openfoodfacts.org/category/{category}.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
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
            response = requests.get(f"{url}?page={page}", headers=headers, timeout=10)
            
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


# Fonction de nettoyage des préfixes
def clean_prefixes(items):
    formatted_items = []
    for item in items:
        item_cleaned = re.sub(r'^.*?:', '', item)
        formatted_item = ' '.join([part.capitalize() for part in re.split(r'[- ]', item_cleaned)])
        formatted_items.append(formatted_item.replace(" ", "-"))
    return formatted_items


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


def get_category_data(category):
    # Nom du fichier CSV pour la catégorie
    csv_file = f"{category}.csv"
    
    if os.path.exists(csv_file):
        st.write(f"Chargement des données depuis le fichier CSV pour la catégorie : {category}")
        df_processed = pd.read_csv(csv_file)
    else:
        st.write(f"Téléchargement et traitement des données pour la catégorie : {category}")
        products = fetch_data(category)
        if products:
            df_processed = process_products(products)
            # Enregistrement du DataFrame dans un fichier CSV
            df_processed.to_csv(csv_file, index=False)
            st.write(f"Données enregistrées dans le fichier : {csv_file}")
        else:
            st.warning(f"Aucun produit trouvé pour la catégorie : {category}.")
            df_processed = pd.DataFrame()  # DataFrame vide si aucun produit
    return df_processed

# Interface utilisateur dans Streamlit
categories = ["Snacks", "Beverages", "Dairy", "Fruits", "Vegetables"]
for category in categories:
    df_processed = get_category_data(category)
    if not df_processed.empty:
        st.write(f"Produits traités pour la catégorie : {category}")
        st.dataframe(df_processed)  # Afficher le DataFrame traité
    else:
        st.warning(f"Aucune donnée disponible pour la catégorie : {category}.")
