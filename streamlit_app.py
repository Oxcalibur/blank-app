import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
import tempfile
import time
import re 
import random

# --- 1. CONFIGURACIÓN ---
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
    
    html, body, [class*="css"] { font-family: 'Lora', serif; background-color: #fdfbf7; color: #4b3621 !important; }
    h1 { font-family: 'Cinzel', serif; color: #5e3c38 !important; text-align: center; text-transform: uppercase; text-shadow: 2px 2px 4px #d4c5b0; }
    h3 { color: #8b5e3c !important; text-align: center; font-style: italic; }
    
    .stButton button { background-color: transparent; border: 2px solid #8b5e3c; color: #5e3c38 !important; border-radius: 10px; transition: 0.3s; font-weight: bold; }
    .stButton button:hover { background-color: #5e3c38; color: white !important; transform: scale(1.05); }
    .stChatMessage { background-color: #ffffff; border: 1px solid #e0d0c0; border-radius: 15px; }
    .stChatMessage p { color: #2c1e1a !important; }
    
    #MainMenu, footer, header {visibility: hidden;}
    .stTextInput input { color: #2c1e1a !important; background-color: #ffffff !important; }
    
    /* MODIFICACIÓN: CAJA DE SINOPSIS GÓTICA */
    .sinopsis-box {
        background-color: #fdfbf7;
        color: #4b3621 !important;
        border: 2px solid #d4c5b0; /* Borde un poco más grueso */
        padding: 25px;
        border-radius: 5px;
        
        /* AQUI CAMBIAMOS LA FUENTE A 'CINZEL' (ESTILO GÓTICO/ROMÁNTICO) */
        font-family: 'Cinzel', serif; 
        font-size: 1.1em; /* Un poco más grande para leerse bien */
        font-weight: 500;
        
        line-height: 1.6;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: justify;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05); /* Sombra suave */
    }
    
    .cita-sugerida {
        background-color: #f4eadd;
        border-left: 4px solid #8b5e3c;
        padding: 15px;
        margin-top: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        font-family: 'Lora', serif;
        color: #5e3c38 !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .cita-titulo { font-weight: bold; font-size: 0.9em; text-transform: uppercase; margin-bottom: 5px; }
    .cita-texto { font-style: italic; font-size: 1.05em; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# --- 2. ESTADO ---
if "page" not in st.session_state: st.session_state.page = "portada"
if "current_char" not in st.session_state: st.session_state.current_char = None
if "messages" not in st.session_state: st.session_state.messages = []
if "suggested_fragment" not in st.session_state: st.session_state.suggested_fragment = None

# --- 3. API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Falta API Key en secrets.toml")
    st.stop()

# --- 4. PAUTAS COMUNES ---
PAUTAS_COMUNES = """
DIRECTRICES OBLIGATORIAS DE FORMATO Y ESTILO:
1. BREVEDAD: Tus respuestas deben ser CORTAS y concisas (máximo 2 o 3 oraciones). Estamos en un diálogo fluido.
2. FORMATO DE VOZ: Estás hablando, no escribiendo. NO uses nunca markdown (ni negritas, ni cursivas). NO uses asteriscos para describir acciones (*suspira*). Solo texto plano.
3. IDIOMA: Responde siempre en Español.
"""

# --- 5. TEXTOS Y FRAGMENTOS ---
SINOPSIS_TEXTO = """
Inspirada en la inmortal obra de Charlotte Brontë, “Jane Eyre”. Pasión, misterio y una mujer que desafía el destino. Una historia vibrante con la intensidad de un clásico.
<br><br>
Leonor Polo no es una mujer común. Sobreviviente de una infancia cruel y de un hospicio gris, se convierte en institutriz en la deslumbrante Villa Aurora, mansión perteneciente a una familia adinerada de la Sevilla del siglo XIX. Pronto, el carismático y cultivado patrón, Maximiliano Alcázar, despierta en ella una pasión prohibida.
<br><br>
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

# --- 6. FUNCIONES AUXILIARES ---
def limpiar_para_audio(texto):
    texto = re.sub(r'\[\[REF:\d+\]\]', '', texto)
    # Quitamos tags HTML si los hay
    texto = re.sub(r'<[^>]*>', '', texto) 
    texto = re.sub(r'[\*#_`~]', '', texto)
    texto = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto)
    return texto.strip()

async def generar_audio_edge(texto, voz, velocidad="-10%"):
    clean_text = limpiar_para_audio(texto)
    if not clean_text or len(clean_text) < 2: return None
    communicate = edge_tts.Communicate(clean_text, voz, rate=velocidad)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        await communicate.save(fp.name)
        return fp.name

def preparar_prompt_inteligente(char_key, base_instruction):
    fragmentos = LIBRO_FRAGMENTOS.get(char_key, [])
    texto_fragmentos = ""
    for i, frag in enumerate(fragmentos):
        texto_fragmentos += f"FRAGMENTO_{i}: {frag}\n"
    
    instruccion_final = f"""
    {base_instruction}
    
    {PAUTAS_COMUNES}
    
    --- MEMORIA LITERARIA ---
    Estos son fragmentos literales de tu historia:
    {texto_fragmentos}
    
    INSTRUCCIÓN DE INTELIGENCIA:
    Si tu respuesta toca un tema relacionado con un fragmento, añade al final [[REF:número]].
    """
    return instruccion_final

# --- 7. PERSONAJES ---
CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo", "short_name": "Leonor", "role": "Protagonista", "avatar": "img/leonor.png", 
        "voice": "es-ES-ElviraNeural", "speed": "-5%",
        "greeting": "Bienvenido a Villa Aurora. El calor es sofocante... ¿Traéis noticias?",
        "base_instruction": """
            Eres Leonor Polo, la protagonista. (S.XIX).
            Has sobrevivido a una infancia dura y al hospicio.
            Ahora eres institutriz en 'Villa Aurora' (Sevilla).
            Amas a Maximiliano pero te mantienes cauta.
            **Tono:** Educada, culta, melancólica.
        """
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar", "short_name": "Maximiliano", "role": "Dueño", "avatar": "img/maximiliano.png", 
        "voice": "es-ES-AlvaroNeural", "speed": "-5%",
        "greeting": "¿Quién sois? No recibo visitas sin cita previa.",
        "base_instruction": """
            Eres Maximiliano Alcázar. Dueño de 'Villa Aurora'.
            Hombre de mundo, rico, ciego y manco (herido).
            Ocultas un secreto en el ático y niegas los ruidos.
            **Tono:** Grave, misterioso, arrogante pero noble en el fondo.
        """
    },
    "mercedes": {
        "name": "Doña Mercedes", "short_name": "Doña Mercedes", "role": "Ama de Llaves", "avatar": "img/mercedes.png", 
        "voice": "es-ES-AbrilNeural", "speed": "+0%",
        "greeting": "Límpiese los pies. El Señor no está para nadie.",
        "base_instruction": """
            Eres Doña Mercedes, ama de llaves.
            Religiosa, eficiente y protectora.
            Guardas los secretos del Señor.
            **Tono:** Servicial pero firme.
        """
    },
    "elena": {
        "name": "Elena", "short_name": "Elena", "role": "Espíritu", "avatar": "img/elena.png", 
        "voice": "es-ES-XimenaNeural", "greeting": "La brisa trae recuerdos...", "speed": "-20%",
        "base_instruction": """
            Eres el espíritu de Elena, amiga de la infancia.
            Representas la inocencia y los sueños.
            **Tono:** Dulce, etéreo, onírico.
        """
    },
    "susana": {
        "name": "Susana (Autora)", "short_name": "Susana", "role": "La Autora", "avatar": "img/susana.png", 
        "voice": "es-ES-ElviraNeural", "speed": "+0%",
        "greeting": "Hola, soy Susana, la autora. Pregúntame sobre cómo creé a Leonor.",
        "base_instruction": """
            Eres Susana, autora de 'El Sueño de Leonor'.
            Novela de ficción histórica (S.XIX), empoderamiento y misterio.
            **Tono:** Cercano, apasionado por la literatura.
        """
    }
}

# --- 8. NAVEGACIÓN ---
def ir_a_seleccion(): st.session_state.page = "seleccion"; st.rerun()
def ir_a_chat(p): 
    st.session_state.current_char = p
    st.session_state.page = "chat"
    st.session_state.messages = [{"role": "model", "content": CHARACTERS[p]["greeting"]}]
    st.session_state.suggested_fragment = None 
    st.rerun()
def volver(): st.session_state.page = "portada"; st.rerun()

# --- 9. VISTAS ---
if st.session_state.page == "portada":
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("EL SUEÑO DE LEONOR")
    st.markdown("<h3>Una novela de pasión y misterio en el siglo XIX</h3>", unsafe_allow_html=True)
    
    # 1. IMAGEN CENTRADA (usando 3 columnas)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        try: st.image("img/villa_aurora.png", use_container_width=True)
        except: st.image("https://placehold.co/600x400/png?text=Villa+Aurora", use_container_width=True)
    
    # 2. SINOPSIS DEBAJO (Tipografía Gótica 'Cinzel')
    st.markdown(f'<div class="sinopsis-box">{SINOPSIS_TEXTO}</div>', unsafe_allow_html=True)
    
    # 3. BOTONES DEBAJO DE LA SINOPSIS
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("🔊 Escuchar Sinopsis", use_container_width=True):
            with st.spinner("Leyendo sinopsis..."):
                try:
                    audio_file = asyncio.run(generar_audio_edge(SINOPSIS_TEXTO, "es-ES-ElviraNeural", "+0%"))
                    if audio_file: st.audio(audio_file, format='audio/mp3', autoplay=True)
                except Exception as e: st.error(f"Error: {e}")
    with col_b:
        if st.button("🗝️ ENTRAR EN LA NOVELA", use_container_width=True): ir_a_seleccion()

elif st.session_state.page == "seleccion":
    st.title("EL VESTÍBULO")
    st.markdown("Elige tu interlocutor:")
    keys = list(CHARACTERS.keys())
    cols = st.columns(len(keys))
    
    for i, col in enumerate(cols):
        k = keys[i]
        d = CHARACTERS[k]
        with col:
            try: st.image(d["avatar"], use_container_width=True)
            except: pass
            if st.button(d["short_name"], key=k): ir_a_chat(k)
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Volver a la portada"): volver()

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
        texto_mostrar = re.sub(r'\[\[REF:\d+\]\]', '', msg["content"])
        with st.chat_message(role, avatar=av): st.markdown(texto_mostrar)

    if st.session_state.suggested_fragment is not None:
        idx = st.session_state.suggested_fragment
        fragmentos_pj = LIBRO_FRAGMENTOS.get(key, [])
        if 0 <= idx < len(fragmentos_pj):
            frag_text = fragmentos_pj[idx]
            st.markdown(f"""
            <div class="cita-sugerida">
                <div class="cita-titulo">📜 {data['short_name']} sugiere leer:</div>
                <div class="cita-texto">"{frag_text}"</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔊 Leer fragmento"):
                 st.session_state.messages.append({"role": "model", "content": f"_(Lee el pasaje)_ {frag_text}"})
                 st.session_state.suggested_fragment = None 
                 st.rerun() 

    prompt_completo = preparar_prompt_inteligente(key, data["base_instruction"])
    try: model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025", system_instruction=prompt_completo)
    except: model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=prompt_completo)

    if prompt := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.suggested_fragment = None 
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant", avatar=data["avatar"]):
            box = st.empty()
            full_text = ""
            history_clean = []
            
            for m in st.session_state.messages:
                clean_content = re.sub(r'\[\[REF:\d+\]\]', '', m["content"])
                history_clean.append({"role": m["role"], "parts": [clean_content]})

            try:
                chat = model.start_chat(history=history_clean[:-1])
                response = chat.send_message(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        display_text = re.sub(r'\[\[REF:\d+\]\]', '', full_text)
                        box.markdown(display_text + "▌")
                        time.sleep(0.01)
                
                final_display = re.sub(r'\[\[REF:\d+\]\]', '', full_text)
                box.markdown(final_display)
                st.session_state.messages.append({"role": "model", "content": full_text})
                
                match = re.search(r'\[\[REF:(\d+)\]\]', full_text)
                if match:
                    ref_id = int(match.group(1))
                    st.session_state.suggested_fragment = ref_id
                    st.rerun() 

                with st.spinner("🔊 ..."):
                    try:
                        velocidad = data.get("speed", "-10%")
                        audio_file = asyncio.run(generar_audio_edge(full_text, data["voice"], velocidad))
                        if audio_file: st.audio(audio_file, format='audio/mp3', autoplay=True)
                    except: pass

            except Exception as e:
                st.error(f"Error: {e}")