# main.py
import streamlit as st
import time

# Importamos módulos propios (Estructura Modular)
from config import CHARACTERS, SINOPSIS, CSS_STYLE, LINK_INSTAGRAM
from utils import init_api_keys, cargar_novela, reproducir_musica_fondo
from audio_engine import generar_voz_gemini
from llm_engine import generar_respuesta_chat, generar_recuerdo_personaje
from game_engine import render_sidebar_ia

# 1. Configuración Global
st.set_page_config(page_title="El Sueño de Leonor", page_icon="🌹", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# 2. Inicialización
client_text, client_audio = init_api_keys()
novel_text = cargar_novela()

# Estado de Sesión
if "page" not in st.session_state: st.session_state.page = "portada"
if "quiz_score" not in st.session_state: st.session_state.quiz_score = 0
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None

# 3. Sidebar
with st.sidebar:
    st.header("Villa Aurora")
    st.checkbox("🔇 Silenciar", key="mute_music")
    reproducir_musica_fondo()
    st.divider()
    render_sidebar_ia(client_text, novel_text)

# 4. Navegación de Páginas

# --- PORTADA ---
if st.session_state.page == "portada":
    st.title("EL SUEÑO DE LEONOR")
    
    # Columnas principales para centrar todo el bloque en la pantalla
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        # 1. Imagen centrada
        st.image("img/villa_aurora.png", use_container_width=True)
        
        # 2. Texto de Sinopsis debajo de la imagen
        st.markdown(f'<div class="info-box">{SINOPSIS}</div>', unsafe_allow_html=True)
        
        # 3. BOTONES ALINEADOS (Izquierda: Audio | Derecha: Entrar)
        # Creamos dos sub-columnas justo debajo del texto
        col_audio, col_entrar = st.columns([1, 1])
        
        with col_audio:
            if st.button("🔊 Escuchar Sinopsis", use_container_width=True):
                audio = generar_voz_gemini(client_audio, SINOPSIS, "susana")
                if audio: st.session_state.last_audio = audio; st.rerun()
        
        with col_entrar:
            if st.button("🗝️ ENTRAR", use_container_width=True):
                st.session_state.page = "seleccion"
                st.rerun()
            
    # Reproductor de audio global para la portada (invisible pero funcional)
    if st.session_state.last_audio: 
        st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

# --- SELECCIÓN (VESTÍBULO) ---
elif st.session_state.page == "seleccion":
    st.title("EL VESTÍBULO")
    
    # Autora (arriba derecha)
    _, col_autora = st.columns([5, 1])
    with col_autora:
        st.image(CHARACTERS['susana']['avatar'], width=90)
        if st.button("Autora"):
            st.session_state.current_char = "susana"
            st.session_state.page = "chat"
            st.session