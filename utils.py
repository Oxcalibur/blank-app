# utils.py
import streamlit as st
import os
import pypdf
import base64
from google.oauth2 import service_account
from google import genai
from google.genai import types
from google.cloud import texttospeech

# --- OPTIMIZACIÓN: Usar cache de recursos para los clientes de API ---
# Esto asegura que los clientes se creen UNA SOLA VEZ por aplicación, no por sesión/rerun.
@st.cache_resource(show_spinner=False)
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

# --- OPTIMIZACIÓN: Context Caching de Gemini ---
# Esto asegura que el PDF se suba a Google y se cree un caché solo una vez.
@st.cache_resource(show_spinner=False)
def inicializar_cache_novela(_client, path="img/leonor.pdf"):
    """Sube el PDF a Google y crea un caché de contexto para ahorrar tokens."""
    try:
        if not os.path.exists(path):
            st.warning(f"No se encontró el archivo: {path}")
            return None
            
        file_ref = _client.files.upload(file=path)
        cache = _client.caches.create(
            model="gemini-2.5-flash",
            config=types.CreateCachedContentConfig(
                contents=[file_ref],
                ttl="3600s" # 60 minutos de vida (se renueva con el uso)
            )
        )
        return cache.name
    except Exception as e:
        st.warning(f"No se pudo inicializar la caché de contexto: {e}")
        return None

# --- OPTIMIZACIÓN: Usar cache de datos para imágenes ---
# Evita leer y codificar la misma imagen en cada rerun.
@st.cache_data(show_spinner=False)
def get_img_as_base64(path):
    """Convierte una imagen local a string Base64 para incrustar en HTML."""
    if not os.path.exists(path): return ""
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- OPTIMIZACIÓN: Cachear el archivo de música ---
@st.cache_data(show_spinner=False)
def _get_music_b64(path="img/Entre mis recuerdos.mp3"):
    """Lee y codifica el archivo de música una sola vez."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def reproducir_musica_fondo(path="img/Entre mis recuerdos.mp3"):
    """Reproduce música si no está silenciada."""
    if st.session_state.get("mute_music", False): return

    b64 = _get_music_b64(path)
    if not b64:
        return

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

# Las funciones `reproducir_saludo` y `reproducir_saludo_personalizado` se han eliminado
# porque no se utilizaban en `streamlit_app.py` y su lógica de reproducción de audio
# ya se gestiona de forma más centralizada y eficiente en el script principal.