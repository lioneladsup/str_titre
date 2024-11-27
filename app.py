import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit as st
import pandas as pd
from urllib.parse import urlparse
import pandas as pd
import numpy as np
import json
import re
import requests
import uuid  
import traceback
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
from Data import calculate
import yaml
import warnings
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging
import traceback  # Ajout pour afficher la pile des erreurs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.filterwarnings('ignore')

url_login_info = 'https://docs.google.com/spreadsheets/d/1XwQZwNXHfmmpQU7tcGhB2MWCAoQj1vi3BcL2Q2mOwlM/edit?gid=0#gid=0'
url_cat_advice = 'https://docs.google.com/spreadsheets/d/13Ujrp1d3FHcRxTQLRUjkRKqJrgujYAeeq2wrFvjDZPY/edit?gid=2045289059#gid=2045289059'
url_postlist = "https://www.meetic.fr/p/lists/postList.json"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
max_index = 0

def save_session_to_firestore():
    """
    Saves the session data from st.session_state to Firestore.
    """
    if 'user_state' in st.session_state and st.session_state.user_state.get('logged_in', False):
        user_data = st.session_state.user_state
        username = user_data['username']
        session_id = user_data['session_id']
        
        # Reference to the main user document by username
        user_doc_ref = db.collection("sessions").document(username)
        
        # Save general user information in the main document if it doesn’t exist
        user_doc_ref.set({
            "username": username,
            "last_login": datetime.now().isoformat()
        }, merge=True)
        
        # Reference to the specific session document in a subcollection
        session_doc_ref = user_doc_ref.collection("user_sessions").document(f"{username}_{session_id}")
        
        # Save the session data, including interactions, to the subcollection
        session_doc_ref.set({
            "session_id": session_id,
            "username": username,
            "login_time": user_data.get("login_time", datetime.now().isoformat()),
            "interactions": user_data.get("interactions", [])
        })
        
        print(f"Session data for {username} saved to Firestore")

def user_login():
    # Load login info from Google Sheets
    df_login_info = googlesheets.import_sheet(url_login_info)  # Assumes you have this function to import data
    
    # Initialize user_state if it doesn't exist
    if 'user_state' not in st.session_state:
        st.session_state.user_state = {
            'username': '',
            'password': '',
            'logged_in': False,
            'session_id': None,
            'interactions': []
        }

    # If not logged in, show login form
    if not st.session_state.user_state['logged_in']:
        st.title('User Login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit = st.button('Login')

        # Check if user submitted the form
        if submit:
            # Check credentials against df_login_info (loaded from Google Sheets)
            user_row = df_login_info[(df_login_info['username'] == username) & 
                                     (df_login_info['password'] == password)]
            
            # If matching user is found, log in
            if not user_row.empty:
                # Set session data
                st.session_state.user_state['username'] = username
                st.session_state.user_state['logged_in'] = True
                st.session_state.user_state['session_id'] = f"{username}_{datetime.now().timestamp()}"
                
                # Add interaction data
                st.session_state.user_state['interactions'].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "Logged in"
                })
                
                st.success('You are logged in')
                save_session_to_firestore()
            else:
                st.error('Invalid username or password')

    else:
        # If logged in, show the user's name and main page
        st.success(f"Welcome back, {st.session_state.user_state['username']}!")
        
        # Call the main app functionality after login (for example, audit page)
        audit_page()  # This can be replaced with whatever page you want to display post-login
        
        # Optionally, add interaction data for each page load or interaction
        st.session_state.user_state['interactions'].append({
            "timestamp": datetime.now().isoformat(),
            "action": "Page loaded"
        })
        
        # Save session after interaction
        save_session_to_firestore()

import streamlit as st
import pandas as pd
import requests
import pandas as pd
import yaml
import numpy as np
from googleapiclient.discovery import build
from google.oauth2 import service_account
import urllib3
import xmltodict
import openai


