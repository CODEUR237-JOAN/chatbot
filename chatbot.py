import streamlit as st
from google import genai
from google.genai import types

# 1. Configuration de la page
st.set_page_config(
    page_title="Assistant CamTrans",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injection du CSS pour le design moderne et les animations
st.markdown("""
<style>
    /* Gradient et animation sur le titre principal */
    .hero-title {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8C42 50%, #4A90E2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.6rem;
        margin-bottom: 0.2rem;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .hero-caption {
        font-size: 1.1rem;
        color: #888;
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.8s ease-out;
    }

    /* Style des bulles du Chatbot */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 12px 18px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeIn 0.4s ease-in-out;
    }

    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }

    /* Personnalisation de la Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Boutons des questions suggérées */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.03);
        text-align: left;
        padding: 10px 14px;
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 75, 75, 0.15), rgba(74, 144, 226, 0.15));
        border-color: #FF4B4B;
        transform: translateX(4px);
    }

    /* Keyframe Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# 3. En-tête stylisé
st.markdown('<h1 class="hero-title">🚚 Assistant CamTrans</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-caption">L\'intelligence artificielle dédiée à vos expéditions et au transport de marchandises au Cameroun & Afrique Centrale.</p>', unsafe_allow_html=True)

# 4. Gestion des secrets et de la barre latérale
secret_api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

# Initialisation de la clé suggérée si l'utilisateur clique sur un exemple
if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None

with st.sidebar:
    st.header("⚙️ Configuration")
    
    if secret_api_key:
        st.success("Clé API sécurisée !", icon="🔒")
        api_key = secret_api_key
    else:
        api_key = st.text_input("Clé API Google Gemini :", type="password", help="Obtenez votre clé sur Google AI Studio")
        st.markdown("[👉 Obtenir une clé API Gemini](https://aistudio.google.com/app/api-keys)")
    
    st.divider()
    
    st.subheader("💡 Exemples rapides")
    st.caption("Cliquez sur une question pour la poser directement :")

    examples = [
        "Estime le prix pour un trajet Douala - Yaoundé",
        "Comment optimiser une tournée de livraison ?",
        "Quelles sont les règles pour les colis fragiles ?",
        "Comment fonctionne l'application CamTrans ?"
    ]

    for ex in examples:
        if st.button(f"📌 {ex}", key=f"btn_{ex}"):
            st.session_state.suggested_prompt = ex

    st.divider()

    # Bouton de réinitialisation du Chat
    if st.button("🗑️ Effacer la conversation", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# 5. Blocage si pas de clé API
if not api_key:
    st.info("👋 Bienvenue sur l'assistant CamTrans ! Veuillez renseigner votre clé API Gemini dans la barre latérale pour commencer.", icon="🔑")
    st.stop()

# 6. Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Instruction Système de l'Assistant
SYSTEM_INSTRUCTION = """
Tu es l'assistant IA officiel de CamTrans, une plateforme de logistique et de transport de marchandises au Cameroun et en Afrique Centrale. 
Ton rôle est d'aider les clients et les transporteurs :
- Estimer des tarifs de livraison (ex: Douala - Yaoundé, Bafoussam, Garoua, etc.)
- Donner des conseils sur la logistique, l'emballage et l'optimisation des trajets
- Expliquer le fonctionnement de l'écosystème CamTrans
- Fournir des réponses structurées, courtes, chaleureuses et professionnelles.

Formatage : Utilise des puces, des émojis et des mots en gras pour rendre la lecture très agréable.
"""

# 7. Affichage des messages existants
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🚚"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 8. Saisie utilisateur (Champ texte ou clic sur un exemple)
prompt_input = st.chat_input("Posez votre question sur CamTrans, vos expéditions ou la logistique...")

# Récupération de la question (priorité au clic sur exemple)
prompt = st.session_state.suggested_prompt or prompt_input
if st.session_state.suggested_prompt:
    st.session_state.suggested_prompt = None  # Réinitialiser le clic

if prompt:
    # Sauvegarde et affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Réponse de l'IA
    with st.chat_message("assistant", avatar="🚚"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            # Formatage de l'historique pour le SDK google-genai
            formatted_contents = []
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                formatted_contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=m["content"])]
                    )
                )

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3
            )

            # Utilisation du modèle gemini-1.5-flash
            response_stream = client.models.generate_content_stream(
                model="gemini-1.5-flash",
                contents=formatted_contents,
                config=config
            )
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Une erreur est survenue lors de la communication avec l'IA : {e}")