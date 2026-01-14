# utils.py
import streamlit as st
import os
import pypdf
import base64
from google.oauth2 import service_account
from google import genai
from google.cloud import texttospeech

def init_api_keys():
    """Inicializa clientes de API de forma segura."""
    try:
        # Cliente Texto (Gemini)
        client_text = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # Cliente Audio (Vertex)
        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
        client_audio = texttospeech.TextToSpeechClient(credentials=creds)
        
        return client_text, client_audio
    except Exception as e:
        st.error(f"Error de Autenticación: {e}")
        st.stop()

def cargar_novela(path="img/leonor.pdf"):
    """Carga y limpia el texto del PDF."""
    if "novel_text" in st.session_state and st.session_state.novel_text:
        return st.session_state.novel_text
    
    try:
        if os.path.exists(path):
            reader = pypdf.PdfReader(path)
            import re
            full_text = "".join([p.extract_text() for p in reader.pages])
            cleaned = re.sub(r'\s+', ' ', full_text).strip()
            st.session_state.novel_text = cleaned
            return cleaned
    except: 
        return "Texto no disponible."
    return ""

def get_img_as_base64(path):
    """Convierte una imagen local a string Base64 para incrustar en HTML."""
    if not os.path.exists(path): return ""
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def reproducir_musica_fondo(path="img/Entre mis recuerdos.mp3"):
    """Reproduce música si no está silenciada."""
    if st.session_state.get("mute_music", False): return
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            md = f"""
                <audio autoplay loop id="bg_audio" allow="autoplay">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById("bg_audio");
                    if (audio) {{ audio.volume = 0.2; audio.play().catch(e => console.log("Autoplay bloqueado por navegador")); }}
                </script>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass