import streamlit as st
import requests

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
        # Récupérer les noms des catégories à partir de 'tags'
        return [category['name'] for category in json_data.get('tags', [])]  # Utilisation de 'tags'
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la connexion à l'API : {e}")
        return []
    except ValueError as e:
        st.error(f"Erreur lors du décodage du JSON : {e}")
        return []

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

    # Bouton pour afficher les produits
    if st.button("Afficher les produits"):
        products = get_products_by_category(category)
        if products:
            for product in products:
                # Créer deux colonnes pour le nom, code-barres et lien, et l'image
                col1, col2 = st.columns([2, 1])  # Ratio de 2:1 pour les colonnes

                with col1:
                    st.write(f"**Nom:** {product.get('product_name', 'Inconnu')}")
                    st.write(f"**Code-barres:** {product.get('code', 'Inconnu')}")
                    st.write(f"**Lien:** [Détails du produit]({product.get('url', '#')})")  # Lien vers la page du produit
                
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
