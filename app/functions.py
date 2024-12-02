# functions.py

import requests
import plotly.express as px
import pandas as pd
import time
import streamlit as st
import plotly.graph_objects as go
import re

def initialize_session_state():
    # Check if "objectifs" (goals) is already initialized in session state
    # If not, initialize it with default values for fats, sugars, salt, and calories
    if "objectifs" not in st.session_state:
        st.session_state.objectifs = {"graisses": 70, "sucres": 50, "sel": 6, "calories": 2000}

    # Check if "selected_products" is already initialized in session state
    # If not, initialize it as an empty list (this will hold selected products)
    if "selected_products" not in st.session_state:
        st.session_state.selected_products = []

    # Check if "show_search" is already initialized in session state
    # If not, initialize it as False (controls whether the search interface is shown)
    if "show_search" not in st.session_state:
        st.session_state.show_search = False

    # Check if "search_results" is already initialized in session state
    # If not, initialize it as an empty list (this will hold search results)
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

def show_cart_sidebar():
   with st.sidebar:
       # Display the sidebar subheader for the cart
       st.subheader("Cart", anchor="cart-subheader")

       # Check if there are products in the selected_products list
       if st.session_state.selected_products:
           # Loop through each selected product and display its name
           for index, product in enumerate(st.session_state.selected_products):
               product_name = product.get('product_name', 'Unknown')
               st.write(f"- {product_name}")

               # Add a button to remove the product from the cart
               # When clicked, remove the product and show a success message
               if st.button(f"Remove {product_name}", key=f"remove_{index}", use_container_width=True):
                   st.session_state.selected_products.pop(index)
                   st.success(f"{product_name} removed from cart")
                   st.rerun()  # Re-run the app to update the cart display
       else:
           # If the cart is empty, display a message
           st.write("Your cart is empty.")
           
       # Button to add a product to the cart
       # When clicked, show the product search interface and switch pages
       if st.button("Add product", key="add_product", use_container_width=True):
           st.session_state.show_search = True
           st.switch_page("pages/1 - 🛒 Products.py")

# Function to search for a product by name
def search_product(query):
    # Construct the URL for the OpenFoodFacts API with the search query
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
    
    # Send a GET request to the API
    response = requests.get(url)
    
    # Check if the request was successful (HTTP status 200)
    if response.status_code == 200:
        # Parse the JSON response to extract the list of products
        data = response.json()
        return data.get('products', [])
    else:
        # Display an error message if the request failed
        st.error(f"Error occurred while searching for product: {response.status_code}")
        return []

# Function to search for products by category
@st.cache_data
def search_product_by_category(category, nb_items=20):
    # URL to fetch products from the specified category
    url = f"https://world.openfoodfacts.org/category/{category}.json"
    
    # Custom headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # List to store the found products
    products = []
    
    # Pagination parameters
    page = 1
    page_size = 100

    # Continue fetching until we reach the desired number of items
    while len(products) < nb_items:  
        try:
            # Request the product data for the current page
            response = requests.get(f"{url}?page={page}&page_size={page_size}", headers=headers, timeout=10)
            
            # If the response is successful (status 200)
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                new_products = data.get('products', [])
                
                # If no new products were found, stop the loop
                if not new_products:
                    break
                
                # Filter the products based on the required conditions
                for product in new_products:
                    if (product.get('product_name') and 
                        product.get('nutriments') and 
                        product.get('nutriscore_grade') not in [None, '', 'unknown', 'UNKNOWN'] and
                        product.get('ecoscore_grade') not in [None, '', 'unknown', 'UNKNOWN'] and
                        product.get('countries_tags') and 
                        product.get('nova_group')):
                        
                        nutriments = product.get('nutriments', {})
                        
                        # Check if the required nutriments are present
                        if all(nutriments.get(key) not in [None, '', 0, 'unknown', 'UNKNOWN'] 
                               for key in ["energy-kcal", "fat", "saturated-fat", "carbohydrates", 
                                           "sugars", "proteins", "salt"]):
                            products.append(product)
                            if len(products) >= nb_items:
                                break
                
                # Move to the next page
                page += 1
            else:
                break  # Stop if we get an unsuccessful response

        except:
            break  # Exit in case of any exception (e.g., timeout)

    # Return the required number of products
    return products[:nb_items]


