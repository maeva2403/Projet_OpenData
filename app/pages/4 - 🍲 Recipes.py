# pages/4 - 🍲 Recipes.py

import streamlit as st
import requests

from functions import initialize_session_state, show_cart_sidebar, get_recipes_by_ingredient, get_recipe_details


# User interface setup with Streamlit
st.set_page_config(page_title="Recipe Generator", page_icon="🍲", layout="wide")

initialize_session_state()
show_cart_sidebar()

# Page styling with embedded CSS for pastel colors
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
        color: #333333;
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

# Main title of the page
st.markdown("<h1 class='title'>🍲 Recipe Generator with MealDB 🍲</h1>", unsafe_allow_html=True)

# Subtitle description
st.markdown("<p class='subtitle'>Enter an ingredient, and get simple recipes using that ingredient</p>", unsafe_allow_html=True)

# Input field for the ingredient with styled label
st.markdown("<label class='input-label'>Enter an ingredient</label>", unsafe_allow_html=True)
ingredient = st.text_input("")

# If an ingredient is entered, search and display the recipes
if ingredient:
    recipes = get_recipes_by_ingredient(ingredient)
    
    if isinstance(recipes, list):
        for recipe in recipes:
            # Fetch the complete details of the recipe
            recipe_details = get_recipe_details(recipe["idMeal"])

            if recipe_details:
                # Display the recipe card with two columns
                with st.container():
                    st.markdown(f"<div class='recipe-card'>", unsafe_allow_html=True)
                    st.subheader(f"{recipe['strMeal']}")
                    
                    # Two columns: one for the image, another for the ingredients
                    col1, col2 = st.columns([1, 2])
                    
                    # Column for the image
                    with col1:
                        st.image(recipe["strMealThumb"], width=300)
                    
                    # Column for the ingredients
                    with col2:
                        st.markdown(f"### 🍽️ Ingredients required:")
                        ingredients = []
                        for i in range(1, 21):
                            ingredient_name = recipe_details.get(f"strIngredient{i}")
                            ingredient_measure = recipe_details.get(f"strMeasure{i}")
                            if ingredient_name and ingredient_name.strip():
                                ingredients.append(f"{ingredient_measure} {ingredient_name}")

                        # Split the ingredients into two columns
                        half = len(ingredients) // 2
                        col_ingr1, col_ingr2 = st.columns(2)
                        with col_ingr1:
                            for ingr in ingredients[:half]:
                                st.markdown(f"- <span class='ingredient'>{ingr}</span>", unsafe_allow_html=True)
                        with col_ingr2:
                            for ingr in ingredients[half:]:
                                st.markdown(f"- <span class='ingredient'>{ingr}</span>", unsafe_allow_html=True)

                        # Button linking to the full recipe
                        st.markdown(f"<a href='https://www.themealdb.com/meal/{recipe['idMeal']}' target='_blank' class='recipe-button'>View Full Recipe</a>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write(recipes)  # If no recipes are found, display the response
else:
    st.write("Please enter an ingredient to search for recipes.")  # If no ingredient is entered, prompt the user to enter one
