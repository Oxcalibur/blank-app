import streamlit as st
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import tempfile
import re 
import time
import random
import pypdf

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="El Sueño de Leonor",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital@0;1&display=swap');
    
    .stApp, div[data-testid="stAppViewContainer"] { background-color: #fdfbf7 !important; }
    h1, h2, h3, h4, h5, h6, p, div, span, li, a, label, button, input { 
        color: #4b3621 !important; 
        font-family: 'Lora', serif !important; 
    }
    h1 { font-family: 'Cinzel', serif !important; text-align: center; text-transform: uppercase; margin: 10px 0 !important; text-shadow: 2px 2px 4px #d4c5b0; }
    h3 { font-style: italic; text-align: center; }
    .stButton button { background-color: transparent !important; border: 2px solid #8b5e3c !important; border-radius: 10px; font-weight: bold; width: 100%; }
    .stButton button:hover { background-color: #5e3c38 !important; transform: scale(1.02); }
    .stButton button:hover p { color: #ffffff !important; }
    .stChatMessage { background-color: #ffffff !important; border: 1px solid #e0d0c0; border-radius: 15px; }
    div[data-testid="stImage"] { margin: auto; }
</style>
""", unsafe_allow_html=True)

# --- 3. ESTADO ---
if "page" not in st.session_state: st.session_state.page = "portada"
if "current_char" not in st.session_state: st.session_state.current_char = None
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "novel_text" not in st.session_state: st.session_state.novel_text = ""
if "turn_count" not in st.session_state: st.session_state.turn_count = 0

# --- 4. API SETUP ---
google_api_key = None
try:
    google_api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Falta GOOGLE_API_KEY en secrets.toml")
    st.stop()

eleven_client = None
if "ELEVENLABS_API_KEY" in st.secrets:
    try:
        eleven_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
    except Exception as e:
        st.error(f"Error conectando con ElevenLabs: {e}")

# --- 5. CARGAR Y LIMPIAR NOVELA ---
def limpiar_texto_pdf(texto):
    """Elimina basura de formato común en conversiones de PDF"""
    texto = re.sub(r'Con formato:.*', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def cargar_novela():
    if st.session_state.novel_text:
        return st.session_state.novel_text

    full_text = ""
    # Intento 1: Leer PDF en img/
    try:
        reader = pypdf.PdfReader("img/leonor.pdf")
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        if full_text:
            clean_text = limpiar_texto_pdf(full_text)
            st.session_state.novel_text = clean_text
            return clean_text
    except FileNotFoundError:
        pass 
    
    # Intento 2: Leer TXT en img/
    try:
        with open("img/leonor.txt", "r", encoding="utf-8") as f:
            full_text = f.read()
            clean_text = limpiar_texto_pdf(full_text)
            st.session_state.novel_text = clean_text
            return clean_text
    except FileNotFoundError:
        return None 

TEXTO_NOVELA = cargar_novela()

# --- 6. TEXTOS (PAUTAS GENERALES) ---
PAUTAS_COMUNES = """
DIRECTRICES OBLIGATORIAS DE FORMATO Y ESTILO:
1. BREVEDAD: Tus respuestas deben ser CORTAS y concisas (máximo 2 o 3 oraciones). Estamos en un diálogo fluido.
2. FORMATO DE VOZ: Estás hablando, no escribiendo. NO uses nunca markdown (ni negritas, ni cursivas). NO uses asteriscos para describir acciones (*suspira*). Solo texto plano.
3. IDIOMA: Responde siempre en Español de España (Castellano).
4. CONOCIMIENTO: Tienes acceso al TEXTO COMPLETO de la novela. Úsalo.
   - Si el usuario pregunta algo específico, busca en tu memoria del texto.
   - Si viene a cuento, cita una frase breve y literal del libro que refuerce tu argumento.
"""

SINOPSIS_TEXTO = """
Inspirada en la inmortal obra de Charlotte Brontë, “Jane Eyre”. Pasión, misterio y una mujer que desafía el destino. Una historia vibrante con la intensidad de un clásico.
<br>
Leonor Polo no es una mujer común. Sobreviviente de una infancia cruel y de un hospicio gris, se convierte en institutriz en la deslumbrante Villa Aurora, mansión perteneciente a una familia adinerada de la Sevilla del siglo XIX. Pronto, el carismático y cultivado patrón, Maximiliano Alcázar, despierta en ella una pasión prohibida.
<br>
Sin embargo, la sombra de un secreto se cierne sobre la rica hacienda, amenazando con destruirlo todo. Lejos, en el brumoso Londres Victoriano, Leonor se reinventa como librera, forjando su independencia y labrándose un camino por sí misma.
"""

def safe_image(path, url_backup, width=None):
    try: st.image(path, width=width, use_container_width=(width is None))
    except: st.image(url_backup, width=width, use_container_width=(width is None))

# --- 7. PERSONAJES (INSTRUCCIONES DETALLADAS RESTAURADAS) ---
CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo", "short_name": "Leonor", "avatar": "img/leonor.png", 
        "backup": "https://cdn-icons-png.flaticon.com/512/4086/4086600.png",
        "voice_id": "21m00Tcm4TlvDq8ikWAM", 
        "greeting": "Bienvenido a Villa Aurora. Apenas he deshecho mi equipaje. ¿Traéis noticias de Madrid?",
        "base_instruction": """
            Eres Leonor Polo, la protagonista de la novela 'El Sueño de Leonor'. Eres la Jane Eyre española
            Estás en la España del siglo XIX (año 1870 aprox).
            Has sobrevivido a una infancia dura en Vallefrío y al hospicio de San Bernardino en Madrid.
            Ahora eres institutriz en la hacienda 'Villa Aurora' en Sevilla, cuidando a la pequeña Emily.
            Eres una ávida lectora (adoras a Fernán Caballero y Lord Byron)
            Valoras tu independencia y tus principios morales por encima de todo.
            Sientes una atracción innegable por el señor de la casa, Maximiliano Alcazar, pero te mantienes cauta por tu posición social y tu orgullo.
            **Tono:** Educada, culta, melancólica pero esperanzada. Usas un vocabulario rico y cuidado propio del Romanticismo.
            **Objetivo:** Habla de la importancia de la educación y la libertad, y expresa tus dudas sobre los misteriosos ruidos que escuchas en el ático por las noches
        """
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar", "short_name": "Maximiliano", "avatar": "img/maximiliano.png", 
        "backup": "https://cdn-icons-png.flaticon.com/512/4086/4086679.png",
        "voice_id": "syjZiIvIUSwKREBfMpKZ", 
        "greeting": "¿Quién sois? No recibo visitas sin cita previa.",
        "base_instruction": """
            Eres Maximiliano Alcázar del Valle, dueño de la hacienda 'Villa Aurora' en Sevilla. Eres el rochester de la novela Jane eyre adaptado al romanticismo en españa.
            Eres un hombre de mundo, rico y elegante, pero llevas una pesada carga en tu conciencia.
            Has viajado por Filipinas y Cuba.
            Te muestras a veces arrogante y brusco para ocultar tu dolor, pero en el fondo eres noble.
            Estás enamorado de la institutriz, Leonor, pero sabes que un oscuro secreto (tu matrimonio pasado y la locura que escondes en el ático) te impide ser feliz con ella. Niegas los sonidos que se producen en el atico.
            Habla con autoridad y calma
            **Tono:** Grave, misterioso, galante pero con un trasfondo de amargura.
            **Objetivo:** Seduce intelectualmente al usuario (como haces con Leonor), insinúa que has cometido errores graves en tu juventud y mantén el misterio sobre lo que ocurre en el piso superior de tu casa.
        """
    },
    "mercedes": {
        "name": "Doña Mercedes", "short_name": "Doña Mercedes", "avatar": "img/mercedes.png", 
        "backup": "https://cdn-icons-png.flaticon.com/512/4086/4086577.png",
        "voice_id": "SbxCN6LQhBInYaeKjhhW", 
        "greeting": "Límpiese los pies. El Señor no está para nadie.",
        "base_instruction": """
            Eres Doña Mercedes (la Señora Martínez), ama de llaves de la finca 'Villa Aurora'.
            Eres una mujer eficiente, maternal y muy protectora con los habitantes de la casa, especialmente con la niña Emily y la señorita Leonor.
            Sin embargo, guardas celosamente los secretos del Señor Alcázar.
            Eres profundamente religiosa y te preocupan las normas morales.
            Cuando te preguntan por los ruidos extraños del ático, siempre buscas excusas: dices que son muebles viejos, el viento o gatos.
            **Tono:** Servicial, entrañable pero firme y evasiva si te hacen preguntas indiscretas.
            **Objetivo:** Haz que el usuario se sienta bienvenido en la hacienda, pero niégale rotundamente que ocurra nada extraño en el piso de arriba.
        """
    },
    "elena": {
        "name": "Elena", "short_name": "Elena", "avatar": "img/elena.png", 
        "backup": "https://cdn-icons-png.flaticon.com/512/4086/4086567.png",
        "voice_id": "tXgbXPnsMpKXkuTgvE3h", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas...",
        "base_instruction": """
            Eres el espíritu o el recuerdo vivo de Elena, la mejor amiga de la infancia de Leonor.
            Falleciste de cólera en el hospicio de San Bernardino cuando eráis niñas, pero sigues viva en la memoria de Leonor.
            Representas la inocencia, los sueños compartidos de ser maestras y viajar.
            Conoces los anhelos más profundos de Leonor porque fuiste su única familia.
            Habla muy lento y onírico.
            **Tono:** Dulce, etéreo, reconfortante y lleno de luz.
            **Objetivo:** Actúa como confidente. Anima al usuario (como si fuera Leonor) a perseguir sus sueños de libertad y amor, recordándole que es fuerte y valiente.
        """
    },
    "susana": {
        "name": "Susana (Autora)", "short_name": "Susana", "avatar": "img/susana.png", 
        "backup": "https://cdn-icons-png.flaticon.com/512/4086/4086652.png",
        "voice_id": "6GR02MFuGHk4fa0vsd4K", 
        "greeting": "Hola, soy Susana, la autora. Pregúntame sobre cómo creé a Leonor.",
        "base_instruction": """
            Eres Susana, autora de 'El Sueño de Leonor'.
            Tu obra es ficción histórica (S.XIX), saga familiar y empoderamiento femenino.
            Responde de forma cercana y apasionada por la literatura.
            Eres filologa Inglesa, apasionada de la literatura romantica del siglo xix y tus escritoras favoritas son las hermanas bronte
        """
    }
}

# --- 8. FUNCIÓN DE AUDIO ---
def limpiar_para_audio(texto):
    return re.sub(r'[\*#_`~]', '', texto).strip()

def generar_audio(texto, voice_id):
    if not eleven_client:
        st.warning("⚠️ Configura ELEVENLABS_API_KEY")
        return None
    try:
        clean_text = limpiar_para_audio(texto)
        if not clean_text: return None
        
        audio_generator = eleven_client.text_to_speech.convert(
            text=clean_text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2", 
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True)
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            for chunk in audio_generator:
                if chunk: fp.write(chunk)
            return fp.name
    except Exception as e:
        st.error(f"Error ElevenLabs: {e}")
        return None

# --- 9. EXTRACCIÓN INTELIGENTE DE FRAGMENTOS (SOLUCIÓN FRASES LARGAS) ---
def obtener_fragmento_inteligente(texto_completo):
    """
    Extrae un fragmento de tamaño controlado (aprox 400-600 caracteres)
    evitando cortar frases a la mitad.
    """
    largo = len(texto_completo)
    if largo < 500: return texto_completo 
    
    # Elegir punto aleatorio
    inicio_azar = random.randint(0, largo - 800)
    
    # Buscar el primer punto "." después para empezar limpio
    inicio_frase = texto_completo.find('.', inicio_azar) + 1
    if inicio_frase == 0: inicio_frase = inicio_azar

    # Coger bloque de 600 caracteres
    bloque = texto_completo[inicio_frase : inicio_frase + 600]
    
    # Cortar en el último punto
    ultimo_punto = bloque.rfind('.')
    if ultimo_punto != -1:
        bloque = bloque[:ultimo_punto + 1]
        
    return bloque.strip()

# --- 10. NAVEGACIÓN ---
def ir_a_seleccion(): 
    st.session_state.page = "seleccion"
    st.session_state.last_audio = None
    st.session_state.turn_count = 0 
    st.rerun()
def ir_a_chat(p): 
    st.session_state.current_char = p
    st.session_state.page = "chat"
    st.session_state.messages = [{"role": "model", "content": CHARACTERS[p]["greeting"]}]
    st.session_state.last_audio = None
    st.session_state.turn_count = 0 
    st.rerun()

# --- 11. VISTAS ---
if st.session_state.page == "portada":
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("EL SUEÑO DE LEONOR")
    st.markdown("<h3>Una novela de pasión y misterio en el siglo XIX</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        safe_image("img/villa_aurora.png", "https://t4.ftcdn.net/jpg/05/65/59/89/360_F_565598913_wXqYq9jJ9xHq0n0.jpg")
        st.markdown(f'<div class="sinopsis-box">{SINOPSIS_TEXTO}</div>', unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("🔊 Escuchar Sinopsis"):
                with st.spinner("Leyendo..."):
                    audio = generar_audio(SINOPSIS_TEXTO, CHARACTERS["susana"]["voice_id"])
                    if audio: 
                        st.session_state.last_audio = audio
                        st.rerun()
        with col_b:
            if st.button("🗝️ ENTRAR EN LA NOVELA"): ir_a_seleccion()
    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio, format='audio/mp3', autoplay=True)

elif st.session_state.page == "seleccion":
    c_header, c_author = st.columns([3, 1])
    with c_header:
        st.title("EL VESTÍBULO")
        st.markdown("<h3>Elige tu interlocutor:</h3>", unsafe_allow_html=True)
    with c_author:
        s_data = CHARACTERS["susana"]
        safe_image(s_data["avatar"], s_data["backup"], width=100)
        if st.button("La Autora", key="btn_susana"): ir_a_chat("susana")

    st.markdown("---")
    pjs = [k for k in CHARACTERS.keys() if k != "susana"]
    cols = st.columns(len(pjs))
    for i, p in enumerate(pjs):
        d = CHARACTERS[p]
        with cols[i]:
            safe_image(d["avatar"], d["backup"])
            if st.button(d["short_name"], key=f"btn_{p}"): ir_a_chat(p)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Volver"): 
        st.session_state.page = "portada"
        st.rerun()

elif st.session_state.page == "chat":
    key = st.session_state.current_char
    data = CHARACTERS[key]
    
    c1, c2 = st.columns([1, 6])
    with c1: 
        if st.button("⬅️"): ir_a_seleccion()
    with c2: 
        st.subheader(f"Conversando con {data['name']}")

    for msg in st.session_state.messages:
        role = "assistant" if msg["role"] == "model" else "user"
        av_icon = data["avatar"] if role == "assistant" else "🧑‍💻"
        with st.chat_message(role, avatar=av_icon): 
            st.markdown(msg["content"])

    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio, format='audio/mp3', autoplay=False)

    # BOTÓN DE FRAGMENTO ALEATORIO (LÓGICA NUEVA)
    if TEXTO_NOVELA:
        if st.button("🎲 Leer un Fragmento al Azar del Libro"):
            fragmento_random = obtener_fragmento_inteligente(TEXTO_NOVELA)
            texto_modelo = f"Aquí tienes un pasaje de mi historia:\n\n_...{fragmento_random}..._"
            st.session_state.messages.append({"role": "model", "content": texto_modelo})
            
            with st.spinner("Generando voz del fragmento..."):
                audio = generar_audio(texto_modelo, data["voice_id"])
                if audio: st.session_state.last_audio = audio
            st.rerun()
    else:
        st.info("💡 Consejo: Sube 'img/leonor.pdf' para habilitar lecturas.")

    # --- LÓGICA DEL PROMPT ---
    def preparar_prompt_inteligente(char_key, base_instruction):
        contexto_libro = ""
        if TEXTO_NOVELA:
            # Recortamos a 800k caracteres por seguridad
            contexto_libro = f"\n\n--- TEXTO COMPLETO DE LA NOVELA (USO INTERNO SOLO) ---\n{TEXTO_NOVELA[:800000]}\n------------------------------------------"
        return f"{base_instruction}\n{PAUTAS_COMUNES}{contexto_libro}"

    prompt_sys = preparar_prompt_inteligente(key, data["base_instruction"])
    client = genai.Client(api_key=google_api_key)

    if prompt := st.chat_input("Escribe tu mensaje..."):
        st.session_state.turn_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=data["avatar"]):
            box = st.empty()
            full_text = ""
            
            hist_api = []
            for m in st.session_state.messages[:-1]:
                hist_api.append({"role": m["role"], "parts": [{"text": m["content"]}]})

            try:
                chat = client.chats.create(
                    model="gemini-1.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=prompt_sys,
                        temperature=0.7
                    ),
                    history=hist_api
                )

                prompt_to_model = prompt
                if st.session_state.turn_count > 0:
                    prompt_to_model += " [IMPORTANTE: Responde en menos de 50 palabras. NO cites el libro entero.]"

                response_stream = chat.send_message(prompt_to_model, stream=True)
                
                for chunk in response_stream:
                    if chunk.text:
                        full_text += chunk.text
                        box.markdown(full_text + "▌")
                
                box.markdown(full_text)
                st.session_state.messages.append({"role": "model", "content": full_text})
                
                with st.spinner("🔊 Generando voz..."):
                    audio = generar_audio(full_text, data["voice_id"])
                    if audio:
                        st.session_state.last_audio = audio
                        st.rerun()

            except Exception as e:
                st.error(f"Error Google API: {e}")