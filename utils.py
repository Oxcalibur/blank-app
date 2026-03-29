# utils.py
import streamlit as st
import os
import datetime
import zoneinfo
import pypdf
import base64
from google.oauth2 import service_account
from google import genai
from google.genai import types
from google.cloud import texttospeech
from config import HORA_PICO_INICIO, HORA_PICO_FIN

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

# --- GESTIÓN DE CACHÉ HÍBRIDA POR HORARIOS ---
def es_hora_pico():
    """Devuelve True si la hora actual de Madrid está entre HORA_PICO_INICIO y HORA_PICO_FIN."""
    try:
        tz = zoneinfo.ZoneInfo("Europe/Madrid")
        ahora = datetime.datetime.now(tz)
        return HORA_PICO_INICIO <= ahora.hour < HORA_PICO_FIN
    except Exception as e:
        print(f"Error al evaluar hora pico: {e}")
        return False # Ante la duda o error, caemos en el modo valle (más barato)

def obtener_o_crear_cache(client_text, path="img/leonor.pdf"):
    """Crea o recupera la caché del documento solo si es hora pico."""
    if not es_hora_pico():
        return None

    if "cache_name" in st.session_state and st.session_state.cache_name:
        return st.session_state.cache_name

    try:
        if not os.path.exists(path):
            st.warning(f"No se encontró el archivo: {path}")
            return None
            
        with st.spinner("Inicializando memoria fotográfica en Horas Pico..."):
            file_ref = client_text.files.upload(file=path)
            cache = client_text.caches.create(
            model="gemini-2.5-flash",
            config=types.CreateCachedContentConfig(
                contents=[file_ref],
                    ttl="3600s" # 60 minutos de vida
            )
        )
            st.session_state.cache_name = cache.name
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