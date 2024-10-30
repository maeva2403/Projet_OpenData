import streamlit as st
import requests
import re

# Fonction pour obtenir les produits par catégorie
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

# Fonction pour obtenir les catégories disponibles
def get_categories():
    url = "https://world.openfoodfacts.org/categories.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lancer une erreur pour les codes de statut non 200
        json_data = response.json()
        return [category['name'] for category in json_data.get('tags', [])]  # Utilisation de 'tags'
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la connexion à l'API : {e}")
        return []
    except ValueError as e:
        st.error(f"Erreur lors du décodage du JSON : {e}")
        return []

# Fonction pour nettoyer les préfixes et formater chaque mot avec la première lettre en majuscule
def clean_prefixes(items):
    formatted_items = []
    for item in items:
        item_cleaned = re.sub(r'^.*?:', '', item)  # Retirer le préfixe avant ':'
        formatted_item = ' '.join([part.capitalize() for part in re.split(r'[- ]', item_cleaned)])  # Capitaliser chaque sous-partie
        formatted_item = formatted_item.replace(" ", "-")  # Remettre les tirets
        formatted_items.append(formatted_item)
    return formatted_items

# Liste des nutriments spécifiques à afficher
selected_nutrients = [
    'carbohydrates_100g', 'carbohydrates_unit',
    'energy-kcal_100g', 'energy-kcal_unit',
    'fat_100g', 'fat_unit',
    'fiber_100g', 'fiber_unit',
    'proteins_100g', 'proteins_unit',
    'salt_100g', 'salt_unit',
    'saturated-fat_100g', 'saturated-fat_unit',
    'sugars_100g', 'sugars_unit'
]

# Interface utilisateur
st.title("Application de Recettes Alimentaires")

# Ajouter du CSS pour la personnalisation
st.markdown("""
    <style>
        .main {
            background-color: white;  /* Fond blanc */
            color: black;              /* Texte noir */
        }
        .separator {
            border-top: 2px solid orange;  /* Séparateur orange */
            margin: 10px 0;                /* Espacement autour du séparateur */
        }
    </style>
""", unsafe_allow_html=True)

# Récupération des catégories
categories = get_categories()

# Sélection de la catégorie
if categories:
    category = st.selectbox("Choisissez une catégorie", categories)
    st.write(f"Vous avez sélectionné la catégorie : {category}")

    # Zone de texte pour la recherche de produit
    search_query = st.text_input("Recherchez un produit par son nom", "")

    # Bouton pour afficher les produits
    if st.button("Afficher les produits"):
        products = get_products_by_category(category)
        
        # Filtrer les produits en fonction de la requête de recherche
        if search_query:
            products = [p for p in products if search_query.lower() in p.get('product_name', '').lower()]

        if products:
            for product in products:
                # Créer deux colonnes pour le nom, code-barres et lien, et l'image
                col1, col2 = st.columns([2, 1])  # Ratio de 2:1 pour les colonnes

                with col1:
                    st.write(f"**Nom :** {product.get('product_name', 'Inconnu')}")
                    st.write(f"**Code-barres :** {product.get('code', 'Inconnu')}")
                    st.write(f"**Lien :** [Détails du produit]({product.get('url', '#')})")  # Lien vers la page du produit

                    # Afficher la quantité du produit
                    quantity = product.get('quantity', 'Information non disponible')
                    st.write(f"**Quantité :** {quantity}")

                    # Afficher les origines
                    origins = product.get('origins', 'Information non disponible')
                    st.write(f"**Origines :** {origins}")

                    # Afficher les nutriments sélectionnés uniquement
                    nutriments = product.get('nutriments', {})
                    if nutriments:
                        st.write("**Nutriments :**")
                        for nutrient_key in selected_nutrients:
                            nutrient_value = nutriments.get(nutrient_key)
                            if nutrient_value is not None:
                                nutrient_name = nutrient_key.replace('_100g', '').replace('_unit', '').replace('-', ' ').capitalize()
                                st.write(f"- {nutrient_name}: {nutrient_value}")
                    else:
                        st.write("**Nutriments :** Information non disponible")

                    # Afficher le Nutri-Score
                    nutriscore_grade = product.get('nutriscore_grade', 'Non disponible')
                    st.write(f"**Nutri-Score :** {nutriscore_grade.upper()}")

                    # Afficher le NOVA Group
                    nova_group = product.get('nova_group', 'Non disponible')
                    st.write(f"**NOVA Group :** {nova_group}")

                    # Afficher les données nutritionnelles par portion
                    nutrition_data_per = product.get('nutrition_data_per', 'Non disponible')
                    st.write(f"**Données nutritionnelles par :** {nutrition_data_per}")

                    # Afficher les allergènes avec préfixes nettoyés
                    allergens = product.get('allergens', '')
                    if allergens:
                        allergens_cleaned = clean_prefixes(allergens.split(','))
                        st.write(f"**Allergènes :** {', '.join(allergens_cleaned)}")
                    else:
                        st.write("**Allergènes :** Information non disponible.")

                    # Afficher les labels avec préfixes nettoyés
                    labels = product.get('labels', '')
                    if labels:
                        labels_cleaned = clean_prefixes(labels.split(','))
                        st.write(f"**Labels :** {', '.join(labels_cleaned)}")
                    else:
                        st.write("**Labels :** Information non disponible.")

                    # Récupérer et afficher les pays de vente avec préfixes nettoyés
                    countries = product.get('countries_tags', [])
                    if countries:
                        countries_cleaned = clean_prefixes(countries)
                        st.write(f"**Pays de vente :** {', '.join(countries_cleaned)}")
                    else:
                        st.write("**Pays de vente :** Aucune information disponible.")

                with col2:
                    # Afficher l'image du produit
                    image_url = product.get('image_front_small_url', None)  # Récupérer l'URL de l'image
                    if image_url:
                        st.image(image_url, caption=product.get('product_name', 'Inconnu'), width=150)  # Spécifiez la largeur ici
                    else:
                        st.write("Aucune image disponible.")
                
                st.markdown('<div class="separator"></div>', unsafe_allow_html=True)  # Traîter séparateur
        else:
            st.write("Aucun produit trouvé.")
else:
    st.write("Impossible de récupérer les catégories.")
