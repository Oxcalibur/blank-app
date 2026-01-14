from google.genai import types
from google.genai import errors
import random
import json
import streamlit as st
from config import SINOPSIS

# --- CONFIGURACIÓN DE MODELOS ---
PRIMARY_MODEL = "gemini-3-flash-preview"  # Intentamos usar este primero (Lo último)
FALLBACK_MODEL = "gemini-2.5-flash"       # Si falla, usamos este (El estable)

def _get_sys_instruction(personaje_data, contexto_libro):
    """Helper para no repetir código de instrucciones."""
    return f"""
    {personaje_data['base_instruction']}
    DIRECTRIZ DE LONGITUD: Tus respuestas deben ser breves y conversacionales (máximo 50 palabras) para mantener un diálogo fluido con el lector.
    RESUMEN GENERAL: {SINOPSIS}
    CONTENIDO ÍNTEGRO DE LA NOVELA:
    {contexto_libro}
    """

# --- 1. VERSIÓN STREAMING (CON FALLBACK) ---
def generar_respuesta_chat_stream(client, historial, prompt_usuario, personaje_data, contexto_libro):
    """
    Intenta generar respuesta con Gemini 3.0. 
    Si falla, cae automáticamente a Gemini 2.5.
    Devuelve un generador seguro.
    """
    
    sys_instruction = _get_sys_instruction(personaje_data, contexto_libro)
    
    hist_api = [
        types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]) 
        for m in historial
    ]

    # Función interna que intenta conectar con un modelo específico
    def create_chat_stream(model_name):
        chat = client.chats.create(
            model=model_name, 
            config=types.GenerateContentConfig(system_instruction=sys_instruction), 
            history=hist_api
        )
        return chat.send_message_stream(prompt_usuario)

    # El generador principal que gestiona el error
    def stream_wrapper():
        active_model = PRIMARY_MODEL
        stream = None
        
        try:
            # INTENTO 1: Modelo Principal
            stream = create_chat_stream(PRIMARY_MODEL)
            # Intentamos leer el primer chunk para ver si explota
            first_chunk_read = False
            for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    first_chunk_read = True
                    yield chunk.text
            
            # Si llegamos aquí sin errores, todo fue bien con Gemini 3.0
            
        except Exception as e:
            # Si falla, capturamos el error y cambiamos al modelo seguro
            print(f"⚠️ Fallo con {PRIMARY_MODEL}: {e}. Cambiando a {FALLBACK_MODEL}...")
            
            try:
                # INTENTO 2: Modelo Fallback (Gemini 2.5)
                active_model = FALLBACK_MODEL
                stream_fallback = create_chat_stream(FALLBACK_MODEL)
                for chunk in stream_fallback:
                    if hasattr(chunk, 'text') and chunk.text:
                        yield chunk.text
            except Exception as e2:
                yield f"[Error crítico del sistema: No se pudo conectar con ninguna IA. ({e2})]"

    return stream_wrapper()

# --- 2. VERSIÓN ESTÁTICA (CON FALLBACK) ---
def generar_respuesta_chat(client, historial, prompt_usuario, personaje_data, contexto_libro):
    sys_instruction = _get_sys_instruction(personaje_data, contexto_libro)
    
    hist_api = [
        types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]) 
        for m in historial
    ]
    
    # Lógica de reintento
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            chat = client.chats.create(
                model=model, 
                config=types.GenerateContentConfig(system_instruction=sys_instruction), 
                history=hist_api
            )
            return chat.send_message(prompt_usuario).text
        except Exception as e:
            print(f"⚠️ Error en {model}: {e}")
            continue # Pasa al siguiente modelo
            
    return "Lo siento, no puedo responder en este momento."

# --- 3. RECUERDOS (CON FALLBACK) ---
def generar_recuerdo_personaje(client, personaje_data, contexto_libro):
    prompt = f"""
    Actúa estrictamente como {personaje_data['name']}. 
    Analiza tu evolución en el siguiente texto completo: 
    {contexto_libro}
    Selecciona un momento clave y emocional.
    Nárralo en 1ª persona como si lo revivieras ahora.
    Máximo 100 palabras.
    """
    
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(model=model, contents=prompt)
            return res.text.strip()
        except Exception as e:
            print(f"⚠️ Error recuerdo {model}: {e}")
            continue
            
    return "Intento recordar, pero hay mucha niebla..."

# --- 4. CURIOSIDADES Y TRIVIAL (CON FALLBACK) ---
def generar_pregunta_trivial(client, contexto_libro):
    tema = random.choice(["detalles de la trama", "escenarios de la novela", "contexto histórico"])
    prompt = f"Genera pregunta test difícil sobre {tema} basada en: {contexto_libro}. JSON Output: {{'pregunta':'','opciones':['','',''],'correcta':''}}"
    
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(
                model=model, 
                contents=prompt, 
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(res.text)
        except:
            continue
            
    return {"pregunta": "¿En qué ciudad transcurre la trama?", "opciones": ["Madrid", "Sevilla", "Londres"], "correcta": "Sevilla"}

def generar_curiosidad(client):
    prompt = "Dato real sorprendente de 1870 o Romanticismo. Máximo 25 palabras."
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(model=model, contents=prompt)
            return res.text
        except:
            continue
    return "El duelo por honor seguía siendo una práctica clandestina en 1870."