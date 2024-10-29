import requests
import json
import os
import time
import shutil
from datetime import datetime

def clear_data_directory():
    """Nettoie le dossier data/raw"""
    if os.path.exists('data/raw'):
        shutil.rmtree('data/raw')
        print("Ancien dossier data supprimé")
    os.makedirs('data/raw', exist_ok=True)
    print("Nouveau dossier data créé")

def fetch_categories():
    url = "https://world.openfoodfacts.org/categories.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        categories = [category['name'] for category in json_data.get('tags', [])]
        
        # Sauvegarder les catégories
        with open('data/raw/categories.json', 'w') as f:
            json.dump(categories, f)
            
        print(f"Catégories sauvegardées : {len(categories)} catégories trouvées")
        return categories
    except Exception as e:
        print(f"Erreur lors de la récupération des catégories : {e}")
        return []

def fetch_products_by_category(category):
    url = f"https://world.openfoodfacts.org/category/{category}.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        products = response.json().get('products', [])
        
        # Créer le dossier pour la catégorie
        category_path = f'data/raw/products/{category}'
        os.makedirs(category_path, exist_ok=True)
        
        # Sauvegarder les produits
        with open(f'{category_path}/products.json', 'w') as f:
            json.dump(products, f)
            
        print(f"Produits sauvegardés pour {category} : {len(products)} produits trouvés")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la récupération des produits pour {category} : {e}")
        return False

def fetch_data_with_timeout(timeout_seconds=60):
    """Récupère les données avec une limite de temps"""
    # Nettoyer les anciennes données
    clear_data_directory()
    
    start_time = time.time()
    categories = fetch_categories()
    
    if not categories:
        print("Échec de la récupération des catégories")
        return
    
    # Créer le dossier products
    os.makedirs('data/raw/products', exist_ok=True)
    
    categories_processed = 0
    for category in categories:
        # Vérifier si on a dépassé le temps limite
        if time.time() - start_time > timeout_seconds:
            print(f"\nTemps limite de {timeout_seconds} secondes atteint!")
            break
            
        if fetch_products_by_category(category):
            categories_processed += 1
        
        # Petite pause entre les requêtes pour éviter le rate limiting
        time.sleep(0.5)
    
    total_time = time.time() - start_time
    print(f"\nRécupération terminée en {total_time:.2f} secondes")
    print(f"Catégories traitées : {categories_processed}/{len(categories)}")

if __name__ == "__main__":
    fetch_data_with_timeout(60)  # 60 secondes = 1 minute