def clean_prefixes(items):
    formatted_items = []
    for item in items:
        # Remove prefix before the first colon
        item_cleaned = re.sub(r'^.*?:', '', item)
        
        # Capitalize each part of the string, split by spaces or hyphens
        formatted_item = ' '.join([part.capitalize() for part in re.split(r'[- ]', item_cleaned)])
        
        # Replace spaces with hyphens to maintain formatting (e.g., country code style)
        formatted_item = formatted_item.replace(" ", "-")
        
        formatted_items.append(formatted_item)
    
    return formatted_items

def display_sales_map(countries_data):
    if not countries_data:
        return
    
    # Créer un dictionnaire pays -> produits
    country_products = {}
    for product in countries_data:
        product_name = product.get('product_name', 'Unknown')
        countries = product.get('countries_tags', [])
        
        cleaned_countries = clean_prefixes(countries)
        for country in cleaned_countries:
            if country not in country_products:
                country_products[country] = []
            country_products[country].append(product_name)
    
    # Créer le DataFrame pour Plotly
    df_countries = pd.DataFrame([
        {'Country': country, 'Products': '<br>- '.join(products)}
        for country, products in country_products.items()
    ])
    
    # Créer la carte avec les infobulles personnalisées
    fig = px.choropleth(
        df_countries,
        locations='Country',
        locationmode='country names',
        color='Country',
        hover_data=['Products'],
        custom_data=['Products'],
        title="Sales Countries for Selected Products",
        template="plotly_white",
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        title_font_size=18,
        title_font_family="Arial",
        title_x=0
    )
    
    # Personnaliser le format des infobulles
    fig.update_traces(
        hovertemplate="<b>%{location}</b><br><br>" +
        "Products sold:<br>- %{customdata[0]}<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_sales_info_and_map(selected_products):
    # Afficher le tableau des pays
    countries_list = []
    for product in selected_products:
        product_name = product.get('product_name', 'Inconnu')
        countries = product.get('countries_tags', [])
        
        if countries:
            countries_cleaned = clean_prefixes(countries)
            countries_list.append({
                'Product': product_name, 
                'Countries of Sale': ', '.join(countries_cleaned)
            })
        else:
            countries_list.append({
                'Product': product_name, 
                'Countries of Sale': 'No information available'
            })

    df_countries = pd.DataFrame(countries_list)
    st.subheader("Sales Countries Table for Products")
    st.dataframe(df_countries)
    
    # Afficher la carte avec les produits au survol
    display_sales_map(selected_products)

# Function to display the sales countries table
def display_sales_countries_table(selected_products):
    countries_list = []  # List to store sales countries
    
    # Iterate over each product in the cart
    for product in selected_products:
        product_name = product.get('product_name', 'Unknown')
        countries = product.get('countries_tags', [])
        
        if countries:
            countries_cleaned = clean_prefixes(countries)
            countries_list.append({'Product': product_name, 'Countries of Sale': ', '.join(countries_cleaned)})
        else:
            countries_list.append({'Product': product_name, 'Countries of Sale': 'No information available'})
    
    # Create a DataFrame from the list
    df_countries = pd.DataFrame(countries_list)

    # Display the table in Streamlit
    st.subheader("Sales Countries Table for Products")
    st.dataframe(df_countries)
        
# Function to generate a nutrient comparison chart with Recommended Daily Allowances (RDA)
def plot_nutrient_rda_comparison_plotly(selected_products, goals):
   rda = {
       "Calories (kcal)": goals.get("calories", 2000),
       "Fat (g)": goals.get("fat", 70),
       "Saturated Fat (g)": goals.get("saturated_fat", 20),
       "Carbohydrates (g)": goals.get("carbohydrates", 260), 
       "Sugars (g)": goals.get("sugars", 50),
       "Proteins (g)": goals.get("proteins", 50),
       "Salt (g)": goals.get("salt", 6)
   }

   # Calculate totals
   totals = {
       "Calories": sum(p.get('nutriments', {}).get('energy-kcal', 0) for p in selected_products),
       "Fat": sum(p.get('nutriments', {}).get('fat', 0) for p in selected_products),
       "Saturated Fat": sum(p.get('nutriments', {}).get('saturated-fat', 0) for p in selected_products),
       "Carbohydrates": sum(p.get('nutriments', {}).get('carbohydrates', 0) for p in selected_products),
       "Sugars": sum(p.get('nutriments', {}).get('sugars', 0) for p in selected_products),
       "Proteins": sum(p.get('nutriments', {}).get('proteins', 0) for p in selected_products),
       "Salt": sum(p.get('nutriments', {}).get('salt', 0) for p in selected_products)
   }

   comparison_data = {
       "Nutrient": list(rda.keys()),
       "Total Consumption": list(totals.values()),
       "RDA": list(rda.values())
   }

   df_comparison = pd.DataFrame(comparison_data)
   df_comparison_long = pd.melt(df_comparison, id_vars=["Nutrient"], 
                               value_vars=["Total Consumption", "RDA"],
                               var_name="Type", value_name="Value")

   fig = px.bar(df_comparison_long, x="Nutrient", y="Value", color="Type", barmode="group",
                labels={"Value": "Quantity (in kcal or g)", "Nutrient": "Nutrient", "Type": "Value Type"},
                title="Comparison of Nutrients with Recommended Daily Allowances")

   fig.update_layout(
       title_font_size=18,
       title_font_family="Arial",
       title_x=0,
       xaxis_title_font_size=14,
       yaxis_title_font_size=14,
       xaxis_tickangle=-45,
       xaxis_title="Nutrients",
       yaxis_title="Quantity (in kcal or g)",
       template="plotly_white",
       barmode="group"
   )

   st.plotly_chart(fig)

# Function to generate a nutrient distribution chart for selected products
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
                title="Total Nutrients of Selected Products",
                color_discrete_sequence=["#4CAF50", "#FFC107", "#F44336", "#2196F3", "#9C27B0", "#FF9800", "#03A9F4"])

   fig.update_layout(
       title_font_size=18,
       title_font_family="Arial",
       title_x=0,
       xaxis_title_font_size=14,
       yaxis_title_font_size=14,
       xaxis_tickangle=-45,
       xaxis_title="Nutrients",
       yaxis_title="Quantity (in kcal or g)",
       template="plotly_white",
       xaxis=dict(showgrid=True, zeroline=False),
       yaxis=dict(showgrid=True, zeroline=False),
       title=dict(font=dict(color="#4CAF50"))
   )

   st.plotly_chart(fig)

