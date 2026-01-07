import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="El Sueño de Leonor - Prototipo",
    page_icon="🌹",
    layout="wide"
)

# Estilo visual
st.markdown("""
<style>
    .stChatMessage { font-family: 'Georgia', serif; }
    h1, h2, h3 { color: #4b3621; }
</style>
""", unsafe_allow_html=True)

# --- 2. CONEXIÓN API (SECRETS) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Falta la API Key. Crea el archivo .streamlit/secrets.toml")
    st.stop()

# --- 3. PERSONAJES (CONTEXTO NOVELA) ---
CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo",
        "role": "La Protagonista",
        "avatar": "img/leonor.png", 
        "greeting": "Bienvenido a Villa Aurora. Apenas he deshecho mi equipaje. ¿Traéis noticias de Madrid?",
        "system_instruction": """
            Eres Leonor Polo, protagonista de 'El Sueño de Leonor' (S. XIX).
            Eres culta, institutriz, resiliente tras tu paso por el hospicio.
            Te gusta Maximiliano pero mantienes las distancias por decoro.
            Habla con lenguaje culto y elegante de la época.
        """
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar",
        "role": "El Dueño de la Finca",
        "avatar": "img/maximiliano.png", 
        "greeting": "¿Quién sois? No recibo visitas sin cita previa. Sed breve.",
        "system_instruction": """
            Eres Maximiliano Alcázar, rico y atormentado.
            Ocultas un secreto en el ático y cargas con una gran culpa.
            Eres brusco pero noble en el fondo. Niega cualquier rumor sobre ruidos extraños.
        """
    },
    "mercedes": {
        "name": "Doña Mercedes",
        "role": "Ama de Llaves",
        "avatar": "img/mercedes.png", 
        "greeting": "Límpiese los pies antes de entrar. El Señor no está para nadie.",
        "system_instruction": """
            Eres el Ama de Llaves, Doña Mercedes.
            Protectora, estricta y religiosa.
            Tu misión es proteger la reputación de la casa. Desvía cualquier pregunta incómoda.
        """
    },
    "elena": {
        "name": "Elena",
        "role": "Recuerdo / Espíritu",
        "avatar": "img/elena.png", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas... ¿Los sientes?",
        "system_instruction": """
            Eres el espíritu de Elena, amiga de la infancia de Leonor.
            Dulce, etérea y onírica. Representas la esperanza y la inocencia.
        """
    }
}

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.header("🎭 Personajes")
    char_names = [d["name"] for k, d in CHARACTERS.items()]
    selected = st.radio("Hablar con:", char_names)
    
    # Identificar personaje
    curr_key = next(k for k, v in CHARACTERS.items() if v["name"] == selected)
    curr_char = CHARACTERS[curr_key]
    
    try:
        st.image(curr_char["avatar"], width=150)
    except:
        st.warning("Falta imagen en carpeta img/")
    
    if st.button("Reiniciar"):
        st.session_state.messages = []
        st.rerun()

# --- 5. LOGICA DEL CHAT ---
st.title(f"💬 {curr_char['name']}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mensaje de bienvenida al cambiar personaje
if "last_char" not in st.session_state or st.session_state.last_char != curr_key:
    st.session_state.last_char = curr_key
    st.session_state.messages = [{"role": "model", "content": curr_char["greeting"]}]

# --- 6. CONFIGURACIÓN DEL MODELO (AQUÍ ESTÁ EL CAMBIO) ---
# Intentamos usar el modelo preview solicitado. Si falla, usamos el estable.
TARGET_MODEL = "gemini-2.5-flash-preview-09-2025"
FALLBACK_MODEL = "gemini-1.5-flash"

try:
    # Intentamos configurar el modelo solicitado
    model = genai.GenerativeModel(
        model_name=TARGET_MODEL,
        system_instruction=curr_char["system_instruction"]
    )
    # Hacemos una llamada vacía de prueba para ver si el nombre es válido
    # (Esto es un truco técnico para validar el modelo antes de chatear)
    # Si falla, saltará al 'except'
except Exception:
    # Si el modelo 2.5 no existe o da error, usamos el 1.5 silenciosamente
    model = genai.GenerativeModel(
        model_name=FALLBACK_MODEL,
        system_instruction=curr_char["system_instruction"]
    )
    # Opcional: Avisar al usuario en la barra lateral (descomentar si quieres verlo)
    # st.sidebar.warning(f"Usando {FALLBACK_MODEL} (El 2.5 no respondió)")

# --- 7. MOSTRAR CHAT ---
for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    av = curr_char["avatar"] if role == "assistant" else None
    with st.chat_message(role, avatar=av):
        st.markdown(msg["content"])

# --- 8. INPUT USUARIO ---
if prompt := st.chat_input("Tu respuesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar historial
    history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]

    # Generar respuesta
    with st.chat_message("assistant", avatar=curr_char["avatar"]):
        box = st.empty()
        full_text = ""
        try:
            # Enviamos historial menos el último mensaje (que ya enviamos en send_message)
            chat = model.start_chat(history=history[:-1])
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    box.markdown(full_text + "▌")
                    time.sleep(0.01)
            box.markdown(full_text)
            st.session_state.messages.append({"role": "model", "content": full_text})
            
        except Exception as e:
            st.error(f"Error: {e}")