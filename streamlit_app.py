import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
import tempfile
import time
import re # Importamos expresiones regulares para limpiar el texto

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(
    page_title="El Sueño de Leonor - Experiencia Interactiva",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ESTILOS CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital@0;1&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Lora', serif;
        background-color: #fdfbf7;
        color: #4b3621 !important;
    }
    
    h1 {
        font-family: 'Cinzel', serif;
        color: #5e3c38 !important;
        text-align: center;
        text-transform: uppercase;
        text-shadow: 2px 2px 4px #d4c5b0;
    }
    
    h3 { color: #8b5e3c !important; text-align: center; font-style: italic; }

    .stButton button {
        background-color: transparent; border: 2px solid #8b5e3c; color: #5e3c38 !important;
        border-radius: 10px; transition: 0.3s; font-weight: bold;
    }
    .stButton button:hover {
        background-color: #5e3c38; color: white !important; transform: scale(1.05);
    }
    
    .stChatMessage { background-color: #ffffff; border: 1px solid #e0d0c0; border-radius: 15px; }
    .stChatMessage p { color: #2c1e1a !important; }
    
    #MainMenu, footer, header {visibility: hidden;}
    .stTextInput input { color: #2c1e1a !important; background-color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE ESTADO ---
if "page" not in st.session_state: st.session_state.page = "portada"
if "current_char" not in st.session_state: st.session_state.current_char = None
if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. CONEXIÓN API (GEMINI) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Falta API Key en .streamlit/secrets.toml")
    st.stop()

# --- 4. FUNCIONES DE AUDIO (BLINDADAS) ---

def limpiar_texto(texto):
    """Elimina markdown (*, #, -) para que el TTS no falle"""
    # Eliminar asteriscos, almohadillas y guiones bajos
    limpio = texto.replace("*", "").replace("#", "").replace("_", "")
    # Eliminar enlaces markdown
    limpio = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', limpio)
    return limpio

async def generar_audio_edge(texto, voz):
    """Genera audio usando Microsoft Edge TTS"""
    texto_limpio = limpiar_texto(texto)
    
    # Si el texto es muy corto o vacío, no generamos nada para evitar error
    if not texto_limpio or len(texto_limpio.strip()) < 2:
        return None

    try:
        communicate = edge_tts.Communicate(texto_limpio, voz)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            await communicate.save(fp.name)
            return fp.name
    except Exception as e:
        # Si falla, devolvemos None en lugar de romper la app
        print(f"Error generando audio: {e}")
        return None

# --- 5. PERSONAJES ---
CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo",
        "role": "La Protagonista",
        "avatar": "img/leonor.png", 
        "voice": "es-ES-ElviraNeural", 
        "greeting": "Bienvenido a Villa Aurora. Apenas he deshecho mi equipaje. ¿Traéis noticias de Madrid?",
        "system_instruction": """
            Eres Leonor Polo, protagonista de 'El Sueño de Leonor'. (S.XIX).
            Institutriz culta, resiliente. Hablas con elegancia.
            Responde de forma breve y concisa.
        """
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar",
        "role": "El Dueño",
        "avatar": "img/maximiliano.png", 
        "voice": "es-ES-AlvaroNeural", 
        "greeting": "¿Quién sois? No recibo visitas sin cita previa.",
        "system_instruction": """
            Eres Maximiliano Alcázar. Rico, atormentado, brusco pero noble.
            Hablas con autoridad. Responde de forma breve y concisa.
        """
    },
    "mercedes": {
        "name": "Doña Mercedes",
        "role": "Ama de Llaves",
        "avatar": "img/mercedes.png", 
        "voice": "es-ES-AbrilNeural", 
        "greeting": "Límpiese los pies. El Señor no está para nadie.",
        "system_instruction": """
            Eres Doña Mercedes, Ama de Llaves. Estricta y protectora.
            Responde de forma breve y concisa.
        """
    },
    "elena": {
        "name": "Elena",
        "role": "Espíritu",
        "avatar": "img/elena.png", 
        "voice": "es-MX-DaliaNeural", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas...",
        "system_instruction": """
            Eres el espíritu de Elena. Dulce, etérea y onírica.
            Responde de forma breve y concisa.
        """
    }
}

# --- 6. NAVEGACIÓN ---
def ir_a_seleccion(): st.session_state.page = "seleccion"; st.rerun()
def ir_a_chat(p): 
    st.session_state.current_char = p; 
    st.session_state.page = "chat"; 
    st.session_state.messages = [{"role": "model", "content": CHARACTERS[p]["greeting"]}]
    st.rerun()
def volver(): st.session_state.page = "portada"; st.rerun()

# --- 7. VISTAS ---
if st.session_state.page == "portada":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("EL SUEÑO DE LEONOR")
    st.markdown("<h3>Una experiencia interactiva en el Romanticismo Español</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("img/villa_aurora.png", use_container_width=True)
        except: st.image("https://placehold.co/600x400/png?text=Villa+Aurora", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗝️ LLAMAR A LA PUERTA", use_container_width=True): ir_a_seleccion()

elif st.session_state.page == "seleccion":
    st.title("EL VESTÍBULO")
    st.markdown("<h3>¿Con quién desea hablar?</h3>", unsafe_allow_html=True)
    st.markdown("---")
    cols = st.columns(4)
    keys = list(CHARACTERS.keys())
    for i, col in enumerate(cols):
        if i < len(keys):
            k = keys[i]
            d = CHARACTERS[k]
            with col:
                try: st.image(d["avatar"], use_container_width=True)
                except: pass
                if st.button(f"{d['name'].split()[0]}", key=k): ir_a_chat(k)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Volver"): volver()

elif st.session_state.page == "chat":
    key = st.session_state.current_char
    data = CHARACTERS[key]
    
    c1, c2 = st.columns([1, 10])
    with c1: 
        if st.button("⬅️"): ir_a_seleccion()
    with c2: st.subheader(f"{data['name']}")

    for msg in st.session_state.messages:
        role = "assistant" if msg["role"] == "model" else "user"
        av = data["avatar"] if role == "assistant" else None
        with st.chat_message(role, avatar=av): st.markdown(msg["content"])

    # Fallback de modelo si el preview falla
    try: model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025", system_instruction=data["system_instruction"])
    except: model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=data["system_instruction"])

    if prompt := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=data["avatar"]):
            box = st.empty()
            full_text = ""
            history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
            
            try:
                chat = model.start_chat(history=history[:-1])
                response = chat.send_message(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        box.markdown(full_text + "▌")
                        time.sleep(0.01)
                box.markdown(full_text)
                st.session_state.messages.append({"role": "model", "content": full_text})
                
                # --- AUDIO ROBUSTO ---
                # Limpiamos el texto antes de enviarlo
                with st.spinner("🔊 ..."):
                    try:
                        audio_file = asyncio.run(generar_audio_edge(full_text, data["voice"]))
                        if audio_file:
                            st.audio(audio_file, format='audio/mp3', autoplay=True)
                        else:
                            st.warning("(Audio no disponible para este mensaje)")
                    except Exception as e:
                        # Si falla el audio, no rompemos el chat, solo avisamos
                        print(f"Error audio: {e}")

            except Exception as e:
                st.error(f"Error Gemini: {e}")