# Function to create a comparison chart of nutrients for each product
def create_nutrient_comparison(products):
    # List of nutrients we want to compare
    nutrients = [
        'energy-kcal', 'fat', 'saturated-fat', 'carbohydrates', 
        'sugars', 'fiber', 'proteins', 'salt'
    ]
    
    data = []  # Initialize an empty list to store the product data
    
    # Loop through each product to extract its nutrient data
    for product in products:
        nutriments = product.get('nutriments', {})  # Get the nutrient data for the product
        product_data = {
            'Product': product.get('product_name', 'Unknown'),  # Get the product name (default to 'Unknown' if missing)
            **{nutrient: nutriments.get(nutrient, 0) for nutrient in nutrients}  # Add each nutrient's value, defaulting to 0 if not available
        }
        data.append(product_data)  # Append the product's data to the list
    
    # Convert the data into a DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    fig = go.Figure()  # Initialize a plotly figure
    
    # Loop through each unique product to plot the bar charts
    for product in df['Product'].unique():
        product_data = df[df['Product'] == product]  # Filter the DataFrame for the current product
        fig.add_trace(go.Bar(
            name=product,  # Name of the trace is the product name
            x=nutrients,  # X-axis is the list of nutrients
            y=product_data[nutrients].values.flatten(),  # Y-axis is the nutrient values for the current product
            text=product_data[nutrients].values.flatten(),  # Display the nutrient values as text on the bars
            textposition='auto',  # Automatically position the text on the bars
        ))

    # Update the layout for the chart
    fig.update_layout(
        title="Nutrients comparison per product",  # Title of the chart
        barmode='group',  # Bars will be grouped by product
        yaxis_title="Quantity",  # Y-axis label
        xaxis_title="Nutrients",  # X-axis label
        xaxis_tickangle=-45  # Angle the x-axis labels for better readability
    )
    
    # Return the figure to be displayed
    return fig

