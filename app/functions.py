# functions.py

import requests
import plotly.express as px
import pandas as pd
import time
import streamlit as st
import plotly.graph_objects as go
import re

def initialize_session_state():
    if "objectifs" not in st.session_state:
        st.session_state.objectifs = {"graisses": 70, "sucres": 50, "sel": 6, "calories": 2000}

    if "selected_products" not in st.session_state:
        st.session_state.selected_products = []

    if "show_search" not in st.session_state:
        st.session_state.show_search = False

    if "search_results" not in st.session_state:
        st.session_state.search_results = []

def show_cart_sidebar():
   with st.sidebar:
       st.subheader("Panier", anchor="cart-subheader")

       if st.session_state.selected_products:
           for index, product in enumerate(st.session_state.selected_products):
               product_name = product.get('product_name', 'Unknown')
               st.write(f"- {product_name}")

               if st.button(f"Remove {product_name}", key=f"remove_{index}", use_container_width=True):
                   st.session_state.selected_products.pop(index)
                   st.success(f"{product_name} removed from cart")
                   st.rerun()
       else:
           st.write("Your cart is empty.")
           
       if st.button("Add product", key="add_product", use_container_width=True):
           st.session_state.show_search = True
           st.switch_page("pages/1 - 🛒 Products.py")

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
@st.cache_data
def search_product_by_category(category, nb_items=20):
   url = f"https://world.openfoodfacts.org/category/{category}.json"
   headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
   }
   
   products = []
   page = 1
   page_size = 100

   while len(products) < nb_items:  
       try:
           response = requests.get(f"{url}?page={page}&page_size={page_size}", headers=headers, timeout=10)
           
           if response.status_code == 200:
               data = response.json()
               new_products = data.get('products', [])
               if not new_products:
                   break
                   
               for product in new_products:
                   if (product.get('product_name') and 
                       product.get('nutriments') and 
                       product.get('nutriscore_grade') not in [None, '', 'unknown', 'UNKNOWN'] and
                       product.get('ecoscore_grade') not in [None, '', 'unknown', 'UNKNOWN'] and
                       product.get('countries_tags') and 
                       product.get('nova_group')):
                       
                       nutriments = product.get('nutriments', {})
                       if all(nutriments.get(key) not in [None, '', 0, 'unknown', 'UNKNOWN'] 
                             for key in ["energy-kcal", "fat", "saturated-fat", "carbohydrates", 
                                       "sugars", "proteins", "salt"]):
                           products.append(product)
                           if len(products) >= nb_items:
                               break
                   
               page += 1
           else:
               break

       except:
           break

   return products[:nb_items]


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

# Fonction pour afficher la carte des pays de vente avec préfixes nettoyés
def display_sales_map(countries, zoom_country=None):
    if countries:
        # Nettoyer les pays (enlever les préfixes et capitaliser correctement)
        countries_cleaned = clean_prefixes(countries)
        
        # Créer un DataFrame avec les pays nettoyés
        df_countries = pd.DataFrame(countries_cleaned, columns=['Country'])
        
        # Utiliser Plotly pour afficher une carte choroplète des pays sélectionnés
        fig = px.choropleth(df_countries,
                            locations='Country', 
                            locationmode='country names',
                            color='Country',
                            hover_name='Country',
                            title="Pays de vente des produits sélectionnés",
                            template="plotly_white",  # Fond blanc
                            color_continuous_scale='Viridis')  # Option pour une palette moderne et colorée
        
        # Afficher la carte dans Streamlit avec une largeur maximale
        st.plotly_chart(fig, use_container_width=True)

