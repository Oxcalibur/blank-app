# audio_engine.py
import io
import wave
import re
import streamlit as st
from google.cloud import texttospeech
from config import CHARACTERS

# Función interna de generación (sin caché)
def _sintetizar_audio(client, texto, voice_name, voice_style):
    if not client or not texto: return None
    
    clean_text = re.sub(r'\[.*?\]', '', texto).strip().replace("*", "")
    
    config = texttospeech.StreamingSynthesizeConfig(
        voice=texttospeech.VoiceSelectionParams(
            language_code="es-ES", 
            name=voice_name, 
            model_name="gemini-2.5-flash-tts"
        )
    )

    def request_generator():
        yield texttospeech.StreamingSynthesizeRequest(streaming_config=config)
        yield texttospeech.StreamingSynthesizeRequest(
            input=texttospeech.StreamingSynthesisInput(
                text=clean_text, 
                prompt=voice_style
            )
        )

    try:
        responses = client.streaming_synthesize(request_generator())
        audio_data = bytearray()
        for r in responses: audio_data.extend(r.audio_content)
        
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(24000); f.writeframes(audio_data)
        return buf.getvalue()
    except Exception as e:
        print(f"Error TTS: {e}")
        return None

# --- OPTIMIZACIÓN 1: Caché para saludos repetitivos ---
# El 'ttl' (Time To Live) de 3600 segundos hace que se refresque cada hora por si acaso.
@st.cache_data(show_spinner=False, ttl=3600)
def generar_audio_saludo_cached(_client, texto, personaje_key):
    """Genera audio y lo guarda en memoria para uso instantáneo futuro."""
    # Nota: _client lleva guion bajo para que Streamlit no intente 'hashearlo'.
    datos = CHARACTERS.get(personaje_key)
    if not datos: return None
    return _sintetizar_audio(_client, texto, datos['voice_name'], datos['voice_style'])

# Función para chat dinámico (siempre nuevo, sin caché)
def generar_voz_gemini(client, texto, personaje_key):
    datos = CHARACTERS.get(personaje_key)
    if not datos: return None
    return _sintetizar_audio(client, texto, datos['voice_name'], datos['voice_style'])