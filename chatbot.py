import streamlit as st
import time
from groq import Groq

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

# 5. Gestion de la clé API et de la barre latérale
secret_api_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else None

with st.sidebar:
    st.header("⚙️ Configuration")
    
    if secret_api_key:
        st.success("Clé API Groq sécurisée !", icon="🔒")
        api_key = secret_api_key
    else:
        api_key = st.text_input("Clé API Groq :", type="password", help="Obtenez votre clé sur console.groq.com")
        st.markdown("[👉 Obtenir une clé Groq (gratuit)](https://console.groq.com/keys)")
    
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

# 6. Blocage si pas de clé API
if not api_key:
    st.info("👋 Bienvenue sur l'assistant CamTrans ! Veuillez renseigner votre clé API Groq dans la barre latérale pour commencer.", icon="🔑")
    st.stop()

# 7. Message d'accueil décrivant le domaine de CamTrans
if not st.session_state.messages:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(255, 75, 75, 0.08), rgba(74, 144, 226, 0.08));
        border: 1px solid rgba(255, 140, 66, 0.2);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        animation: fadeIn 0.6s ease-in-out;
    ">
        <h3 style="margin-top: 0; color: #FF8C42;">👋 Bienvenue sur l'Assistant CamTrans !</h3>
        <p style="color: #ccc; font-size: 1.05rem; margin-bottom: 12px;">
            Nous sommes spécialisés dans la <strong style="color: #FF4B4B;">logistique et le transport de marchandises au Cameroun</strong>. 
            Notre assistant IA est là pour vous accompagner dans tous vos besoins de livraison et d'expédition.
        </p>
        <p style="color: #aaa; margin-bottom: 8px;">📦 <strong>Ce que je peux faire pour vous :</strong></p>
        <ul style="color: #bbb; list-style: none; padding-left: 0; line-height: 2;">
            <li>🚛 <strong>Estimation de tarifs</strong> — Douala → Yaoundé, Bafoussam, Garoua, et toutes les villes du Cameroun</li>
            <li>🗺️ <strong>Optimisation de trajets</strong> — Planifiez vos tournées de livraison efficacement</li>
            <li>📋 <strong>Conseils logistiques</strong> — Emballage, réglementation, colis fragiles, douanes</li>
            <li>💡 <strong>Aide sur CamTrans</strong> — Fonctionnement de la plateforme et de nos services</li>
        </ul>
        <p style="color: #888; font-size: 0.9rem; margin-bottom: 0;">💬 Posez votre question ci-dessous pour commencer !</p>
    </div>
    """, unsafe_allow_html=True)

# 8. Affichage des messages existants
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🚚"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 8. Saisie utilisateur (Champ texte ou clic sur un exemple)
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
            client = Groq(api_key=api_key)
            
            formatted_messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
            for m in st.session_state.messages:
                formatted_messages.append({"role": m["role"], "content": m["content"]})

            # Retry logic pour gérer les erreurs de quota temporaires
            max_retries = 3
            retry_delay = 15

            for attempt in range(max_retries):
                try:
                    response_stream = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=formatted_messages,
                        temperature=0.3,
                        stream=True
                    )
                    
                    for chunk in response_stream:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            response_placeholder.markdown(full_response + "▌")
                    
                    response_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    break

                except Exception as retry_error:
                    error_str = str(retry_error)
                    if ("429" in error_str or "rate_limit" in error_str.lower()) and attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        response_placeholder.markdown(f"⏳ *Quota temporairement atteint. Nouvelle tentative dans {wait_time}s... (essai {attempt + 2}/{max_retries})*")
                        time.sleep(wait_time)
                        full_response = ""
                        continue
                    else:
                        raise retry_error

        except Exception as e:
            error_msg = str(e)
            
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
                
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                st.warning("⚠️ Limite de requêtes atteinte. Veuillez patienter **2 à 3 minutes** puis réessayez.")
            elif "ConnectError" in error_msg or "getaddrinfo" in error_msg:
                st.error("🌐 Erreur de connexion réseau. Vérifiez votre connexion internet et réessayez.")
            elif "authentication" in error_msg.lower() or "401" in error_msg:
                st.error("🔑 Clé API Groq invalide. Vérifiez votre clé dans la barre latérale.")
            else:
                st.error(f"❌ Une erreur est survenue : {e}")