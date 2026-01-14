import streamlit as st
import time

# Importamos módulos propios
from config import CHARACTERS, SINOPSIS, CSS_STYLE, LINK_INSTAGRAM
from utils import init_api_keys, cargar_novela, reproducir_musica_fondo, get_img_as_base64
from audio_engine import generar_voz_gemini, generar_audio_saludo_cached
from llm_engine import generar_respuesta_chat_stream, generar_recuerdo_personaje
from game_engine import render_sidebar_ia

# CONFIGURACIÓN RESPONSIVE: 'auto' cierra la barra en móvil y la abre en PC
st.set_page_config(page_title="El Sueño de Leonor", page_icon="🌹", layout="wide", initial_sidebar_state="collapsed")
st.markdown(CSS_STYLE, unsafe_allow_html=True)

client_text, client_audio = init_api_keys()
novel_text = cargar_novela()

if "page" not in st.session_state: st.session_state.page = "portada"
if "quiz_score" not in st.session_state: st.session_state.quiz_score = 0
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Villa Aurora</h2>", unsafe_allow_html=True)
    st.checkbox("🔇 Silenciar Música", key="mute_music")
    st.divider()
    # Barra lateral optimizada con Fragmentos
    render_sidebar_ia(client_text, novel_text)

# Música de fondo (fuera del sidebar para asegurar autoplay al inicio)
reproducir_musica_fondo()