# Function to convert letter-based score to numerical score
def convert_letter_score_to_number(letter):
    # Mapping of letter grades to numerical scores
    score_mapping = {
        'A': 5, 'A-PLUS': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1,
        'a': 5, 'a-plus': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1
    }
    # Convert the input letter to uppercase and return the corresponding score; default to 0 if not found
    return score_mapping.get(str(letter).upper(), 0)

# Function to create a radar chart comparing the Nutriscore, Ecoscore, and NOVA scores of selected products
def create_radar_comparison(products):
    data = []  # List to store the processed data for each product
    
    # Loop through each product and extract its scores
    for product in products:
        # Convert Nutriscore and Ecoscore letter grades to numerical values
        nutriscore = convert_letter_score_to_number(product.get('nutriscore_grade', 'e'))
        ecoscore = convert_letter_score_to_number(product.get('ecoscore_grade', 'e'))
        
        # Get the NOVA group (default to 4 if not available)
        nova = product.get('nova_group', 4)
        # Convert the NOVA group to a numerical value, where 1 is the best and 4 is the worst
        nova_converted = 5 - ((nova - 1) * (4/3)) if nova else 0
        
        # Append the processed data for this product to the data list
        data.append({
            'Product': product.get('product_name', 'Unknown'),
            'Nutriscore': nutriscore,
            'Ecoscore': ecoscore,
            'NOVA': nova_converted
        })
    
    # Create a Plotly figure for the radar chart
    fig = go.Figure()
    
    # Loop through the data and add a trace for each product
    for product in data:
        fig.add_trace(go.Scatterpolar(
            r=[product['Nutriscore'], product['Ecoscore'], product['NOVA']],  # Radar chart values
            theta=['Nutriscore', 'Ecoscore', 'NOVA'],  # Labels for each axis
            fill='toself',  # Fill the area inside the radar chart
            name=product['Product']  # Label for the trace (product name)
        ))
    
    # Update the layout of the radar chart
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),  # Set the range of the radial axis (0 to 5)
        title="Comparison of Scores (5 = best score)"  # Title of the chart
    )
    
    # Return the figure to be displayed
    return fig

# Function to get recipes by a specific ingredient
@st.cache_data
def get_recipes_by_ingredient(ingredient):
    # API URL to filter meals by ingredient
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)  # Sending GET request to the API
    if response.status_code == 200:  # Check if the request is successful
        data = response.json()  # Parse the JSON response
        # Return the list of meals or a message if no meals are found
        return data["meals"] if data["meals"] else "No recipe found for this ingredient."
    # Return an error message if the API request fails
    return f"Error: {response.status_code}"

# Function to get detailed information about a specific recipe
@st.cache_data
def get_recipe_details(recipe_id):
    # API URL to get detailed information about a recipe using its ID
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={recipe_id}"
    response = requests.get(url)  # Sending GET request to the API
    if response.status_code == 200:  # Check if the request is successful
        data = response.json()  # Parse the JSON response
        # Return the details of the recipe or None if no details are found
        return data["meals"][0] if data["meals"] else None
    # Return None if the API request fails
    return None


