import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# Fonction pour obtenir un produit par recherche par nom
def search_product(query):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('products', [])
    else:
        st.error(f"Erreur lors de la recherche de produit : {response.status_code}")
        return []

# Fonction pour obtenir des produits par catégorie
def search_product_by_category(category):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?categories={category}&action=process&json=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('products', [])
    else:
        st.error(f"Erreur lors de la recherche de produits dans la catégorie {category} : {response.status_code}")
        return []

# Fonction pour nettoyer les préfixes et formater chaque mot avec la première lettre en majuscule
def clean_prefixes(items):
    formatted_items = []
    for item in items:
        # Retirer tout préfixe avant ':'
        item_cleaned = re.sub(r'^.*?:', '', item)
        # Capitaliser chaque sous-partie
        formatted_item = ' '.join([part.capitalize() for part in re.split(r'[- ]', item_cleaned)])
        # Remettre les tirets pour avoir le bon format de pays
        formatted_item = formatted_item.replace(" ", "-")
        formatted_items.append(formatted_item)
    return formatted_items

# Fonction pour afficher la carte des pays de vente
def display_sales_map(countries):
    if countries:
        # Nettoyer les préfixes
        countries_cleaned = clean_prefixes(countries)
        
        # Créer un DataFrame avec les pays nettoyés
        df_countries = pd.DataFrame(countries_cleaned, columns=['Country'])
        
        # Utiliser Plotly pour afficher une carte choroplète
        fig = px.choropleth(df_countries,
                            locations='Country', 
                            locationmode='country names',
                            color='Country',
                            hover_name='Country',
                            title="Pays de vente des produits",
                            template="plotly_white")
        
        fig.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="lightgray")
        fig.update_layout(title="Carte des pays de vente des produits", title_x=0.5, title_font_size=18)
        
        st.plotly_chart(fig)
    else:
        st.write("Aucune information sur les pays de vente.")
        
# Fonction pour générer un graphique de comparaison des nutriments avec les AJR
def plot_nutrient_journalier_plotly(selected_products, objectifs):
    # Recommandations journalières par défaut (AJR)
    ajr = {
        "Graisses (g)": objectifs.get("graisses", 70),
        "Sucres (g)": objectifs.get("sucres", 50),
        "Sel (g)": objectifs.get("sel", 6),
        "Calories (kcal)": objectifs.get("calories", 2000)
    }

    # Calcul des valeurs totales pour chaque nutriment
    total_fat = sum(product.get('nutriments', {}).get('fat', 0) for product in selected_products)
    total_sugars = sum(product.get('nutriments', {}).get('sugars', 0) for product in selected_products)
    total_salt = sum(product.get('nutriments', {}).get('salt', 0) for product in selected_products)
    total_calories = sum(product.get('nutriments', {}).get('energy-kcal', 0) for product in selected_products)

    # Création des données pour le graphique
    comparison_data = {
        "Nutriment": ["Graisses (g)", "Sucres (g)", "Sel (g)", "Calories (kcal)"],
        "Consommation Totale": [total_fat, total_sugars, total_salt, total_calories],
        "AJR": [ajr["Graisses (g)"], ajr["Sucres (g)"], ajr["Sel (g)"], ajr["Calories (kcal)"]]
    }

    # Convertir en DataFrame
    df_comparison = pd.DataFrame(comparison_data)

    # Convertir en format long pour plotly (idéal pour les barres groupées)
    df_comparison_long = pd.melt(df_comparison, id_vars=["Nutriment"], value_vars=["Consommation Totale", "AJR"],
                                 var_name="Type", value_name="Valeur")

    # Créer un histogramme avec Plotly
    fig = px.bar(df_comparison_long, x="Nutriment", y="Valeur", color="Type", barmode="group",
                 labels={"Valeur": "Quantité (g ou kcal)", "Nutriment": "Nutriment", "Type": "Type de valeur"},
                 title="Comparaison des nutriments avec les recommandations journalières")

    # Personnaliser l'apparence du graphique
    fig.update_layout(
        title="Comparaison des nutriments avec les recommandations journalières (AJR)",
        title_font_size=18,
        title_font_family="Arial",
        title_x=0.5,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        xaxis_tickangle=-45,
        xaxis_title="Nutriments",
        yaxis_title="Quantité (g ou kcal)",
        template="plotly_white",
        barmode="group"
    )

    # Afficher le graphique
    st.plotly_chart(fig)

