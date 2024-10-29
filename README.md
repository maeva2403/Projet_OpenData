# Projet OpenData - Application de Visualisation de Données

## Description
Application web développée avec Streamlit pour visualiser et analyser des données provenant de l'API OpenFoodFacts.

## Architecture du Projet

```
Projet_OpenData/
│
├── api/                    # Scripts de récupération de données
│   ├── __init__.py
│   ├── fetch_data.py      # Script principal de récupération
│   └── utilities.py       # Fonctions utilitaires pour l'API
│
├── app/                    # Application Streamlit
│   ├── __init__.py
│   ├── main.py            # Point d'entrée de l'application
│   └── pages/             # Pages de l'application
│       ├── __init__.py
│       ├── page1.py
│       ├── page2.py
│       └── page3.py
│
├── data/                   # Données
│
├── src/                   # Code source partagé
│   ├── __init__.py
│   ├── data_processing.py # Traitement des données
│   └── visualization.py   # Fonctions de visualisation
│
├── requirements.txt       # Dépendances
└── README.md             # Documentation
```

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/maeva2403/Projet_OpenData.git
cd Projet_OpenData
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Le projet se compose de deux parties distinctes :

### 1. Récupération des données (API)
Pour mettre à jour les données depuis l'API OpenFoodFacts :
```bash
python api/fetch_data.py
```
Cette commande va :
- Récupérer les catégories disponibles
- Télécharger les données pour chaque catégorie
- Sauvegarder les données dans le dossier `data/`

### 2. Application Web (Streamlit)
Pour lancer l'application web :
```bash
streamlit run app/main.py
```

## Structure des Pages

- **Page 1** : [Description de la page 1]
- **Page 2** : [Description de la page 2]
- **Page 3** : [Description de la page 3]

## Développement

Pour contribuer au projet :

1. Créer une nouvelle branche :
```bash
git checkout -b nom-de-votre-fonctionnalite
```

2. Faire vos modifications
3. Pousser vos changements :
```bash
git add .
git commit -m "Description des modifications"
git push origin nom-de-votre-fonctionnalite
```

4. Créer une Pull Request sur GitHub

## Guide de Contribution

- La partie API (`api/`) gère uniquement la récupération et le stockage des données
- La partie App (`app/`) gère uniquement l'affichage et l'interaction utilisateur
- Le code partagé va dans `src/`
- Les données sont stockées dans `data/`

## Dépendances Principales

- Streamlit
- Pandas
- Requests
- [Autres dépendances]

## Auteurs

- [Nom Auteur 1]
- [Nom Auteur 2]
- [Nom Auteur 3]