# Récupérer et afficher les pays de vente avec préfixes nettoyés dans un tableau et sur la carte
def display_sales_info_and_map(selected_products):
    countries_list = []  # Liste pour stocker les pays de vente
    
    # Récupérer les pays de vente
    countries = []
    for product in selected_products:
        product_name = product.get('product_name', 'Inconnu')
        product_countries = product.get('countries_tags', [])
        
        if product_countries:
            countries_cleaned = clean_prefixes(product_countries)
            countries_list.append({'Product': product_name, 'Countries of Sale': ', '.join(countries_cleaned)})
            countries.extend(countries_cleaned)  # Ajouter tous les pays dans la liste des pays
        
        else:
            countries_list.append({'Product': product_name, 'Countries of Sale': 'Aucune information disponible'})
    
    # Créer un DataFrame pour le tableau des pays
    df_countries = pd.DataFrame(countries_list)
    st.subheader("Tableau des pays de vente des produits")
    st.dataframe(df_countries)
    
    # Afficher la carte des pays de vente
    display_sales_map(countries)

# Fonction pour afficher la carte des pays de vente
def display_sales_countries_table(selected_products):
    countries_list = []  # Liste pour stocker les pays de vente
    
    # Parcours de chaque produit dans le panier
    for product in selected_products:
        product_name = product.get('product_name', 'Inconnu')
        countries = product.get('countries_tags', [])
        
        if countries:
            countries_cleaned = clean_prefixes(countries)
            countries_list.append({'Product': product_name, 'Countries of Sale': ', '.join(countries_cleaned)})
        else:
            countries_list.append({'Product': product_name, 'Countries of Sale': 'Aucune information disponible'})
    
    # Créer un DataFrame à partir de la liste
    df_countries = pd.DataFrame(countries_list)

    # Afficher le tableau dans Streamlit
    st.subheader("Tableau des pays de vente des produits")
    st.dataframe(df_countries)

        
# Fonction pour générer un graphique de comparaison des nutriments avec les AJR
def plot_nutrient_journalier_plotly(selected_products, objectifs):
   ajr = {
       "Calories (kcal)": objectifs.get("calories", 2000),
       "Graisses (g)": objectifs.get("graisses", 70),
       "Graisses saturées (g)": objectifs.get("graisses_sat", 20),
       "Glucides (g)": objectifs.get("glucides", 260), 
       "Sucres (g)": objectifs.get("sucres", 50),
       "Protéines (g)": objectifs.get("proteines", 50),
       "Sel (g)": objectifs.get("sel", 6)
   }

   # Calcul des totaux
   totals = {
       "Calories": sum(p.get('nutriments', {}).get('energy-kcal', 0) for p in selected_products),
       "Graisses": sum(p.get('nutriments', {}).get('fat', 0) for p in selected_products),
       "Graisses saturées": sum(p.get('nutriments', {}).get('saturated-fat', 0) for p in selected_products),
       "Glucides": sum(p.get('nutriments', {}).get('carbohydrates', 0) for p in selected_products),
       "Sucres": sum(p.get('nutriments', {}).get('sugars', 0) for p in selected_products),
       "Protéines": sum(p.get('nutriments', {}).get('proteins', 0) for p in selected_products),
       "Sel": sum(p.get('nutriments', {}).get('salt', 0) for p in selected_products)
   }

   comparison_data = {
       "Nutriment": list(ajr.keys()),
       "Consommation Totale": list(totals.values()),
       "AJR": list(ajr.values())
   }

   df_comparison = pd.DataFrame(comparison_data)
   df_comparison_long = pd.melt(df_comparison, id_vars=["Nutriment"], 
                               value_vars=["Consommation Totale", "AJR"],
                               var_name="Type", value_name="Valeur")

   fig = px.bar(df_comparison_long, x="Nutriment", y="Valeur", color="Type", barmode="group",
                labels={"Valeur": "Quantité (en kcal OU en g)", "Nutriment": "Nutriment", "Type": "Type de valeur"},
                title="Comparaison des nutriments avec les AJR")

   fig.update_layout(
       title_font_size=18,
       title_font_family="Arial",
       title_x=0.5,
       xaxis_title_font_size=14,
       yaxis_title_font_size=14,
       xaxis_tickangle=-45,
       xaxis_title="Nutriments",
       yaxis_title="Quantité (en kcal OU en g)",
       template="plotly_white",
       barmode="group"
   )

   st.plotly_chart(fig)