# --- PORTADA ---
if st.session_state.page == "portada":
    st.markdown("<h1 style='text-align: center; font-size: 3em; margin-bottom: 0.2em;'>EL SUEÑO DE LEONOR</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        st.image("img/villa_aurora.png", width="stretch")
        
        st.markdown(f"""
        <div class="info-box" style="margin-top: 20px;">
            <h3 style="text-align: center; margin-top: 0;">Sinopsis</h3>
            {SINOPSIS}
        </div>
        """, unsafe_allow_html=True)
        
        col_audio, col_entrar = st.columns(2, gap="medium")
        with col_audio:
            if st.button("🔊 Escuchar Prólogo", width="stretch"):
                audio = generar_audio_saludo_cached(client_audio, SINOPSIS, "susana")
                if audio: st.session_state.last_audio = audio; st.rerun()
        with col_entrar:
            if st.button("🗝️ ENTRAR EN LA VILLA", width="stretch"):
                st.session_state.last_audio = None 
                st.session_state.page = "seleccion"
                st.rerun()
        
        st.markdown("---")
        st.info("👈 **Tip:** Pulsa la flecha (>) arriba a la izquierda para abrir el **Salón de Juegos**.")
            
    if st.session_state.last_audio: 
        st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

# --- SELECCIÓN ---
elif st.session_state.page == "seleccion":
    # --- CSS HACK: BOTONES INVISIBLES ---
    # Hacemos que los botones de tipo "primary" dentro de columnas sean invisibles 
    # y cubran todo el área (overlay), permitiendo hacer clic en la tarjeta.
    # USAMOS :has() PARA QUE SOLO AFECTE A LAS TARJETAS, NO A SUSANA
    st.markdown("""
    <style>
    /* HACK: Botón invisible superpuesto usando márgenes negativos */
    /* Esto es más robusto que position:absolute porque "tira" del botón hacia arriba */
    
    /* CASO 1: Tarjetas NORMALES */
    div[data-testid="stColumn"]:has(.contenedor-personaje:not(.mini)) .stButton {
        margin-top: -300px !important; /* Subimos el botón para que cubra la tarjeta */
        position: relative !important;
        z-index: 100 !important;
        width: 100% !important;
    }
    
    div[data-testid="stColumn"]:has(.contenedor-personaje:not(.mini)) .stButton button {
        height: 300px !important; /* Altura de la tarjeta */
        width: 100% !important;
        opacity: 0 !important; /* Invisible */
        color: transparent !important;
        cursor: pointer;
    }

    /* CASO 2: Tarjetas MINI (Susana) */
    div[data-testid="stColumn"]:has(.contenedor-personaje.mini) .stButton {
        margin-top: -160px !important;
        position: relative !important;
        z-index: 100 !important;
        width: 100% !important;
    }
    div[data-testid="stColumn"]:has(.contenedor-personaje.mini) .stButton button {
        height: 160px !important;
        width: 100% !important;
        opacity: 0 !important;
        color: transparent !important;
        cursor: pointer;
    }

    /* ESTILOS VISUALES MINI TARJETA */
    .contenedor-personaje.mini .tarjeta { width: 120px !important; height: 160px !important; }
    .contenedor-personaje.mini .marco-imagen { width: 80px !important; height: 80px !important; margin-bottom: 5px !important; }
    .contenedor-personaje.mini .nombre-personaje { font-size: 12px !important; margin-top: 2px !important; }
    .contenedor-personaje.mini .cara-trasera { padding: 5px !important; }
    .contenedor-personaje.mini .titulo-trasero { font-size: 10px !important; margin-bottom: 2px !important; padding-bottom: 2px !important; }
    .contenedor-personaje.mini .texto-descripcion { font-size: 9px !important; line-height: 1.1 !important; }
    </style>
    """, unsafe_allow_html=True)

    def render_tarjeta_personaje(key, mini=False):
        """Genera el HTML de la tarjeta y el botón invisible."""
        data = CHARACTERS[key]
        img_b64 = get_img_as_base64(data['avatar'])
        
        mini_class = " mini" if mini else ""
        
        html = f"""
        <div class="contenedor-personaje{mini_class}">
            <div class="tarjeta">
                <div class="cara-frontal">
                    <div class="marco-imagen"><img src="data:image/png;base64,{img_b64}"></div>
                    <div class="nombre-personaje">{data['short_name'].upper()}</div>
                </div>
                <div class="cara-trasera">
                    <div class="titulo-trasero">{data.get('role', 'Personaje')}</div>
                    <div class="texto-descripcion">"{data.get('description', '')}"</div>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        # Botón invisible (type="primary" para que lo capture el CSS)
        return st.button("Seleccionar", key=f"btn_{key}", type="primary", width="stretch")
    
    # --- LAYOUT CABECERA (Título + Susana) ---
    # Ponemos a Susana arriba a la derecha, pequeña, para no empujar el contenido
    c_title, c_susana = st.columns([5, 1], gap="small")
    
    with c_title:
        st.markdown("<h2 style='text-align: center; margin-top: 20px;'>EL VESTÍBULO</h2>", unsafe_allow_html=True)
        
    with c_susana:
        if 'susana' in CHARACTERS:
            # Usamos tarjeta mini para mantener el estilo
            if render_tarjeta_personaje('susana', mini=True):
                st.session_state.last_audio = None
                st.session_state.current_char = "susana"
                st.session_state.page = "chat"
                st.session_state.messages = [{"role":"model", "content":CHARACTERS['susana']['greeting']}]
                audio_saludo = generar_audio_saludo_cached(client_audio, CHARACTERS['susana']['greeting'], "susana")
                st.session_state.last_audio = audio_saludo
                st.rerun()

    st.divider()
    pjs = ["leonor", "maximiliano", "mercedes", "elena"]
    cols = st.columns(len(pjs))
    for i, key in enumerate(pjs):
        with cols[i]:
            if key in CHARACTERS:
                if render_tarjeta_personaje(key):
                    st.session_state.last_audio = None
                    st.session_state.current_char = key
                    st.session_state.page = "chat"
                    st.session_state.messages = [{"role":"model", "content":CHARACTERS[key]['greeting']}]
                    audio_saludo = generar_audio_saludo_cached(client_audio, CHARACTERS[key]['greeting'], key)
                    st.session_state.last_audio = audio_saludo
                    st.rerun()

# --- CHAT ---
elif st.session_state.page == "chat":
    
    key = st.session_state.current_char
    if not key or key not in CHARACTERS: st.session_state.page = "seleccion"; st.rerun()
    data = CHARACTERS[key]

# --- FONDO INMERSIVO COMÚN (VESTÍBULO Y CHAT) ---
# Se aplica si estamos en selección o chat
if st.session_state.page in ["seleccion", "chat"]:
    vestibulo_b64 = get_img_as_base64("img/vestibulo.png")
    if vestibulo_b64:
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{vestibulo_b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.9));
            z-index: -1;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    if st.session_state.page == "chat":
        if st.button("⬅️ Volver al Vestíbulo"): 
            st.session_state.last_audio = None
            st.session_state.page = "seleccion"
            st.rerun()

        st.markdown(f"<h3>Conversando con {data['name']}</h3>", unsafe_allow_html=True)
        
        if key != "susana":
            if st.button(f"📜 {data['short_name']}, comparte un recuerdo..."):
                with st.spinner("Recordando..."):
                    texto_recuerdo = generar_recuerdo_personaje(client_text, data, novel_text)
                    msg_recuerdo = f"*(Cierra los ojos un instante)* {texto_recuerdo}"
                    st.session_state.messages.append({"role": "model", "content": msg_recuerdo})
                    with st.spinner("🔊 Generando voz..."):
                        audio = generar_voz_gemini(client_audio, texto_recuerdo, key)
                        st.session_state.last_audio = audio
                    st.rerun()

        for m in st.session_state.messages:
            with st.chat_message("assistant" if m["role"]=="model" else "user"):
                st.markdown(m["content"])
                if "[INSTAGRAM]" in m["content"]: st.link_button("📸 Instagram de Susana", LINK_INSTAGRAM)
                
        if st.session_state.last_audio: 
            st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

        if prompt := st.chat_input("Escribe tu mensaje..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            texto_final = ""
            with st.chat_message("assistant"):
                stream = generar_respuesta_chat_stream(client_text, st.session_state.messages[:-1], prompt, data, novel_text)
                texto_final = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "model", "content": texto_final})
            
            if texto_final:
                with st.spinner(f"🗣️ {data['short_name']} está hablando..."):
                    audio_resp = generar_voz_gemini(client_audio, texto_final, key)
                    st.session_state.last_audio = audio_resp
            
            st.rerun()