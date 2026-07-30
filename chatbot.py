import streamlit as st
import time

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
st.markdown('<p class="hero-caption">L\'intelligence artificielle dédiée à vos expéditions et au transport de marchandises au Cameroun.</p>', unsafe_allow_html=True)

# 4. Initialisation des variables de session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggested_prompt" not in st.session_state:
    st.session_state.suggested_prompt = None

# System Instruction
SYSTEM_INSTRUCTION = """
Tu es l'assistant IA officiel de CamTrans, une plateforme de logistique et de transport de marchandises au Cameroun. 
Ton rôle est d'aider les clients et les transporteurs :
- Estimer des tarifs de livraison (ex: Douala - Yaoundé, Bafoussam, Garoua, etc.)
- Donner des conseils sur la logistique, l'emballage et l'optimisation des trajets
- Expliquer le fonctionnement de l'écosystème CamTrans
- Fournir des réponses structurées, courtes, chaleureuses et professionnelles.

Formatage : Utilise des puces, des émojis et des mots en gras pour rendre la lecture très agréable.
"""

# 5. Détection du fournisseur et de la clé API
PROVIDER_CONFIG = {
    "gemini": {"label": "Google Gemini", "key_name": "GEMINI_API_KEY", "icon": "✨", "key_prefix": "AIza"},
    "groq": {"label": "Groq (LLaMA)", "key_name": "GROQ_API_KEY", "icon": "⚡", "key_prefix": "gsk_"},
    "openai": {"label": "OpenAI (GPT)", "key_name": "OPENAI_API_KEY", "icon": "🤖", "key_prefix": "sk-"},
}

# Lire le fournisseur depuis secrets.toml ou valeur par défaut
provider = st.secrets.get("AI_PROVIDER", "gemini").lower()
if provider not in PROVIDER_CONFIG:
    provider = "gemini"

provider_info = PROVIDER_CONFIG[provider]

# 6. Gestion de la barre latérale
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Sélection du fournisseur
    selected_provider = st.selectbox(
        "Fournisseur d'IA :",
        options=list(PROVIDER_CONFIG.keys()),
        format_func=lambda x: f"{PROVIDER_CONFIG[x]['icon']} {PROVIDER_CONFIG[x]['label']}",
        index=list(PROVIDER_CONFIG.keys()).index(provider),
        help="Choisissez votre fournisseur d'IA"
    )
    
    # Mettre à jour le provider si changé
    provider = selected_provider
    provider_info = PROVIDER_CONFIG[provider]
    
    st.divider()
    
    # Gestion de la clé API
    secret_api_key = st.secrets.get(provider_info["key_name"]) if provider_info["key_name"] in st.secrets else None
    
    # Vérifier si la clé secrète est une vraie clé (pas le placeholder)
    is_placeholder = secret_api_key and ("VOTRE_CLE" in secret_api_key or "ICI" in secret_api_key)
    
    if secret_api_key and not is_placeholder:
        st.success(f"Clé {provider_info['label']} sécurisée !", icon="🔒")
        api_key = secret_api_key
    else:
        api_key = st.text_input(
            f"Clé API {provider_info['label']} :",
            type="password",
            help=f"Entrez votre clé API {provider_info['label']}"
        )
        
        # Liens pour obtenir les clés
        links = {
            "gemini": "[👉 Obtenir une clé Gemini](https://aistudio.google.com/app/apikey)",
            "groq": "[👉 Obtenir une clé Groq (gratuit)](https://console.groq.com/keys)",
            "openai": "[👉 Obtenir une clé OpenAI](https://platform.openai.com/api-keys)",
        }
        st.markdown(links[provider])
    
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
            st.rerun()

    st.divider()

    # Bouton de réinitialisation du Chat
    if st.button("🗑️ Effacer la conversation", type="secondary"):
        st.session_state.messages = []
        st.session_state.suggested_prompt = None
        st.rerun()

# 7. Blocage si pas de clé API
if not api_key:
    st.info(f"👋 Bienvenue ! Veuillez renseigner votre clé API **{provider_info['label']}** dans la barre latérale pour commencer.", icon="🔑")
    st.stop()


# =============================================================================
# 8. Fonctions de génération par fournisseur
# =============================================================================

def generate_gemini(api_key, messages, system_instruction):
    """Génère une réponse avec Google Gemini (streaming)."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    
    formatted_contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])]
        )
        for m in messages
    ]

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3
    )

    response_stream = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=formatted_contents,
        config=config
    )
    
    for chunk in response_stream:
        if chunk.text:
            yield chunk.text


def generate_groq(api_key, messages, system_instruction):
    """Génère une réponse avec Groq / LLaMA (streaming)."""
    from groq import Groq

    client = Groq(api_key=api_key)
    
    formatted_messages = [{"role": "system", "content": system_instruction}]
    for m in messages:
        formatted_messages.append({"role": m["role"], "content": m["content"]})

    response_stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=formatted_messages,
        temperature=0.3,
        stream=True
    )
    
    for chunk in response_stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def generate_openai(api_key, messages, system_instruction):
    """Génère une réponse avec OpenAI / GPT (streaming)."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    
    formatted_messages = [{"role": "system", "content": system_instruction}]
    for m in messages:
        formatted_messages.append({"role": m["role"], "content": m["content"]})

    response_stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=formatted_messages,
        temperature=0.3,
        stream=True
    )
    
    for chunk in response_stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# Mapping des fonctions de génération
GENERATORS = {
    "gemini": generate_gemini,
    "groq": generate_groq,
    "openai": generate_openai,
}


# =============================================================================
# 9. Affichage et gestion du chat
# =============================================================================

# Affichage des messages existants
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🚚"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Saisie utilisateur (Champ texte ou clic sur un exemple)
prompt_input = st.chat_input("Posez votre question sur CamTrans, vos expéditions ou la logistique...")

prompt = st.session_state.suggested_prompt or prompt_input

if prompt:
    # Réinitialisation du prompt suggéré après capture
    st.session_state.suggested_prompt = None

    # Sauvegarde et affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Génération et streaming de la réponse de l'assistant
    with st.chat_message("assistant", avatar="🚚"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            generator_fn = GENERATORS[provider]

            # Retry logic pour gérer les erreurs de quota temporaires
            max_retries = 3
            retry_delay = 15  # secondes

            for attempt in range(max_retries):
                try:
                    for text_chunk in generator_fn(api_key, st.session_state.messages, SYSTEM_INSTRUCTION):
                        full_response += text_chunk
                        response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    break  # Succès, on sort de la boucle

                except Exception as retry_error:
                    error_str = str(retry_error)
                    if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "rate_limit" in error_str.lower()) and attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        response_placeholder.markdown(f"⏳ *Quota temporairement atteint. Nouvelle tentative dans {wait_time}s... (essai {attempt + 2}/{max_retries})*")
                        time.sleep(wait_time)
                        full_response = ""
                        continue
                    else:
                        raise retry_error

        except Exception as e:
            error_msg = str(e)
            
            # Retirer le dernier message utilisateur de l'historique en cas d'échec
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
                
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "rate_limit" in error_msg.lower():
                st.warning("⚠️ Limite de requêtes atteinte après plusieurs tentatives. Veuillez patienter **2 à 3 minutes** puis réessayez.")
            elif "ConnectError" in error_msg or "getaddrinfo" in error_msg or "ConnectionError" in error_msg:
                st.error("🌐 Erreur de connexion réseau. Vérifiez votre connexion internet et réessayez.")
            elif "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper() or "401" in error_msg or "authentication" in error_msg.lower():
                st.error(f"🔑 Clé API {provider_info['label']} invalide. Vérifiez votre clé dans la barre latérale.")
            else:
                st.error(f"❌ Une erreur est survenue : {e}")