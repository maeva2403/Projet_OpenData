import streamlit as st
from functions import initialize_session_state, show_cart_sidebar, plot_nutrient_rda_comparison_plotly, plot_nutrient_distribution_plotly, display_sales_info_and_map, plot_label_distribution

# Initialize session state
initialize_session_state()

# Display the cart sidebar
show_cart_sidebar()

# Dashboard title
st.title("Nutritional Dashboard")

# Check if any products are selected
if len(st.session_state.selected_products) < 1:
    st.warning("Please select at least one product.")

# If products are selected, display nutritional information
if st.session_state.selected_products:
    st.subheader("Daily Goals")

    # Create columns for user input of daily goals
    col1, col2, col3, col4 = st.columns(4)
    
    # User input for daily goals for nutrients
    with col1:
        calories = st.number_input("Calories (kcal)", 0, 5000, st.session_state.objectifs["calories"], 50)
        fat = st.number_input("Fat (g)", 0, 200, st.session_state.objectifs["graisses"])
    with col2:
        saturated_fat = st.number_input("Saturated Fat (g)", 0, 100, st.session_state.objectifs.get("graisses_sat", 20))
        carbohydrates = st.number_input("Carbohydrates (g)", 0, 500, st.session_state.objectifs.get("glucides", 260))
    with col3:
        sugars = st.number_input("Sugars (g)", 0, 100, st.session_state.objectifs["sucres"])
        proteins = st.number_input("Proteins (g)", 0, 200, st.session_state.objectifs.get("proteines", 50))
    with col4:
        salt = st.number_input("Salt (g)", 0.0, 20.0, float(st.session_state.objectifs["sel"]), 0.1)

    # Update the session state with the new values
    st.session_state.objectifs.update({
        "Calories": calories,
        "Fat": fat,
        "Saturated_fat": saturated_fat,
        "Carbohydrates": carbohydrates, 
        "Sugars": sugars,
        "Proteins": proteins,
        "Salt": salt
    })

    # Plot comparisons between nutrient values and daily recommended intake (RDA)
    plot_nutrient_rda_comparison_plotly(st.session_state.selected_products, st.session_state.objectifs)
    
    # Plot the distribution of nutrients across the selected products
    plot_nutrient_distribution_plotly(st.session_state.selected_products)
    
    # Plot the distribution of product labels (e.g., vegan, gluten-free)
    plot_label_distribution(st.session_state.selected_products)
    
    # Display sales information and map for the selected products
    display_sales_info_and_map(st.session_state.selected_products)
