import streamlit as st
from pages import page1

def main():
    st.set_page_config(
        page_title="Application Recettes",
        layout="wide"
    )
    
    page1.show()

if __name__ == "__main__":
    main()