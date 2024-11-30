import streamlit as st
from functions import initialize_session_state, show_cart_sidebar, plot_nutrient_journalier_plotly, plot_nutrient_distribution_plotly, display_sales_info_and_map

initialize_session_state()
show_cart_sidebar()

st.title("Tableau de Bord Nutritionnel")

if len(st.session_state.selected_products) < 1:
   st.warning("Sélectionnez au moins 1 produit.")

if st.session_state.selected_products:
   st.subheader("Objectifs Journaliers")
   
   col1, col2, col3, col4 = st.columns(4)
   with col1:
       calories = st.number_input("Calories (kcal)", 0, 5000, st.session_state.objectifs["calories"], 50)
       graisses = st.number_input("Graisses (g)", 0, 200, st.session_state.objectifs["graisses"])
   with col2:
       graisses_sat = st.number_input("Graisses saturées (g)", 0, 100, st.session_state.objectifs.get("graisses_sat", 20))
       glucides = st.number_input("Glucides (g)", 0, 500, st.session_state.objectifs.get("glucides", 260))
   with col3:
       sucres = st.number_input("Sucres (g)", 0, 100, st.session_state.objectifs["sucres"])
       proteines = st.number_input("Protéines (g)", 0, 200, st.session_state.objectifs.get("proteines", 50))
   with col4:
       sel = st.number_input("Sel (g)", 0.0, 20.0, float(st.session_state.objectifs["sel"]), 0.1)

   st.session_state.objectifs.update({
       "calories": calories,
       "graisses": graisses,
       "graisses_sat": graisses_sat,
       "glucides": glucides, 
       "sucres": sucres,
       "proteines": proteines,
       "sel": sel
   })

   plot_nutrient_journalier_plotly(st.session_state.selected_products, st.session_state.objectifs)
   plot_nutrient_distribution_plotly(st.session_state.selected_products)
   display_sales_info_and_map(st.session_state.selected_products)