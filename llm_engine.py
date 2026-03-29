from google.genai import types
from google.genai import errors
import random
import json
import streamlit as st

# --- CONFIGURACIÓN DE MODELOS ---
PRIMARY_MODEL = "gemini-2.5-flash"        # Principal: Optimizado para costes (Estable)
FALLBACK_MODEL = "gemini-3-flash-preview" # fallback: Opción futura o respaldo

def _get_sys_instruction(personaje_data):
    """Helper para no repetir código de instrucciones."""
    from config import SINOPSIS
    return f"""
    {personaje_data['base_instruction']}
    DIRECTRIZ DE LONGITUD: Tus respuestas deben ser breves y conversacionales (máximo 50 palabras) para mantener un diálogo fluido con el lector.
    RESUMEN GENERAL: {SINOPSIS}
    Basate estrictamente en el documento de la novela proporcionado como contexto.
    """

# --- 1. VERSIÓN STREAMING (CON FALLBACK) ---
def generar_respuesta_chat_stream(client, historial, prompt_usuario, personaje_data, cache_name):
    """
    Intenta generar respuesta con el modelo primario (PRIMARY_MODEL). 
    Si falla, cae automáticamente al modelo de respaldo (FALLBACK_MODEL).
    Devuelve un generador seguro.
    """
    
    sys_instruction = _get_sys_instruction(personaje_data)
    
    hist_api = []
    
    # Solución al error de Cache: Inyectar la instrucción del sistema en el historial
    if cache_name:
        hist_api.append(types.Content(role="user", parts=[types.Part.from_text(text=f"[INSTRUCCIONES DE SISTEMA]\n{sys_instruction}\n¿Entendido?")]))
        hist_api.append(types.Content(role="model", parts=[types.Part.from_text(text="Entendido. Asumiré este rol y seguiré las instrucciones estrictamente.")]))
        # Para mantener el orden alterno (User/Model) que exige Gemini si el historial empieza con un saludo ("model")
        if historial and historial[0]["role"] == "model":
            hist_api.append(types.Content(role="user", parts=[types.Part.from_text(text="Perfecto, iniciamos la interacción.")]))
            
    for m in historial:
        hist_api.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]))

    # Función interna que intenta conectar con un modelo específico
    def create_chat_stream(model_name):
        config_kwargs = {}
        if cache_name:
            config_kwargs["cached_content"] = cache_name
        else:
            config_kwargs["system_instruction"] = sys_instruction
            
        chat = client.chats.create(
            model=model_name, 
            config=types.GenerateContentConfig(**config_kwargs), 
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
            
            # Si llegamos aquí sin errores, todo fue bien con el modelo principal
            
        except Exception as e:
            # Si falla, capturamos el error y cambiamos al modelo de respaldo
            print(f"⚠️ Fallo con {PRIMARY_MODEL}: {e}. Cambiando a {FALLBACK_MODEL}...")
            
            try:
                # INTENTO 2: Modelo Fallback
                active_model = FALLBACK_MODEL
                stream_fallback = create_chat_stream(FALLBACK_MODEL)
                for chunk in stream_fallback:
                    if hasattr(chunk, 'text') and chunk.text:
                        yield chunk.text
            except Exception as e2:
                yield f"[Error crítico del sistema: No se pudo conectar con ninguna IA. ({e2})]"

    return stream_wrapper()

# --- 2. VERSIÓN ESTÁTICA (CON FALLBACK) ---
def generar_respuesta_chat(client, historial, prompt_usuario, personaje_data, cache_name):
    sys_instruction = _get_sys_instruction(personaje_data)
    
    hist_api = []
    
    if cache_name:
        hist_api.append(types.Content(role="user", parts=[types.Part.from_text(text=f"[INSTRUCCIONES DE SISTEMA]\n{sys_instruction}\n¿Entendido?")]))
        hist_api.append(types.Content(role="model", parts=[types.Part.from_text(text="Entendido. Asumiré este rol y seguiré las instrucciones estrictamente.")]))
        if historial and historial[0]["role"] == "model":
            hist_api.append(types.Content(role="user", parts=[types.Part.from_text(text="Perfecto, iniciamos la interacción.")]))
            
    for m in historial:
        hist_api.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]))
    
    config_kwargs = {}
    if cache_name:
        config_kwargs["cached_content"] = cache_name
    else:
        config_kwargs["system_instruction"] = sys_instruction
    
    # Lógica de reintento
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            chat = client.chats.create(
                model=model, 
                config=types.GenerateContentConfig(**config_kwargs), 
                history=hist_api
            )
            return chat.send_message(prompt_usuario).text
        except Exception as e:
            print(f"⚠️ Error en {model}: {e}")
            continue # Pasa al siguiente modelo
            
    return "Lo siento, no puedo responder en este momento."

# --- 3. RECUERDOS (CON FALLBACK) ---
def generar_recuerdo_personaje(client, personaje_data, cache_name):
    from config import SINOPSIS
    prompt = f"""
    Actúa estrictamente como {personaje_data['name']}. 
    Analiza tu evolución en el texto de la novela adjunta en tu memoria. 
    Selecciona un momento clave y emocional (invéntalo si es necesario manteniendo la coherencia).
    Nárralo en 1ª persona como si lo revivieras ahora.
    Máximo 100 palabras.
    """
    
    config_kwargs = {}
    if cache_name:
        config_kwargs["cached_content"] = cache_name
        
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(
                model=model, 
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
            )
            return res.text.strip()
        except Exception as e:
            print(f"⚠️ Error recuerdo {model}: {e}")
            continue
            
    return "Intento recordar, pero hay mucha niebla..."

# --- 4. CURIOSIDADES Y TRIVIAL (CON FALLBACK) ---
def generar_pregunta_trivial(client, cache_name):
    from config import SINOPSIS
    tema = random.choice(["detalles de la trama", "escenarios de la novela", "contexto histórico"])
    prompt = f"Genera pregunta test difícil sobre {tema} basada en la novela de tu memoria. JSON Output: {{'pregunta':'','opciones':['','',''],'correcta':''}}"
    
    config_kwargs = {"response_mime_type": "application/json"}
    if cache_name:
        config_kwargs["cached_content"] = cache_name
        
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(
                model=model, 
                contents=prompt, 
                config=types.GenerateContentConfig(**config_kwargs)
            )
            return json.loads(res.text)
        except:
            continue
            
    return {"pregunta": "¿En qué ciudad transcurre la trama?", "opciones": ["Madrid", "Sevilla", "Londres"], "correcta": "Sevilla"}

def generar_curiosidad(client):
    temas = ["moda victoriana", "medicina del siglo XIX", "etiqueta social", "inventos de la revolución industrial", "supersticiones", "literatura romántica", "vida en Londres vs Sevilla", "el lenguaje de los abanicos", "duelos de honor","contexto historico"]
    tema = random.choice(temas)
    prompt = f"Dato real curioso y poco conocido sobre {tema} durante el periodo del romanticismo español o ingles. Máximo 25 palabras. Varía la respuesta cada vez."
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(model=model, contents=prompt)
            return res.text
        except:
            continue
    return "El duelo por honor seguía siendo una práctica clandestina en 1870."