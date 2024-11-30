# pages/4 - 🍲 Recipes.py

import streamlit as st
import requests

from functions import initialize_session_state, show_cart_sidebar, get_recipes_by_ingredient, get_recipe_details


# Interface utilisateur avec Streamlit
st.set_page_config(page_title="Générateur de Recettes", page_icon="🍲", layout="wide")

initialize_session_state()
show_cart_sidebar()

# Styles de la page avec CSS intégré pour les couleurs pastel
st.markdown(
    """
    <style>
    .title {
        color: #FF6F3C;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        font-family: Arial, sans-serif;
    }
    .subtitle {
        color: #FF8552;
        font-size: 1.3em;
        text-align: center;
        font-family: Arial, sans-serif;
        margin-bottom: 20px;
    }
    .input-label {
        color: #FF6F3C;
        font-size: 1.2em;
        font-weight: bold;
        font-family: Arial, sans-serif;
        margin-bottom: 10px;
    }
    .ingredient {
        color: #FF8552;
        font-weight: bold;
        margin-left: 5px;
    }
    .recipe-card {
        background-color: #FFECD1;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    }
    .recipe-button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #FF6F3C;
        color: white;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        margin-top: 15px;
    }
    .recipe-button:link,
    .recipe-button:visited {
        color: white;
        text-decoration: none;
    }
    .recipe-button:hover {
        background-color: #FF8552;
        color: white;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True
)

# Titre principal de la page
st.markdown("<h1 class='title'>🍲 Générateur de Recettes avec MealDB 🍲</h1>", unsafe_allow_html=True)

# Sous-titre de description
st.markdown("<p class='subtitle'>Entrez un ingrédient, et obtenez des recettes simples utilisant cet ingrédient</p>", unsafe_allow_html=True)

# Champ d'entrée pour l'ingrédient avec étiquette stylisée
st.markdown("<label class='input-label'>Entrez un ingrédient</label>", unsafe_allow_html=True)
ingredient = st.text_input("")

# Si un ingrédient est saisi, recherche et affiche les recettes
if ingredient:
    recipes = get_recipes_by_ingredient(ingredient)
    
    if isinstance(recipes, list):
        for recipe in recipes:
            # Récupère les détails complets de la recette
            recipe_details = get_recipe_details(recipe["idMeal"])

            if recipe_details:
                # Affichage de la carte de recette avec deux colonnes
                with st.container():
                    st.markdown(f"<div class='recipe-card'>", unsafe_allow_html=True)
                    st.subheader(f"{recipe['strMeal']}")
                    
                    # Deux colonnes : une pour l'image, l'autre pour les ingrédients
                    col1, col2 = st.columns([1, 2])
                    
                    # Colonne pour l'image
                    with col1:
                        st.image(recipe["strMealThumb"], width=300)
                    
                    # Colonne pour les ingrédients
                    with col2:
                        st.markdown(f"### 🍽️ Ingrédients nécessaires :")
                        ingredients = []
                        for i in range(1, 21):
                            ingredient_name = recipe_details.get(f"strIngredient{i}")
                            ingredient_measure = recipe_details.get(f"strMeasure{i}")
                            if ingredient_name and ingredient_name.strip():
                                ingredients.append(f"{ingredient_measure} {ingredient_name}")

                        # Divise les ingrédients en deux colonnes
                        half = len(ingredients) // 2
                        col_ingr1, col_ingr2 = st.columns(2)
                        with col_ingr1:
                            for ingr in ingredients[:half]:
                                st.markdown(f"- <span class='ingredient'>{ingr}</span>", unsafe_allow_html=True)
                        with col_ingr2:
                            for ingr in ingredients[half:]:
                                st.markdown(f"- <span class='ingredient'>{ingr}</span>", unsafe_allow_html=True)

                        # Bouton vers la recette complète
                        st.markdown(f"<a href='https://www.themealdb.com/meal/{recipe['idMeal']}' target='_blank' class='recipe-button'>Voir la recette complète</a>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write(recipes)
else:
    st.write("Veuillez entrer un ingrédient pour rechercher des recettes.")
