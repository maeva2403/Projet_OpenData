# Projet OpenData - Application Streamlit

## Description
Application web développée avec Streamlit pour visualiser et analyser des données ouvertes.

## Structure du Projet

```
Projet_OpenData/
│
├── main.py                 # Point d'entrée de l'application
│
├── pages/                  # Différents onglets de l'application
│   ├── __init__.py
│   ├── page1.py           # Premier onglet
│   ├── page2.py           # Deuxième onglet
│   └── page3.py           # Troisième onglet
│
├── data/                   # Stockage des données
│   └── raw/               # Données brutes non modifiées
│
├── src/                    # Code source principal
│   ├── __init__.py
│   ├── data_processing.py # Traitement des données
│   └── visualization.py   # Création des visualisations
│
├── utils/                  # Fonctions utilitaires
│   ├── __init__.py
│   └── helpers.py         # Fonctions d'aide diverses
│
├── config/                 # Configuration
│   └── config.py          # Variables de configuration
│
├── requirements.txt        # Dépendances Python
│
└── README.md              # Ce fichier
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

## Lancement de l'application

```bash
streamlit run main.py
```

## Guide de contribution

1. Créer une nouvelle branche pour votre fonctionnalité :
```bash
git checkout -b nom-de-votre-fonctionnalite
```

2. Effectuer vos modifications
3. Commiter vos changements :
```bash
git add .
git commit -m "Description de vos modifications"
git push origin nom-de-votre-fonctionnalite
```

4. Ouvrir une Pull Request sur GitHub

## Organisation des pages

- **Page 1** : [Description de la première page]
- **Page 2** : [Description de la deuxième page]
- **Page 3** : [Description de la troisième page]

## Dépendances principales

- Streamlit
- Pandas
- [Autres dépendances principales]

## Auteurs

- [Votre nom]
- [Nom du collaborateur 2]
- [Nom du collaborateur 3]