def plot_nutrient_distribution_plotly(selected_products):
    # Logique pour calculer les nutriments et afficher le graphique
    nutrient_data = {
        "Fat (g)": 0,
        "Carbohydrates (g)": 0,
        "Sugars (g)": 0,
        "Salt (g)": 0
    }

    total_calories = 0  # Initialisation de la somme des calories

    for product in selected_products:
        nutriments = product.get('nutriments', {})
        nutrient_data["Fat (g)"] += nutriments.get('fat', 0)
        nutrient_data["Carbohydrates (g)"] += nutriments.get('carbohydrates', 0)
        nutrient_data["Sugars (g)"] += nutriments.get('sugars', 0)
        nutrient_data["Salt (g)"] += nutriments.get('salt', 0)
        
        # Ajout des calories du produit à la somme
        total_calories += nutriments.get('energy-kcal', 0)

    # Convertir les données en DataFrame pour utilisation avec Plotly
    df = pd.DataFrame(nutrient_data, index=[0])  # Une seule ligne représentant la somme totale
    df = df.T  # Transposer pour avoir les nutriments sur l'axe X
    df.columns = ["Total (g)"]

    # Créer un graphique en barres interactif avec Plotly
    fig = px.bar(df, 
                 x=df.index, 
                 y="Total (g)", 
                 color=df.index, 
                 labels={"Total (g)": "Quantité totale", "index": "Nutriments"},
                 title="Somme Totale des Nutriments pour les produits sélectionnés",
                 color_discrete_sequence=["#4CAF50", "#FFC107", "#F44336", "#2196F3"])

    fig.update_layout(
        title_font_size=18,
        title_font_family="Arial",
        title_x=0.5,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        xaxis_tickangle=-45,
        xaxis_title="Nutriments",
        yaxis_title="Quantité totale (par 100g)",
        template="plotly_white",
        xaxis=dict(showgrid=True, zeroline=False),
        yaxis=dict(showgrid=True, zeroline=False),
        title=dict(font=dict(color="#4CAF50"))
    )

    st.plotly_chart(fig)
    st.markdown(f"### Somme des énergies: {total_calories:.2f} kcal", unsafe_allow_html=True)

# Interface utilisateur
st.title("Votre tableau de bord nutritionnel")

# Initialiser les variables dans session_state si elles n'existent pas
if "objectifs" not in st.session_state:
    st.session_state.objectifs = {"graisses": 70, "sucres": 50, "sel": 6, "calories": 2000}

if "selected_products" not in st.session_state:
    st.session_state.selected_products = []

# Initialisation de "show_search" dans session_state si elle n'existe pas encore
if "show_search" not in st.session_state:
    st.session_state.show_search = False

# Initialisation de "search_results" dans session_state si elle n'existe pas encore
if "search_results" not in st.session_state:
    st.session_state.search_results = []

with st.sidebar:
    st.subheader("Panier", anchor="cart-subheader")
    if st.session_state.selected_products:
        for index, product in enumerate(st.session_state.selected_products):
            product_name = product.get('product_name', 'Inconnu')
            st.write(f"- {product_name}")
            if st.button(f"Supprimer {product_name}", key=f"remove_{index}", use_container_width=True):
                st.session_state.selected_products.pop(index)
                st.success(f"{product_name} supprimé de votre panier")
                break
    else:
        st.write("Votre panier est vide.")
    show_search_button = st.button("Ajouter un produit", use_container_width=True, key="add-product")
    if show_search_button:
        st.session_state.show_search = True

