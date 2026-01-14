import streamlit as st
import time

# Importamos módulos propios
from config import CHARACTERS, SINOPSIS, CSS_STYLE, LINK_INSTAGRAM
from utils import init_api_keys, cargar_novela, reproducir_musica_fondo
from audio_engine import generar_voz_gemini, generar_audio_saludo_cached
from llm_engine import generar_respuesta_chat_stream, generar_recuerdo_personaje
from game_engine import render_sidebar_ia

# CONFIGURACIÓN RESPONSIVE: 'auto' cierra la barra en móvil y la abre en PC
st.set_page_config(page_title="El Sueño de Leonor", page_icon="🌹", layout="wide", initial_sidebar_state="auto")
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
    reproducir_musica_fondo()
    st.divider()
    # Barra lateral optimizada con Fragmentos
    render_sidebar_ia(client_text, novel_text)

# --- PORTADA ---
if st.session_state.page == "portada":
    st.markdown("<h1 style='text-align: center; font-size: 3em; margin-bottom: 0.2em;'>EL SUEÑO DE LEONOR</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        st.image("img/villa_aurora.png", use_container_width=True)
        
        st.markdown(f"""
        <div class="info-box" style="margin-top: 20px;">
            <h3 style="text-align: center; margin-top: 0;">Sinopsis</h3>
            {SINOPSIS}
        </div>
        """, unsafe_allow_html=True)
        
        col_audio, col_entrar = st.columns(2, gap="medium")
        with col_audio:
            if st.button("🔊 Escuchar Prólogo", use_container_width=True):
                audio = generar_audio_saludo_cached(client_audio, SINOPSIS, "susana")
                if audio: st.session_state.last_audio = audio; st.rerun()
        with col_entrar:
            if st.button("🗝️ ENTRAR EN LA VILLA", use_container_width=True):
                st.session_state.last_audio = None 
                st.session_state.page = "seleccion"
                st.rerun()
        
        st.markdown("---")
        st.info("👈 **Tip:** Abre el menú lateral (arriba izq.) para descubrir secretos y jugar.")
            
    if st.session_state.last_audio: 
        st.audio(st.session_state.last_audio, format="audio/wav", autoplay=True)

# --- SELECCIÓN ---
elif st.session_state.page == "seleccion":
    st.markdown("<h2>EL VESTÍBULO</h2>", unsafe_allow_html=True)
    
    _, col_autora = st.columns([6, 1])
    with col_autora:
        if 'susana' in CHARACTERS:
            try: st.image(CHARACTERS['susana']['avatar'], width=80)
            except: pass
            if st.button("Autora", key="btn_susana"):
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
                try: st.image(CHARACTERS[key]['avatar'], use_container_width=True)
                except: pass
                if st.button(CHARACTERS[key]['short_name'], key=f"btn_{key}"):
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