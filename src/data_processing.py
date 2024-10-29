import requests
import streamlit as st

def get_products_by_category(category):
    url = f"https://world.openfoodfacts.org/category/{category}.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        products = response.json().get('products', [])
        if not products:
            st.warning("Aucun produit trouvé dans cette catégorie.")
        return products
    else:
        st.error(f"Erreur lors de la récupération des produits : {response.status_code}")
        return []

def get_categories():
    url = "https://world.openfoodfacts.org/categories.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        return [category['name'] for category in json_data.get('tags', [])]
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la connexion à l'API : {e}")
        return []
    except ValueError as e:
        st.error(f"Erreur lors du décodage du JSON : {e}")
        return []