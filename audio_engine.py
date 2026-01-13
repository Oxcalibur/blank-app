# audio_engine.py
import io
import wave
import re
from google.cloud import texttospeech
from config import CHARACTERS

def generar_voz_gemini(client, texto, personaje_key):
    """Genera audio WAV compatible con Streamlit."""
    if not client or not texto: return None
    
    datos = CHARACTERS.get(personaje_key)
    if not datos: return None

    # Limpieza de texto (quitar acotaciones o asteriscos)
    clean_text = re.sub(r'\[.*?\]', '', texto).strip().replace("*", "")
    
    config = texttospeech.StreamingSynthesizeConfig(
        voice=texttospeech.VoiceSelectionParams(
            language_code="es-ES", 
            name=datos['voice_name'], 
            model_name="gemini-2.5-flash-tts"
        )
    )

    def request_generator():
        yield texttospeech.StreamingSynthesizeRequest(streaming_config=config)
        yield texttospeech.StreamingSynthesizeRequest(
            input=texttospeech.StreamingSynthesisInput(
                text=clean_text, 
                prompt=datos['voice_style']
            )
        )

    try:
        responses = client.streaming_synthesize(request_generator())
        audio_data = bytearray()
        for r in responses: audio_data.extend(r.audio_content)
        
        # Empaquetado WAV en memoria
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(24000)
            f.writeframes(audio_data)
        return buf.getvalue()
    except Exception as e:
        print(f"Error TTS: {e}")
        return None