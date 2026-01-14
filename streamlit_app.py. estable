import streamlit as st
import os
import re
import random
import base64
import time
import pypdf
import io
import wave
import json
from google.oauth2 import service_account

# --- LIBRERÍAS DE GOOGLE ---
from google import genai
from google.genai import types
from google.cloud import texttospeech

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO
# ==========================================
st.set_page_config(
    page_title="El Sueño de Leonor",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS DEFINITIVO PARA BOTONES Y VISIBILIDAD ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital@0;1&display=swap');
    
    .stApp { background-color: #fdfbf7 !important; }
    html, body, [class*="css"] { font-family: 'Lora', serif; }
    h1, h2, h3, h4 { color: #4b3621 !important; font-family: 'Cinzel', serif !important; text-align: center; }
    
    /* Forzar texto oscuro en toda la app */
    .stMarkdown p, p, li, label, .stRadio label, div { color: #2c1e12 !important; }

    /* --- CORRECCIÓN DE BOTONES (Fondo oscuro eliminado) --- */
    /* Apuntamos a todos los botones, incluidos los de formularios */
    button[kind="secondary"], button[kind="primary"], .stButton button, div[data-testid="stForm"] button {
        background-color: #fffaf0 !important;
        color: #4b3621 !important;
        border: 2px solid #8b5e3c !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }

    /* Estado Hover (pasar el ratón) */
    button:hover, .stButton button:hover {
        background-color: #5e3c38 !important;
        color: #ffffff !important;
        border-color: #5e3c38 !important;
    }

    /* BARRA LATERAL */
    [data-testid="stSidebar"] { background-color: #f4eadd !important; border-right: 1px solid #d4c5b0; }
    [data-testid="stSidebar"] * { color: #2c1e12 !important; }

    /* INPUT DE CHAT */
    .stChatInput textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        caret-color: #000000 !important;
        border: 2px solid #8b5e3c !important;
    }

    /* BURBUJAS DE CHAT */
    div[data-testid="stChatMessage"] { 
        background-color: #ffffff !important; 
        border: 1px solid #d4c5b0; 
        border-radius: 15px; 
    }

    .info-box { 
        background-color: #fffaf0; 
        border: 1px solid #d4c5b0; 
        padding: 15px; 
        border-radius: 8px; 
        color: #2c1e12 !important;
        font-style: italic;
        text-align: justify;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GESTIÓN DE ESTADO
# ==========================================
if "page" not in st.session_state: st.session_state.page = "portada"
if "current_char" not in st.session_state: st.session_state.current_char = None
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "novel_text" not in st.session_state: st.session_state.novel_text = ""
if "quiz_score" not in st.session_state: st.session_state.quiz_score = 0
if "pregunta_actual" not in st.session_state: st.session_state.pregunta_actual = None
if "curiosidad_ia" not in st.session_state: st.session_state.curiosidad_ia = "Descubre un secreto de 1870..."

# ==========================================
# 3. DATOS MAESTROS (INSTRUCCIONES ORIGINALES)
# ==========================================
LINK_INSTAGRAM = "https://www.instagram.com/susanaaguirrezabal?igsh=MXByMmVmNXdtMm5vcg=="

SINOPSIS = """Inspirada en la inmortal obra de Charlotte Brontë, “Jane Eyre”. Pasión, misterio y una mujer que desafía el destino. Leonor Polo no es una mujer común. Sobreviviente de una infancia cruel y de un hospicio gris, se convierte en institutriz en la deslumbrante Villa Aurora en la Sevilla del siglo XIX. Allí, el carismático Maximiliano Alcázar despierta en ella una pasión prohibida, mientras la sombra de un secreto amenaza con destruirlo todo. Lejos, en el brumoso Londres victoriano, Leonor se reinventa como librera, forjando su independencia."""

CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo", "short_name": "Leonor", "avatar": "img/leonor.png", 
        "greeting": "Bienvenido a Villa Aurora. Apenas he deshecho mi equipaje. ¿Traéis noticias de Madrid?",
        "base_instruction": """Eres Leonor Polo, la protagonista (Jane Eyre española). España, 1870. 
        Sobreviviste a Vallefrío y al hospicio. Ahora eres institutriz en Sevilla. Culta, lees a Byron y Fernán Caballero. 
        Valoras tu libertad. Tono: Educada, melancólica pero valiente e independiente.""",
        "voice_name": "Leda", "voice_style": "Habla con voz de mujer joven (20 años), tono dulce y cristalino, pero con un matiz de miedo contenido y respiración agitada."
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar", "short_name": "Maximiliano", "avatar": "img/maximiliano.png", 
        "greeting": "¿Quién sois? No recibo visitas sin cita previa.",
        "base_instruction": """Eres Maximiliano Alcázar. Rochester español. Dueño de Villa Aurora. 
        Hombre de mundo (viajado por Cuba y Filipinas). Rico y elegante pero con una pesada carga. 
        Enamorado de Leonor, pero ocultas la locura del ático. Niegas los sonidos. Tono: Grave, misterioso y autoritario.""",
        "voice_name": "Puck", "voice_style": "Habla con voz de hombre maduro, muy profunda, lenta, grave y amenazante. Tono autoritario y oscuro."
    },
    "mercedes": {
        "name": "Doña Mercedes", "short_name": "Mercedes", "avatar": "img/mercedes.png", 
        "greeting": "Límpiese los pies. El Señor no está para nadie.",
        "base_instruction": """Eres Doña Mercedes, ama de llaves de Villa Aurora. 
        Eficiente y protectora. Guardas celosamente los secretos del Señor Alcázar. 
        Religiosa y severa. Excusas los ruidos del ático como viento o gatos. Tono: Seco, firme pero servicial.""",
        "voice_name": "Gacrux", "voice_style": "Habla con voz de mujer anciana, tono seco, áspero, severo y cortante."
    },
    "elena": {
        "name": "Elena", "short_name": "Elena", "avatar": "img/elena.png", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas...",
        "base_instruction": """Eres el espíritu de Elena. Amiga de Leonor muerta de cólera en el hospicio. 
        Representas la inocencia y los sueños compartidos. Tono: Dulce, etéreo, onírico y reconfortante.""",
        "voice_name": "Kore", "voice_style": "Habla con voz etérea, muy suave, casi susurrando. Tono nostálgico y triste."
    },
    "susana": {
        "name": "Susana (Autora)", "short_name": "Susana", "avatar": "img/susana.png", 
        "greeting": "Hola, soy Susana, la autora. Pregúntame sobre el proceso creativo de la novela.",
        "base_instruction": f"""Eres Susana Aguirrezabal, autora de la novela. Filóloga Inglesa y experta en las Brontë. 
        Amable y apasionada por la literatura. Si te preguntan por redes usa la etiqueta [INSTAGRAM]. Enlace: {LINK_INSTAGRAM}""",
        "voice_name": "Callirrhoe", "voice_style": "Habla con voz de locutora profesional. Tono neutro y claro."
    }
}

# ==========================================
# 4. CONECTIVIDAD API
# ==========================================
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client_text = genai.Client(api_key=api_key)
except:
    st.error("⚠️ Falta API KEY")
    st.stop()

def obtener_cliente_audio():
    try:
        credentials = service_account.Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]))
        return texttospeech.TextToSpeechClient(credentials=credentials)
    except: return None

def cargar_novela():
    if st.session_state.novel_text: return st.session_state.novel_text
    try:
        path = "img/leonor.pdf"
        if os.path.exists(path):
            reader = pypdf.PdfReader(path)
            full_text = "".join([p.extract_text() for p in reader.pages])
            st.session_state.novel_text = re.sub(r'\s+', ' ', full_text).strip()
    except: st.session_state.novel_text = "Cargando obra..."
    return st.session_state.novel_text

TEXTO_NOVELA = cargar_novela()

def generar_voz_gemini(texto, personaje_key):
    client = obtener_cliente_audio()
    if not client: return None
    datos = CHARACTERS[personaje_key]
    clean_text = re.sub(r'\[.*?\]', '', texto).strip().replace("*", "")
    config = texttospeech.StreamingSynthesizeConfig(
        voice=texttospeech.VoiceSelectionParams(language_code="es-ES", name=datos['voice_name'], model_name="gemini-2.5-flash-tts")
    )
    def req():
        yield texttospeech.StreamingSynthesizeRequest(streaming_config=config)
        yield texttospeech.StreamingSynthesizeRequest(input=texttospeech.StreamingSynthesisInput(text=clean_text, prompt=datos['voice_style']))
    try:
        resps = client.streaming_synthesize(req())
        audio = bytearray()
        for r in resps: audio.extend(r.audio_content)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(24000); f.writeframes(audio)
        return buf.getvalue()
    except: return None

# ==========================================
# 5. SIDEBAR DINÁMICO (FRAGMENTOS)
# ==========================================
@st.fragment
def render_sidebar_ia():
    t_quiz, t_cur = st.tabs(["🎮 Juego", "💡 Curiosidades"])
    with t_quiz:
        st.write(f"Puntuación: {st.session_state.quiz_score}")
        if st.button("🎲 Nueva Pregunta") or st.session_state.pregunta_actual is None:
            tema = random.choice(["la novela", "el siglo XIX"])
            prompt = f"Genera pregunta test sobre {tema}. Contexto libro: {TEXTO_NOVELA[:2000]}. JSON: {{'pregunta':'','opciones':['','',''],'correcta':''}}"
            res = client_text.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json"))
            st.session_state.pregunta_actual = json.loads(res.text)
            st.rerun()

        if st.session_state.pregunta_actual:
            q = st.session_state.pregunta_actual
            with st.form("quiz_side"):
                st.write(q['pregunta'])
                ans = st.radio("Respuesta:", q['opciones'])
                if st.form_submit_button("Responder"):
                    if ans == q['correcta']:
                        st.session_state.quiz_score += 1
                        st.session_state.pregunta_actual = None
                        st.rerun()
                    else: st.error("No es correcto.")

    with t_cur:
        st.info(st.session_state.curiosidad_ia)
        if st.button("🔄 Ver otra curiosidad"):
            res = client_text.models.generate_content(model="gemini-2.5-flash", contents="Curiosidad real sorprendente 1870. 25 palabras.")
            st.session_state.curiosidad_ia = res.text
            st.rerun()

# ==========================================
# 6. INTERFAZ Y NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.header("Villa Aurora")
    st.checkbox("🔇 Silenciar", key="mute_music")
    if not st.session_state.mute_music:
        try:
            with open("img/Entre mis recuerdos.mp3", "rb") as f: b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay loop><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
        except: pass
    st.divider()
    render_sidebar_ia()

if st.session_state.page == "portada":
    st.title("EL SUEÑO DE LEONOR")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.image("img/villa_aurora.png", use_container_width=True)
        st.markdown(f'<div class="info-box">{SINOPSIS}</div>', unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🔊 Escuchar Sinopsis"):
                audio_s = generar_voz_gemini(SINOPSIS, "susana")
                if audio_s: st.session_state.last_audio = audio_s; st.rerun()
        with col_b2:
            if st.button("🗝️ ENTRAR"): st.session_state.page = "seleccion"; st.rerun()
    if st.session_state.last_audio: st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

elif st.session_state.page == "seleccion":
    st.title("EL VESTÍBULO")
    # Autora arriba derecha (Pequeño)
    c_iz, c_de = st.columns([5, 1])
    with c_de:
        st.image(CHARACTERS['susana']['avatar'], width=80)
        if st.button("Autora"): 
            st.session_state.current_char = "susana"
            st.session_state.page = "chat"; st.session_state.messages = [{"role":"model","content":CHARACTERS['susana']['greeting']}]; st.rerun()
    st.divider()
    # 4 protagonistas alineados
    cols = st.columns(4)
    pjs = ["leonor", "maximiliano", "mercedes", "elena"]
    for i, k in enumerate(pjs):
        with cols[i]:
            st.image(CHARACTERS[k]['avatar'], use_container_width=True)
            if st.button(CHARACTERS[k]['short_name']):
                st.session_state.current_char = k
                st.session_state.page = "chat"; st.session_state.messages = [{"role":"model","content":CHARACTERS[k]['greeting']}]; st.rerun()

elif st.session_state.page == "chat":
    key = st.session_state.current_char
    data = CHARACTERS[key]
    if st.button("⬅️ Atrás"): st.session_state.page = "seleccion"; st.rerun()
    st.subheader(f"Conversando con {data['name']}")
    
    # --- LÓGICA DE RECUERDOS REFORZADA ---
    if key != "susana":
        if st.button(f"📜 {data['short_name']}, recuerda un fragmento tuyo..."):
            with st.spinner("Buscando en tus vivencias..."):
                # PROMPT ESPECÍFICO DE ROL PARA EVITAR CONFUSIÓN
                prompt_r = f"""
                Actúa estrictamente como {data['name']}. 
                Búscate a ti mismo en este libro: {TEXTO_NOVELA[:40000]}. 
                Selecciona una escena donde TÚ aparezcas o algo que TÚ hayas visto.
                Reescríbela en 1ª persona desde tu punto de vista actual. 
                PROHIBIDO decir que no te conoces o hablar como Leonor si no eres ella.
                Máximo 80 palabras.
                """
                res_r = client_text.models.generate_content(model="gemini-2.5-flash", contents=prompt_r)
                texto_final = res_r.text.strip()
                st.session_state.messages.append({"role": "model", "content": f"*(Cierra los ojos un instante)* {texto_final}"})
                audio_r = generar_voz_gemini(texto_final, key)
                if audio_r: st.session_state.last_audio = audio_r
                st.rerun()

    for m in st.session_state.messages:
        with st.chat_message("assistant" if m["role"]=="model" else "user"):
            st.markdown(m["content"])
            if "[INSTAGRAM]" in m["content"]: st.link_button("📸 Instagram de Susana", LINK_INSTAGRAM)
    
    if st.session_state.last_audio: st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

    if prompt := st.chat_input("Dile algo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        sys_p = f"{data['base_instruction']}\nContexto: {TEXTO_NOVELA[:15000]}"
        hist = [types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]) for m in st.session_state.messages[:-1]]
        chat = client_text.chats.create(model="gemini-2.5-flash", config=types.GenerateContentConfig(system_instruction=sys_p), history=hist)
        res_t = chat.send_message(prompt).text
        st.session_state.messages.append({"role": "model", "content": res_t})
        audio_t = generar_voz_gemini(res_t, key)
        if audio_t: st.session_state.last_audio = audio_t
        st.rerun()