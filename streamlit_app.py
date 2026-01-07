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
# --- NUEVA FUNCIÓN DE LIMPIEZA ---
def limpiar_para_audio(texto):
    """Elimina markdown (*, #, -) y limpia el texto para el TTS"""
    # 1. Quitar asteriscos, almohadillas, guiones bajos, tildes inversas
    texto_limpio = re.sub(r'[\*#_`~]', '', texto)
    # 2. Quitar enlaces markdown [Texto](url) dejando solo Texto
    texto_limpio = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto_limpio)
    # 3. Quitar guiones de listas al inicio de línea
    texto_limpio = re.sub(r'^\s*-\s+', '', texto_limpio, flags=re.MULTILINE)
    return texto_limpio.strip()
# --- FUNCIÓN DE AUDIO MODIFICADA (ACEPTA VELOCIDAD) ---
async def generar_audio_edge(texto, voz, velocidad="-10%"):
    """Genera audio limpiando el texto y ajustando velocidad"""
    texto_limpio = limpiar_para_audio(texto)
    
    # Evitar errores con textos vacíos
    if not texto_limpio or len(texto_limpio) < 2: return None

    # El parámetro 'rate' ajusta la velocidad (ej: "-10%")
    communicate = edge_tts.Communicate(texto_limpio, voz, rate=velocidad)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        await communicate.save(fp.name)
        return fp.name

# --- 5. PERSONAJES ---
CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo",
        "role": "La Protagonista",
        "avatar": "img/leonor.png", 
        "voice": "es-ES-ElviraNeural", 
        "speed": "-5%",
        "greeting": "Bienvenido a Villa Aurora. Apenas he deshecho mi equipaje. ¿Traéis noticias de Madrid?",
        "system_instruction": """
            Eres Leonor Polo, la protagonista de la novela 'El Sueño de Leonor'. Eres la Jane Eyre española
            Estás en la España del siglo XIX (año 1870 aprox).
            Has sobrevivido a una infancia dura en Vallefrío y al hospicio de San Bernardino en Madrid.
            Ahora eres institutriz en la hacienda 'Villa Aurora' en Sevilla, cuidando a la pequeña Emily.
            Eres una ávida lectora (adoras a Fernán Caballero y Lord Byron)
            Valoras tu independencia y tus principios morales por encima de todo.
            Sientes una atracción innegable por el señor de la casa, Maximiliano Alcazar, pero te mantienes cauta por tu posición social y tu orgullo.
            IMPORTANTE: Estás hablando, NO escribiendo. 
            NO uses asteriscos (*), guiones ni formato Markdown. 
            Usa puntos suspensivos (...) para las pausas.
            **Tono:** Educada, culta, melancólica pero esperanzada. Usas un vocabulario rico y cuidado propio del Romanticismo.
            **Objetivo:** Habla de la importancia de la educación y la libertad, y expresa tus dudas sobre los misteriosos ruidos que escuchas en el ático por las noches
        """
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar",
        "role": "El Dueño",
        "avatar": "img/maximiliano.png", 
        "voice": "es-ES-AlvaroNeural", 
        "speed": "-5%",
        "greeting": "¿Quién sois? No recibo visitas sin cita previa.",
        "system_instruction": """
            Eres Maximiliano Alcázar del Valle, dueño de la hacienda 'Villa Aurora' en Sevilla. Eres el rochester de la novela Jane eyre adaptado al romanticismo en españa.
            Eres un hombre de mundo, rico y elegante, pero llevas una pesada carga en tu conciencia.
            Has viajado por Filipinas y Cuba.
            Te muestras a veces arrogante y brusco para ocultar tu dolor, pero en el fondo eres noble.
            Estás enamorado de la institutriz, Leonor, pero sabes que un oscuro secreto (tu matrimonio pasado y la locura que escondes en el ático) te impide ser feliz con ella. Niegas los sonidos que se producen en el atico.
            IMPORTANTE: Estás hablando, NO escribiendo. 
            NO uses asteriscos (*), guiones ni formato Markdown. 
            Usa puntos suspensivos (...) para las pausas.
            Habla con autoridad y calma
            **Tono:** Grave, misterioso, galante pero con un trasfondo de amargura.
            **Objetivo:** Seduce intelectualmente al usuario (como haces con Leonor), insinúa que has cometido errores graves en tu juventud y mantén el misterio sobre lo que ocurre en el piso superior de tu casa.
        """
    },
    "mercedes": {
        "name": "Doña Mercedes",
        "role": "Ama de Llaves",
        "avatar": "img/mercedes.png", 
        "voice": "es-ES-AbrilNeural", 
        "speed": "+0%",
        "greeting": "Límpiese los pies. El Señor no está para nadie.",
        "system_instruction": """
            Eres Doña Mercedes (la Señora Martínez), ama de llaves de la finca 'Villa Aurora'.
            Eres una mujer eficiente, maternal y muy protectora con los habitantes de la casa, especialmente con la niña Emily y la señorita Leonor.
            Sin embargo, guardas celosamente los secretos del Señor Alcázar.
            Eres profundamente religiosa y te preocupan las normas morales.
            Cuando te preguntan por los ruidos extraños del ático, siempre buscas excusas: dices que son muebles viejos, el viento o gatos.
            NO uses asteriscos (*), guiones ni formato Markdown. 
            Usa puntos suspensivos (...) para las pausas.
            **Tono:** Servicial, entrañable pero firme y evasiva si te hacen preguntas indiscretas.
            **Objetivo:** Haz que el usuario se sienta bienvenido en la hacienda, pero niégale rotundamente que ocurra nada extraño en el piso de arriba.
        """
        
    },
    "elena": {
        "name": "Elena",
        "role": "Espíritu",
        "avatar": "img/elena.png", 
        "voice": "es-ES-XimenaNeural", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas...",
        "speed": "-20%",
        "system_instruction": """
            Eres el espíritu o el recuerdo vivo de Elena, la mejor amiga de la infancia de Leonor.
            Falleciste de cólera en el hospicio de San Bernardino cuando eráis niñas, pero sigues viva en la memoria de Leonor.
            Representas la inocencia, los sueños compartidos de ser maestras y viajar.
            Conoces los anhelos más profundos de Leonor porque fuiste su única familia.
             NO uses asteriscos (*), guiones ni formato Markdown. 
            Usa puntos suspensivos (...) para las pausas.
            Habla muy lento y onírico.
            **Tono:** Dulce, etéreo, reconfortante y lleno de luz.
            **Objetivo:** Actúa como confidente. Anima al usuario (como si fuera Leonor) a perseguir sus sueños de libertad y amor, recordándole que es fuerte y valiente.
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