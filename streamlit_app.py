import streamlit as st
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import tempfile
import re 
import time

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
    
    /* FONDO Y TEXTOS */
    .stApp, div[data-testid="stAppViewContainer"] {
        background-color: #fdfbf7 !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, div, span, li, a, label, button, input { 
        color: #4b3621 !important; 
        font-family: 'Lora', serif !important; 
    }
    
    /* TÍTULOS */
    h1 { 
        font-family: 'Cinzel', serif !important; 
        text-align: center; 
        text-transform: uppercase; 
        text-shadow: 2px 2px 4px #d4c5b0; 
        margin: 10px 0 !important;
    }
    h3 { font-style: italic; text-align: center; }
    
    /* BOTONES */
    .stButton button { 
        background-color: transparent !important; 
        border: 2px solid #8b5e3c !important; 
        border-radius: 10px; 
        font-weight: bold; 
        width: 100%;
    }
    .stButton button:hover { 
        background-color: #5e3c38 !important; 
        transform: scale(1.02); 
    }
    .stButton button:hover p { color: #ffffff !important; }
    
    /* CHAT Y CAJAS */
    .stChatMessage { background-color: #ffffff !important; border: 1px solid #e0d0c0; border-radius: 15px; }
    .sinopsis-box { background-color: #fffaf0; border: 1px solid #d4c5b0; padding: 20px; border-radius: 8px; font-family: 'Cinzel', serif !important; text-align: justify; margin-bottom: 20px; }
    .cita-sugerida { background-color: #f4eadd; border-left: 4px solid #8b5e3c; padding: 15px; margin: 15px 0; border-radius: 5px; }
    
    /* IMÁGENES */
    div[data-testid="stImage"] { margin: auto; }
</style>
""", unsafe_allow_html=True)

# --- 3. ESTADO ---
if "page" not in st.session_state: st.session_state.page = "portada"
if "current_char" not in st.session_state: st.session_state.current_char = None
if "messages" not in st.session_state: st.session_state.messages = []
if "suggested_fragment" not in st.session_state: st.session_state.suggested_fragment = None
if "last_audio" not in st.session_state: st.session_state.last_audio = None

# --- 4. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Falta GOOGLE_API_KEY en secrets.toml")
    st.stop()

# Configuración ElevenLabs
eleven_client = None
if "ELEVENLABS_API_KEY" in st.secrets:
    try:
        eleven_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
    except Exception as e:
        st.error(f"Error conectando con ElevenLabs: {e}")

# --- 5. TEXTOS Y DATOS ---
PAUTAS_COMUNES = """
DIRECTRICES OBLIGATORIAS DE FORMATO Y ESTILO:
1. BREVEDAD: Tus respuestas deben ser CORTAS y concisas (máximo 2 o 3 oraciones). Estamos en un diálogo fluido.
2. FORMATO DE VOZ: Estás hablando, no escribiendo. NO uses nunca markdown (ni negritas, ni cursivas). NO uses asteriscos para describir acciones (*suspira*). Solo texto plano.
3. IDIOMA: Responde siempre en Español de España (Castellano).
"""

SINOPSIS_TEXTO = """
Inspirada en la inmortal obra de Charlotte Brontë, “Jane Eyre”. Pasión, misterio y una mujer que desafía el destino. Una historia vibrante con la intensidad de un clásico.
<br>
Leonor Polo no es una mujer común. Sobreviviente de una infancia cruel y de un hospicio gris, se convierte en institutriz en la deslumbrante Villa Aurora, mansión perteneciente a una familia adinerada de la Sevilla del siglo XIX. Pronto, el carismático y cultivado patrón, Maximiliano Alcázar, despierta en ella una pasión prohibida.
<br>
Sin embargo, la sombra de un secreto se cierne sobre la rica hacienda, amenazando con destruirlo todo. Lejos, en el brumoso Londres Victoriano, Leonor se reinventa como librera, forjando su independencia y labrándose un camino por sí misma.
"""

LIBRO_FRAGMENTOS = {
    "leonor": [
        "La lectura era mi refugio: iba a la biblioteca del salón verde y cogía libros sin que nadie supiera nada. Nadie se daba cuenta, porque en esa casa el único que leía era tío Juan, y ya no vivía.",
        "Villa Aurora era mucho más bella de lo que nunca hubiera imaginado; pero también sentía una extraña inquietud ante tanto lujo. Tenía miedo de que fuera un sueño y me despertara en la casa de tía Guadalupe.",
        "Quería a ese hombre por encima de todo y con toda mi alma. Mi moral victoriana, mis principios férreos… eran solo palabras vacías frente a la fuerza de la realidad. En ese instante, nada más importaba.",
        "El Sueño de Leonor se convirtió el nombre de mi librería, en español para que resultara más exótico. Era un lugar acogedor con estanterías de madera llenas de libros de todos los tamaños y colores."
    ],
    "maximiliano": [
        "Voy a confiar en usted y solo en usted, en nadie más, para que me ayude en esta misión. Una vez me salvó la vida… Por favor, haga usted lo que le pido; y, sobre todo, sea sumamente discreta.",
        "¿No se da cuenta de que estoy representando un papel para acercarla más a mí? Los celos son un arma poderosa; y a lo largo de la historia, como usted seguro que ha leído en tantos libros, ha funcionado.",
        "Soy ciego, manco de una mano, y mucho mayor que usted, y usted es una mujer inteligente, joven e independiente. ¿Se puede saber qué diantres hace con un despojo como yo?",
        "Como has visto, querida mía, soy como un árbol herido por un rayo; ciego y manco."
    ],
    "mercedes": [
        "¡Bienvenida a Villa Aurora, señorita Leonor! Soy la señora Martínez, el ama de llaves de esta casa. ¡Qué alegría tenerla por fin aquí! Debe estar usted agotada después de un viaje tan largo.",
        "La cena se sirve a las ocho y media; cualquier cosa que necesite, estoy a su disposición.",
        "Señorita, ¿Se ha parado a pensar en que ustedes dos son muy diferentes en todos los sentidos? ¿Que el señor Alcázar, además, podría ser su padre, con esos veinte años de diferencia?"
    ],
    "elena": [
        "Tan solo tenía diez años. Tío Juan me acogió cuando madre falleció. Él sí que era un hombre bueno. Me leía cuentos, además me enseñó a leer.",
        "Desde el ventanuco se divisaba parte de Sierra Morena, o eso creía; quizás estaba soñando con ese manto enorme de terciopelo verde con sus bosques espesos llenos de riachuelos.",
        "El aire del atardecer me acarició las mejillas. El olor a flores era dulce. Nunca en mi vida, había experimentado una acogida así."
    ],
    "susana": [
        "Escribir sobre Leonor fue como redescubrir la fuerza que todas llevamos dentro. Quería una heroína que no necesitara ser salvada.",
        "Quise que Villa Aurora fuera un personaje más, con sus luces, sus sombras y ese calor sofocante de Sevilla que lo envuelve todo.",
        "Jane Eyre siempre fue mi inspiración, pero Leonor tiene su propia voz. Es más pasional, más mediterránea, más nuestra."
    ]
}

# --- 6. FUNCIÓN DE AUDIO (ELEVENLABS API v1.0+ CORREGIDA) ---
def limpiar_para_audio(texto):
    texto = re.sub(r'\[\[REF:\d+\]\]', '', texto)
    return re.sub(r'[\*#_`~]', '', texto).strip()

def generar_audio(texto, voice_id):
    if not eleven_client:
        st.warning("⚠️ Configura ELEVENLABS_API_KEY para escuchar el audio.")
        return None
        
    try:
        clean_text = limpiar_para_audio(texto)
        if not clean_text: return None
        
        # Sintaxis ElevenLabs v1.0+
        audio_generator = eleven_client.text_to_speech.convert(
            text=clean_text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2", 
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                stability=0.5, 
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            for chunk in audio_generator:
                if chunk: fp.write(chunk)
            return fp.name

    except Exception as e:
        st.error(f"Error ElevenLabs: {e}")
        return None

# --- 7. CONFIGURACIÓN DE PERSONAJES (IDs DEFINITIVOS) ---
def safe_image(path, url_backup, width=None):
    try: st.image(path, width=width, use_container_width=(width is None))
    except: st.image(url_backup, width=width, use_container_width=(width is None))

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

# --- 8. NAVEGACIÓN ---
def ir_a_seleccion(): 
    st.session_state.page = "seleccion"
    st.session_state.last_audio = None
    st.rerun()
def ir_a_chat(p): 
    st.session_state.current_char = p
    st.session_state.page = "chat"
    st.session_state.messages = [{"role": "model", "content": CHARACTERS[p]["greeting"]}]
    st.session_state.last_audio = None
    st.rerun()

# --- 9. VISTAS ---
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
            st.markdown(re.sub(r'\[\[REF:\d+\]\]', '', msg["content"]))

    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio, format='audio/mp3', autoplay=False)

    if st.session_state.suggested_fragment is not None:
        idx = st.session_state.suggested_fragment
        frag = LIBRO_FRAGMENTOS.get(key, [])[idx]
        st.info(f"📜 Sugerencia: {frag}")
        if st.button("🔊 Leer Fragmento"):
             st.session_state.messages.append({"role": "model", "content": frag})
             st.session_state.suggested_fragment = None 
             with st.spinner("Generando audio..."):
                audio = generar_audio(frag, data["voice_id"])
                if audio: st.session_state.last_audio = audio
             st.rerun()

    def preparar_prompt_inteligente(char_key, base_instruction):
        fragmentos = LIBRO_FRAGMENTOS.get(char_key, [])
        texto_fragmentos = ""
        for i, frag in enumerate(fragmentos):
            texto_fragmentos += f"FRAGMENTO_{i}: {frag}\n"
        return f"{base_instruction}\n{PAUTAS_COMUNES}\n--- MEMORIA LITERARIA ---\n{texto_fragmentos}\nSi usas un fragmento, pon [[REF:número]]."

    prompt_sys = preparar_prompt_inteligente(key, data["base_instruction"])
    try: model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025", system_instruction=prompt_sys)
    except: model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=prompt_sys)

    if prompt := st.chat_input("Escribe tu mensaje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=data["avatar"]):
            box = st.empty()
            full_text = ""
            hist = [{"role": m["role"], "parts": [re.sub(r'\[\[REF:\d+\]\]', '', m["content"])]} for m in st.session_state.messages]
            
            try:
                chat = model.start_chat(history=hist[:-1])
                resp = chat.send_message(prompt, stream=True)
                for chunk in resp:
                    if chunk.text:
                        full_text += chunk.text
                        box.markdown(re.sub(r'\[\[REF:\d+\]\]', '', full_text) + "▌")
                
                final_txt = re.sub(r'\[\[REF:\d+\]\]', '', full_text)
                box.markdown(final_txt)
                st.session_state.messages.append({"role": "model", "content": full_text})
                
                if match := re.search(r'\[\[REF:(\d+)\]\]', full_text):
                    st.session_state.suggested_fragment = int(match.group(1))

                with st.spinner("🔊 Generando voz..."):
                    audio = generar_audio(final_txt, data["voice_id"])
                    if audio:
                        st.session_state.last_audio = audio
                        st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")