def plot_nutrient_distribution_plotly(selected_products):
   nutrient_data = {
       "Energy (kcal)": 0,
       "Fat (g)": 0, 
       "Saturated Fat (g)": 0,
       "Carbohydrates (g)": 0,
       "Sugars (g)": 0,
       "Proteins (g)": 0,
       "Salt (g)": 0
   }

   for product in selected_products:
       nutriments = product.get('nutriments', {})
       nutrient_data["Energy (kcal)"] += nutriments.get('energy-kcal', 0)
       nutrient_data["Fat (g)"] += nutriments.get('fat', 0)
       nutrient_data["Saturated Fat (g)"] += nutriments.get('saturated-fat', 0)
       nutrient_data["Carbohydrates (g)"] += nutriments.get('carbohydrates', 0)
       nutrient_data["Sugars (g)"] += nutriments.get('sugars', 0)
       nutrient_data["Proteins (g)"] += nutriments.get('proteins', 0)
       nutrient_data["Salt (g)"] += nutriments.get('salt', 0)

   df = pd.DataFrame(nutrient_data, index=[0]).T
   df.columns = ["Total"]

   fig = px.bar(df, 
                x=df.index, 
                y="Total",
                color=df.index,
                title="Nutriments totaux des produits sélectionnés",
                color_discrete_sequence=["#4CAF50", "#FFC107", "#F44336", "#2196F3", "#9C27B0", "#FF9800", "#03A9F4"])

   fig.update_layout(
       title_font_size=18,
       title_font_family="Arial",
       title_x=0.5,
       xaxis_title_font_size=14,
       yaxis_title_font_size=14,
       xaxis_tickangle=-45,
       xaxis_title="Nutriments",
       yaxis_title="Quantité (en kcal OU en g)",
       template="plotly_white",
       xaxis=dict(showgrid=True, zeroline=False),
       yaxis=dict(showgrid=True, zeroline=False),
       title=dict(font=dict(color="#4CAF50"))
   )

   st.plotly_chart(fig)

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
       'A': 5, 'A-PLUS': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1,
       'a': 5, 'a-plus': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1
   }
   return score_mapping.get(str(letter).upper(), 0)

def create_radar_comparison(products):
   data = []
   
   for product in products:
       nutriscore = convert_letter_score_to_number(product.get('nutriscore_grade', 'e'))
       ecoscore = convert_letter_score_to_number(product.get('ecoscore_grade', 'e'))
       nova = product.get('nova_group', 4)
       nova_converted = 5 - ((nova - 1) * (4/3)) if nova else 0
       
       data.append({
           'Product': product.get('product_name', 'Unknown'),
           'Nutriscore': nutriscore,
           'Ecoscore': ecoscore,
           'NOVA': nova_converted
       })
   
   fig = go.Figure()
   for product in data:
       fig.add_trace(go.Scatterpolar(
           r=[product['Nutriscore'], product['Ecoscore'], product['NOVA']],
           theta=['Nutriscore', 'Ecoscore', 'NOVA'],
           fill='toself',
           name=product['Product']
       ))
       
   fig.update_layout(
       polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
       title="Comparaison des scores (5 = meilleur score)"
   )
   
   return fig

@st.cache_data
def get_recipes_by_ingredient(ingredient):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["meals"] if data["meals"] else "Aucune recette trouvée pour cet ingrédient."
    return f"Erreur : {response.status_code}"

@st.cache_data
def get_recipe_details(recipe_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={recipe_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["meals"][0] if data["meals"] else None
    return None


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
            "ecoscore_grade": product.get("ecoscore_grade", "Non disponible").upper(),
            "nova_group": product.get("nova_group", "Non disponible"),
            "nutrition_data_per": product.get("nutrition_data_per", "Non disponible"),
            "image_url": product.get("image_front_small_url", None)
        }
        
        # Liste des nutriments spécifiques
        selected_nutrients = [
            'energy-kcal_100g',
            'fat_100g',
            'saturated-fat_100g',
            'carbohydrates_100g',
            'sugars_100g',
            'fiber_100g',
            'proteins_100g',
            'salt_100g'            
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
