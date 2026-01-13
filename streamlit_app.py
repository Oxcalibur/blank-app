## main.py
import streamlit as st
import time

# Importamos módulos propios
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
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        col_img, col_btn = st.columns([3, 1])
        with col_img:
            st.image("img/villa_aurora.png", use_container_width=True)
        with col_btn:
            st.write(""); st.write(""); st.write("")
            if st.button("🗝️ ENTRAR", use_container_width=True):
                st.session_state.page = "seleccion"
                st.rerun()

        st.markdown(f'<div class="info-box">{SINOPSIS}</div>', unsafe_allow_html=True)
        
        # Botones inferiores (Audio Izq | Nada Der - Entrar ya está arriba)
        # Opcional: Si quieres mantener el botón de entrar también abajo, descomenta la parte derecha
        c_aud, c_ent = st.columns([1, 1])
        with c_aud:
            if st.button("🔊 Escuchar Sinopsis", use_container_width=True):
                audio = generar_voz_gemini(client_audio, SINOPSIS, "susana")
                if audio: st.session_state.last_audio = audio; st.rerun()
            
    if st.session_state.last_audio: 
        st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

# --- SELECCIÓN ---
elif st.session_state.page == "seleccion":
    st.title("EL VESTÍBULO")
    
    # Autora
    _, col_autora = st.columns([5, 1])
    with col_autora:
        # Verificamos que 'susana' exista para evitar crash
        if 'susana' in CHARACTERS:
            try:
                st.image(CHARACTERS['susana']['avatar'], width=90)
            except:
                st.write("📷") # Fallback si falla la imagen
            if st.button("Autora"):
                st.session_state.current_char = "susana"
                st.session_state.page = "chat"
                st.session_state.messages = [{"role":"model", "content":CHARACTERS['susana']['greeting']}]
                st.rerun()
            
    st.divider()
    
    # Protagonistas
    pjs = ["leonor", "maximiliano", "mercedes", "elena"]
    cols = st.columns(len(pjs))
    
    for i, key in enumerate(pjs):
        with cols[i]:
            # Protección contra claves inexistentes
            if key in CHARACTERS:
                try:
                    st.image(CHARACTERS[key]['avatar'], use_container_width=True)
                except:
                    st.error(f"Falta img/{key}.png") # Aviso visual si falla la carga
                
                if st.button(CHARACTERS[key]['short_name']):
                    st.session_state.current_char = key
                    st.session_state.page = "chat"
                    st.session_state.messages = [{"role":"model", "content":CHARACTERS[key]['greeting']}]
                    st.rerun()
            else:
                st.error(f"Error: {key}")

# --- CHAT ---
elif st.session_state.page == "chat":
    key = st.session_state.current_char
    # Verificamos que el personaje seleccionado sigue existiendo
    if key not in CHARACTERS:
        st.error("Error de personaje. Volviendo al inicio.")
        st.session_state.page = "seleccion"
        st.rerun()
        
    data = CHARACTERS[key]
    
    if st.button("⬅️ Atrás"): st.session_state.page = "seleccion"; st.rerun()
    st.subheader(f"Conversando con {data['name']}")
    
    if key != "susana":
        if st.button(f"📜 {data['short_name']}, recuerda un fragmento..."):
            with st.spinner("Recordando..."):
                texto_recuerdo = generar_recuerdo_personaje(client_text, data, novel_text)
                msg_recuerdo = f"*(Cierra los ojos un instante)* {texto_recuerdo}"
                st.session_state.messages.append({"role": "model", "content": msg_recuerdo})
                audio = generar_voz_gemini(client_audio, texto_recuerdo, key)
                if audio: st.session_state.last_audio = audio
                st.rerun()

    for m in st.session_state.messages:
        with st.chat_message("assistant" if m["role"]=="model" else "user"):
            st.markdown(m["content"])
            if "[INSTAGRAM]" in m["content"]: st.link_button("📸 Instagram de Susana", LINK_INSTAGRAM)
            
    if st.session_state.last_audio: 
        st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

    if prompt := st.chat_input("Dile algo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        resp_texto = generar_respuesta_chat(client_text, st.session_state.messages[:-1], prompt, data, novel_text)
        st.session_state.messages.append({"role": "model", "content": resp_texto})
        
        audio_resp = generar_voz_gemini(client_audio, resp_texto, key)
        if audio_resp: st.session_state.last_audio = audio_resp
        st.rerun()