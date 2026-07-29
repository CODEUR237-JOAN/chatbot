import streamlit as st
from google import genai
from google.genai import types

# Configuration de la page Streamlit pour CamTrans
st.set_page_config(
    page_title="Assistant CamTrans",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# En-tête de l'application
st.title("✨ Assistant CamTrans")
st.caption("L'intelligence artificielle dédiée à vos expéditions et au transport de marchandises.")

# Barre latérale pour la clé API et les options
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Clé API Google Gemini :", type="password")
    st.markdown("[Obtenir une clé API Gemini](https://aistudio.google.com/app/api-keys)")
    
    st.divider()
    st.subheader("💡 Exemples de questions")
    st.write("• *Comment optimiser une tournée de livraison ?*")
    st.write("• *Peux-tu estimer le prix pour un trajet Douala - Yaoundé ?*")
    st.write("• *Quelles sont les règles pour le transport de marchandises fragiles ?*")
    st.write("• *Comment fonctionne l'application CamTrans ?*")

# Vérification de la clé API
if not api_key:
    st.info("👋 Bienvenue sur CamTrans ! Veuillez saisir votre clé API Gemini dans le panneau de gauche pour démarrer.", icon="🔑")
    st.stop()

# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Instruction système : Personnalité officielle de l'assistant CamTrans
SYSTEM_INSTRUCTION = """
Tu es l'assistant IA officiel de CamTrans, une application de logistique et de transport de marchandises. 
Ton rôle est d'aider les utilisateurs (clients et transporteurs) à:
- Estimer des prix de livraison (notamment au Cameroun et en Afrique Centrale, ex: Douala - Yaoundé)
- Optimiser des trajets et tournées
- Comprendre le fonctionnement de CamTrans
- Obtenir des conseils sur le transport de colis et marchandises

Règles de comportement :
1. Sois toujours poli, professionnel, concis et utile.
2. Si une question ne concerne absolument pas le transport, la mobilité ou CamTrans, ramène gentiment la conversation vers ton domaine d'expertise.
3. Utilise des puces ou du formatage Markdown pour rendre tes réponses très lisibles.
"""

# Affichage des anciens messages
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question sur CamTrans, vos expéditions ou la logistique..."):
    # Stocker et afficher la question de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Génération de la réponse avec Gemini
    with st.chat_message("assistant", avatar="✨"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            # Préparation de l'historique pour Gemini
            formatted_contents = []
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                formatted_contents.append({
                    "role": role,
                    "parts": [{"text": m["content"]}]
                })

            # Configuration avec l'instruction système
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3
            )

            # CORRECTION DU MODÈLE : gemini-2.5-flash au lieu de gemini-2.0-flash
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=formatted_contents,
                config=config
            )
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # Sauvegarde de la réponse dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Erreur lors de la communication avec l'IA CamTrans : {e}")