# Colonne principale - Objectifs et statistiques
if st.session_state.show_search:
    # Utiliser une seule colonne pour la recherche de produit
    st.header("Rechercher un produit", anchor="search-header")
    close_search_button = st.button("❌ Fermer la recherche", key="close_search", use_container_width=True)
    if close_search_button:
        st.session_state.show_search = False

    # Sélection du mode de recherche
    search_mode = st.radio("Choisissez un mode de recherche", ["Par nom", "Par catégorie"])
    
    if search_mode == "Par nom":
        product_search_query = st.text_input("Rechercher un produit")
        if st.button("Rechercher", key="search_by_name"):
            st.session_state.search_results = search_product(product_search_query)
    
    elif search_mode == "Par catégorie":
        category = st.selectbox("Choisissez une catégorie", 
                                ["Beverages", "Snacks", "Pastas", "Fruits", 
                                 "Cereals and potatos", "Vegetables", "Water"])
        if st.button("Rechercher", key="search_by_category"):
            st.session_state.search_results = search_product_by_category(category)
    
    # Affichage des résultats avec plusieurs produits par ligne
    if st.session_state.search_results:
        # Créer un nombre de colonnes par ligne (par exemple 3 produits par ligne)
        num_columns = 3  # Nombre de produits par ligne
        columns = st.columns(num_columns)
        
        # Affichage des produits avec une marge en bas
        for index, product in enumerate(st.session_state.search_results[:10]):
            product_name = product.get('product_name', 'Inconnu')
            image_url = product.get('image_url', None)
            
            # Placer les produits dans les colonnes
            col = columns[index % num_columns]  # Distribution des produits sur les colonnes
            
            with col:
                # Afficher le nom du produit
                st.write(f"### {product_name}")
                
                # Vérifier si l'URL de l'image existe et afficher l'image
                if image_url:
                    # Afficher l'image avec une taille fixe de 150px de largeur
                    st.image(image_url, caption=product_name, use_column_width=False, width=150)  # Redimensionner l'image
                else:
                    st.write("Aucune image disponible.")
                
                # Ajouter un bouton pour ajouter le produit au panier
                button_key = f"add_product_{index}"
                if st.button(f"Ajouter {product_name}", key=button_key, use_container_width=True):
                    if len(st.session_state.selected_products) < 5:
                        st.session_state.selected_products.append(product)
                        st.success(f"{product_name} ajouté à votre panier")
                    else:
                        st.warning("Vous pouvez ajouter jusqu'à 5 produits uniquement.")

                # Ajout d'une marge en bas pour garantir un alignement uniforme
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # Marge en bas

else:
    # Affichage des statistiques si des produits sont dans le panier
    if st.session_state.selected_products:
        col1, col2 = st.columns([1, 3])  # Retour à deux colonnes pour les statistiques
        
        with col1:
            st.subheader("Objectifs Journaliers")
            graisses = st.number_input("Graisses (g)", min_value=0, max_value=200, value=st.session_state.objectifs["graisses"], step=1)
            sucres = st.number_input("Sucres (g)", min_value=0, max_value=100, value=st.session_state.objectifs["sucres"], step=1)
            sel = st.number_input("Sel (g)", min_value=0.0, max_value=20.0, value=float(st.session_state.objectifs["sel"]), step=0.1)
            calories = st.number_input("Calories (kcal)", min_value=0, max_value=5000, value=st.session_state.objectifs["calories"], step=50)
            
            # Mettre à jour les objectifs dans la session
            st.session_state.objectifs["graisses"] = graisses
            st.session_state.objectifs["sucres"] = sucres
            st.session_state.objectifs["sel"] = sel
            st.session_state.objectifs["calories"] = calories

        with col2:
            plot_nutrient_distribution_plotly(st.session_state.selected_products)
            plot_nutrient_journalier_plotly(st.session_state.selected_products, st.session_state.objectifs)
 

st.markdown("""
    <style>
        #dashboard-title {
            font-size: 32px;
            color: #4CAF50;
            text-align: center; /* Centrer le texte */
            margin-bottom: 20px;
        }
        .css-1v3fvcr {
            background-color: #4CAF50;
            color: white;
        }
        .css-1v3fvcr:hover {
            background-color: #388E3C;
        }
        .css-12ttj6n {
            font-size: 22px;
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)