def XMLImport(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = xmltodict.parse(response.data)
    list_champs = []
    for i in data['rss']['channel']['item'] :
        list_champs.extend(list(i.keys()))
    df = pd.DataFrame()
    for ele in set(list_champs) :
        df[ele] = [i[ele] if ele in i.keys() else '' for i in data['rss']['channel']['item']]
    return df


def audit_page_old():
    st.title("Feed Management")

    # Input field for the feed URL
    feed_url = st.text_input("Enter the URL of the feed:")

    if feed_url:
        try:
            # Fetch data from the URL
            response = requests.get(feed_url)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            # Load the data into a DataFrame
            #df_flux = pd.read_csv(pd.compat.StringIO(response.text), sep=',')

            df_flux = XMLImport(response.text)
    
            try:
                df_flux.rename(columns={'g:id': 'id'}, inplace=True)  
                df_flux.rename(columns={'g:image_link': 'image_link'}, inplace=True)  
                df_flux.rename(columns={'g:product_type': 'product_type'}, inplace=True)  
                df_flux.rename(columns={'g:brand': 'brand'}, inplace=True)  
            except:
                pass 
            
            df_flux = df_flux.head(10)

            # Process the data
            df_flux['new_title'] = df_flux.apply(
                calculate.generate_new_title, axis=1, args=('FR',)
            )
            df_title = df_flux[['id', 'new_title', 'title', 'brand']]

            # Clean the 'new_title' column
            df_title['new_title'] = (
                df_title['new_title']
                .str.replace(' beauty', '', case=False)
                .str.replace('"', '', case=False)
            )

            # Display the processed data
            st.subheader("Final Results")
            st.dataframe(df_title)

            # Convert the DataFrame to CSV format for download
            csv = df_title.to_csv(index=False).encode('utf-8')

            # Provide download button for the processed CSV
            st.download_button(
                label="Download Processed CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv",
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch the data from the provided URL: {e}")
        except pd.errors.ParserError as e:
            st.error(f"Failed to parse the CSV data: {e}")





def log_global_error_to_firestore(error_message, username=None):
    """
    Logs an error message to Firestore under the user's errors subcollection or a global errors collection.
    """
    # db = firestore.Client()  # Assumes global Firestore client if initialized elsewhere
    
    # If a username is provided, log to the user's errors subcollection
    if username:
        errors_doc_ref = db.collection("sessions").document(username).collection("errors").document()
    else:
        # Log to a global errors collection if no username is available
        errors_doc_ref = db.collection("global_errors").document()

    # Log the error with a timestamp
    errors_doc_ref.set({
        "timestamp": datetime.now().isoformat(),
        "error_message": error_message
    })


import streamlit as st
import requests
import pandas as pd

# Fonction de login
def login_page():
    st.title("Page de Login")

    # Vérifier si l'utilisateur est déjà connecté
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.success("Vous êtes déjà connecté!")
        # Si connecté, ouvrir directement la page de gestion des flux
        audit_page()  
    else:
        # Demander à l'utilisateur de saisir son nom d'utilisateur et son mot de passe
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if username == "admin" and password == "password123":
                st.session_state["logged_in"] = True  # Définir l'état de la session comme connecté
                st.session_state["page"] = "audit"  # Marquer la page comme étant la page d'audit
                st.success("Connexion réussie!")
                # Rediriger vers la page d'audit directement
                st.session_state["show_audit_page"] = True  # Indiquer que l'on doit afficher la page audit
                # Effacer la page de login (réinitialiser le UI)
                st.rerun()  # Utilisez st.rerun() pour recharger l'application et afficher la page suivante
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

# Fonction de gestion des flux (audit_page)
def audit_page():
    st.title("Feed Management")

    # Champ de saisie pour l'URL du flux
    feed_url = st.text_input("Enter the URL of the feed:")

    # Champ de saisie pour le prompt
    user_prompt = st.text_area("Entrez votre prompt ici:", height=100)

    # Bouton Valider
    if st.button("Valider"):
        # Une fois que l'utilisateur clique sur Valider, on procède au traitement
        if feed_url and user_prompt:
            try:
                # Charger les données à partir du flux
                st.info("Fetching and processing the feed. Please wait...")
                df_flux = XMLImport(feed_url)
                
                # Renommer les colonnes si nécessaire
                try:
                    df_flux.rename(columns={'g:id': 'id'}, inplace=True)
                    df_flux.rename(columns={'g:image_link': 'image_link'}, inplace=True)
                    df_flux.rename(columns={'g:product_type': 'product_type'}, inplace=True)
                    df_flux.rename(columns={'g:brand': 'brand'}, inplace=True)
                except:
                    pass
                
                df_flux = df_flux.head(5)

                # Ajouter la colonne 'new_title' en appliquant la fonction 'generate_new_title' avec le prompt
                df_flux['new_title'] = df_flux.apply(
                    lambda row: calculate.generate_new_title_streamlit(row, user_prompt), axis=1
                )

                # Créer une vue simplifiée avec les nouveaux titres
                df_title = df_flux[['id', 'new_title', 'title', 'brand']]

                # Nettoyer les nouveaux titres
                df_title['new_title'] = df_title['new_title'].str.replace(
                    ' beauty', '', case=False
                ).str.replace('"', '', case=False)

                # Afficher les résultats
                st.success("Traitement terminé ! Voici vos résultats :")

                # Afficher les données brutes
                st.subheader("Aperçu des données brutes")
                st.dataframe(df_flux)

                # Afficher les nouveaux titres
                st.subheader("Nouveaux titres")
                st.dataframe(df_title)

                # Bouton de téléchargement
                csv = df_title.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Télécharger les résultats en CSV",
                    data=csv,
                    file_name='resultats_flux.csv',
                    mime='text/csv',
                )

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to fetch the data from the provided URL: {e}")
            except pd.errors.ParserError as e:
                st.error(f"Failed to parse the data: {e}")
        else:
            # Si l'utilisateur n'a pas rempli les deux champs
            st.error("Veuillez remplir les deux sections avant de cliquer sur Valider.")

# Importer la fonction XMLImport (si non définie ailleurs)
def XMLImport(url):
    import xmltodict
    import urllib3
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = xmltodict.parse(response.data)
    list_champs = []
    for i in data['rss']['channel']['item']:
        list_champs.extend(list(i.keys()))
    df = pd.DataFrame()
    for ele in set(list_champs):
        df[ele] = [i[ele] if ele in i.keys() else '' for i in data['rss']['channel']['item']]
    return df

# Démarrer l'application
if __name__ == "__main__":
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        # Si l'utilisateur est déjà connecté, on affiche la page de gestion des flux
        audit_page()
    else:
        # Sinon, afficher la page de login
        login_page()
