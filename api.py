import requests
import pandas as pd
import streamlit as st
import time

# Fonction pour obtenir tous les produits d'une catégorie en utilisant la pagination
def get_all_products_by_category(category):
    url = f"https://world.openfoodfacts.org/category/{category}.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    products = []
    page = 1  # Commence à la première page

    while True:
        response = requests.get(f"{url}?page={page}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            new_products = data.get('products', [])
            if not new_products:  # Si aucun nouveau produit n'est trouvé, on sort de la boucle
                break
            products.extend(new_products)  # Ajoute les nouveaux produits à la liste
            page += 1  # Passe à la page suivante
        
        elif response.status_code == 429:
            st.warning("Limite de requêtes atteinte. Attente avant de réessayer...")
            time.sleep(10)  # Attendre 10 secondes avant de réessayer
        else:
            st.error(f"Erreur lors de la récupération des produits : {response.status_code}")
            break

    return products

# Configuration de l'application Streamlit
st.title("Produits Alimentaires par Catégorie")

# Obtenir tous les produits dans la catégorie "Snack"
category = "Snack"
products = get_all_products_by_category(category)

# Convertir les produits en DataFrame
df_products = pd.DataFrame(products)

# Vérifier que le DataFrame n'est pas vide
if not df_products.empty:
    # Afficher les colonnes les plus pertinentes
    df_products_filtered = df_products[["product_name", "code", "url", "quantity", "nutriments", "nutriscore_grade", "nova_group", "allergens", "labels", "countries_tags"]]

    # Afficher les premières lignes du DataFrame sur Streamlit
    st.subheader(f"Produits dans la catégorie : {category}")
    st.dataframe(df_products_filtered)  # Afficher le DataFrame dans Streamlit
else:
    st.write("Aucun produit trouvé dans cette catégorie.")
