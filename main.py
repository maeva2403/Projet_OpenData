import streamlit as st

# Titre de votre application
st.title('Mon Application Streamlit')

# Ajout de contenu simple
st.write('Hello World!')

# Exemple avec un widget
if st.button('Cliquez-moi'):
    st.write('Bouton cliqué!')