# Use @st.cache_data to cache the processing of products
@st.cache_data
def process_products(products):
    processed_data = []  # List to store processed product data
    
    # Iterate through each product in the input list
    for product in products:
        # Extract basic product information (name, code, URL, etc.)
        product_data = {
            "product_name": product.get("product_name", "Unknown"),
            "code": product.get("code", "Unknown"),
            "url": product.get("url", "#"),
            "quantity": product.get("quantity", "Information not available"),
            "categories": product.get("categories", "Information not available"),
            "origins": product.get("origins", "Information not available"),
            "nutriscore_grade": product.get("nutriscore_grade", "Not available").upper(),
            "ecoscore_grade": product.get("ecoscore_grade", "Not available").upper(),
            "nova_group": product.get("nova_group", "Not available"),
            "nutrition_data_per": product.get("nutrition_data_per", "Not available"),
            "image_url": product.get("image_front_small_url", None)
        }
        
        # List of specific nutrients to extract
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
        
        # Extracting nutrient values from the product's 'nutriments' field
        nutriments = product.get("nutriments", {})
        for nutrient_key in selected_nutrients:
            nutrient_value = nutriments.get(nutrient_key)
            # Transform the nutrient name for better readability in the DataFrame
            nutrient_name = nutrient_key.replace('_100g', '').replace('_unit', '').replace('-', ' ').capitalize()
            product_data[nutrient_name] = nutrient_value
        
        # Clean and process allergens and labels
        allergens = product.get("allergens", "")
        product_data["allergens"] = ", ".join(clean_prefixes(allergens.split(","))) if allergens else "Not available"
        
        labels = product.get("labels", "")
        product_data["labels"] = ", ".join(clean_prefixes(labels.split(","))) if labels else "Not available"

        # Clean and process categories and origins
        categories = product.get("categories", "")
        product_data["categories"] = ", ".join(clean_prefixes(categories.split(","))) if categories else "Not available"
        
        origins = product.get("origins", "")
        product_data["origins"] = ", ".join(clean_prefixes(origins.split(","))) if origins else "Not available"
        
        # Clean and process countries of sale
        countries = product.get("countries_tags", [])
        product_data["countries"] = ", ".join(clean_prefixes(countries)) if countries else "Not available"
        
        # Add the processed product data to the list
        processed_data.append(product_data)
    
    # Convert the list of product data into a DataFrame and return it
    return pd.DataFrame(processed_data)


def plot_label_distribution(selected_products):
    specific_labels = ["No gluten", "Vegetarian", "Vegan"]
    label_counts = {label: 0 for label in specific_labels}
    label_products = {label: [] for label in specific_labels}

    for product in selected_products:
        labels = product.get('labels', '').split(',')
        for label in specific_labels:
            if label in labels:
                label_counts[label] += 1
                label_products[label].append(product.get('product_name', 'Unknown'))

    total_products = len(selected_products)
    others_count = total_products - sum(label_counts.values())
    if others_count > 0:
        label_counts["Others"] = others_count
        label_products["Others"] = [p.get('product_name', 'Unknown') for p in selected_products 
                                  if not any(label in p.get('labels', '').split(',') for label in specific_labels)]

    labels = list(label_counts.keys())
    values = list(label_counts.values())
    hover_info = [f"<b>{label}</b><br><br>{count} product/s:<br>- " + "<br>- ".join(label_products[label]) 
                 for label, count in zip(labels, values)]

    # Réorganiser les couleurs pour correspondre à l'ordre des labels
    colors = {
        "No gluten": "#FFF59D",    # jaune pâle
        "Vegetarian": "#A8E6CF",   # bleu
        "Vegan": "#81C784",        # vert
        "Others": "#E0E0E0"        # gris
    }
    color_sequence = [colors[label] for label in labels]

    fig = px.pie(
        names=labels,
        values=values,
        title="Product Distribution by Dietary Requirements",
        color_discrete_sequence=color_sequence
    )

    fig.update_traces(
        textposition="inside", 
        textinfo="percent+label",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_info
    )
    
    fig.update_layout(
        title_font_size=18,
        title_font_family="Arial",
        title_x=0,
        hovermode="closest",
        showlegend=True,
        legend_title="Dietary Restrictions"
    )

    st.plotly_chart(fig)
