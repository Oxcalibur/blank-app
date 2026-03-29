from google.genai import types
from google.genai import errors
import random
import json
import streamlit as st
import config
from utils import es_hora_pico, obtener_o_crear_cache

# --- CONFIGURACIÓN DE MODELOS ---
PRIMARY_MODEL = "gemini-2.5-flash"        # Principal: Optimizado para costes (Estable)
FALLBACK_MODEL = "gemini-3-flash-preview" # fallback: Opción futura o respaldo

# --- 1. VERSIÓN STREAMING (CON FALLBACK) ---
def generar_respuesta_chat_stream(client, historial, prompt_usuario, personaje_data):
    """
    Intenta generar respuesta con el modelo primario (PRIMARY_MODEL). 
    Si falla, cae automáticamente al modelo de respaldo (FALLBACK_MODEL).
    Devuelve un generador seguro.
    """
    
    hist_api = []
    
    for m in historial:
        hist_api.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]))

    config_kwargs = {}
    
    if es_hora_pico():
        cache_name = obtener_o_crear_cache(client)
        if cache_name:
            config_kwargs["cached_content"] = cache_name
            
        # Inyección directa de instrucciones en el prompt de usuario para evitar el error 400
        instrucciones = f"[INSTRUCCIONES DE SISTEMA: Actúa como {personaje_data['name']}. {personaje_data['base_instruction']}]. DIRECTRIZ: Respuestas breves (máximo 50 palabras)."
        prompt_final = f"{instrucciones}\n\nMensaje del usuario: {prompt_usuario}"
    else:
        sys_instruction = f"Actúa como {personaje_data['name']}. {personaje_data['base_instruction']}\nDIRECTRIZ DE LONGITUD: Tus respuestas deben ser breves y conversacionales (máximo 50 palabras).\nRESUMEN DE LA NOVELA: {config.RESUMEN_NOVELA}"
        config_kwargs["system_instruction"] = sys_instruction
        prompt_final = prompt_usuario

    # Función interna que intenta conectar con un modelo específico
    def create_chat_stream(model_name):
        chat = client.chats.create(
            model=model_name, 
            config=types.GenerateContentConfig(**config_kwargs), 
            history=hist_api
        )
        return chat.send_message_stream(prompt_final)

    # El generador principal que gestiona el error
    def stream_wrapper():
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
                stream_fallback = create_chat_stream(FALLBACK_MODEL)
                for chunk in stream_fallback:
                    if hasattr(chunk, 'text') and chunk.text:
                        yield chunk.text
            except Exception as e2:
                yield f"[Error crítico del sistema: No se pudo conectar con ninguna IA. ({e2})]"

    return stream_wrapper()

# --- 2. VERSIÓN ESTÁTICA (CON FALLBACK) ---
def generar_respuesta_chat(client, historial, prompt_usuario, personaje_data):
    hist_api = []
    
    for m in historial:
        hist_api.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]))
    
    config_kwargs = {}
    if es_hora_pico():
        cache_name = obtener_o_crear_cache(client)
        if cache_name:
            config_kwargs["cached_content"] = cache_name
        instrucciones = f"[INSTRUCCIONES DE SISTEMA: Actúa como {personaje_data['name']}. {personaje_data['base_instruction']}]. DIRECTRIZ: Respuestas breves (máximo 50 palabras)."
        prompt_final = f"{instrucciones}\n\nMensaje del usuario: {prompt_usuario}"
    else:
        sys_instruction = f"Actúa como {personaje_data['name']}. {personaje_data['base_instruction']}\nDIRECTRIZ DE LONGITUD: Tus respuestas deben ser breves y conversacionales (máximo 50 palabras).\nRESUMEN DE LA NOVELA: {config.RESUMEN_NOVELA}"
        config_kwargs["system_instruction"] = sys_instruction
        prompt_final = prompt_usuario
    
    # Lógica de reintento
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            chat = client.chats.create(
                model=model, 
                config=types.GenerateContentConfig(**config_kwargs), 
                history=hist_api
            )
            return chat.send_message(prompt_final).text
        except Exception as e:
            print(f"⚠️ Error en {model}: {e}")
            continue # Pasa al siguiente modelo
            
    return "Lo siento, no puedo responder en este momento."

# --- 3. RECUERDOS (CON FALLBACK) ---
def generar_recuerdo_personaje(client, personaje_data):
    prompt_base = f"""
    Analiza tu evolución en el texto de la novela adjunta en tu memoria. 
    Selecciona un momento clave y emocional (invéntalo si es necesario manteniendo la coherencia).
    Nárralo en 1ª persona como si lo revivieras ahora.
    Máximo 100 palabras.
    """
    
    config_kwargs = {}
    if es_hora_pico():
        cache_name = obtener_o_crear_cache(client)
        if cache_name:
            config_kwargs["cached_content"] = cache_name
        prompt_final = f"[INSTRUCCIONES: Actúa estrictamente como {personaje_data['name']}. {personaje_data['base_instruction']}]\n\n{prompt_base}"
    else:
        config_kwargs["system_instruction"] = f"Actúa estrictamente como {personaje_data['name']}. {personaje_data['base_instruction']}\nRESUMEN: {config.RESUMEN_NOVELA}"
        prompt_final = prompt_base
        
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(
                model=model, 
                contents=prompt_final,
                config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
            )
            return res.text.strip()
        except Exception as e:
            print(f"⚠️ Error recuerdo {model}: {e}")
            continue
            
    return "Intento recordar, pero hay mucha niebla..."

# --- 4. CURIOSIDADES Y TRIVIAL (CON FALLBACK) ---
def generar_pregunta_trivial(client):
    tema = random.choice(["detalles de la trama", "escenarios de la novela", "contexto histórico"])
    prompt_base = f"Genera pregunta test difícil sobre {tema} basada en la novela de tu memoria. JSON Output: {{'pregunta':'','opciones':['','',''],'correcta':''}}"
    
    config_kwargs = {"response_mime_type": "application/json"}
    
    if es_hora_pico():
        cache_name = obtener_o_crear_cache(client)
        if cache_name:
            config_kwargs["cached_content"] = cache_name
        prompt_final = prompt_base
    else:
        config_kwargs["system_instruction"] = f"Usa el siguiente resumen de la novela para generar la pregunta:\nRESUMEN: {config.RESUMEN_NOVELA}"
        prompt_final = prompt_base
        
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(
                model=model, 
                contents=prompt_final, 
                config=types.GenerateContentConfig(**config_kwargs)
            )
            return json.loads(res.text)
        except:
            continue
            
    return {"pregunta": "¿En qué ciudad transcurre la trama?", "opciones": ["Madrid", "Sevilla", "Londres"], "correcta": "Sevilla"}

def generar_curiosidad(client):
    temas = ["moda victoriana", "medicina del siglo XIX", "etiqueta social", "inventos de la revolución industrial", "supersticiones", "literatura romántica", "vida en Londres vs Sevilla", "el lenguaje de los abanicos", "duelos de honor","contexto historico"]
    tema = random.choice(temas)
    prompt_base = f"Dato real curioso y poco conocido sobre {tema} durante el periodo del romanticismo español o ingles. Máximo 25 palabras. Varía la respuesta cada vez."
    
    config_kwargs = {}
    if es_hora_pico():
        cache_name = obtener_o_crear_cache(client)
        if cache_name:
            config_kwargs["cached_content"] = cache_name
    else:
        config_kwargs["system_instruction"] = f"Contexto general: {config.RESUMEN_NOVELA}"

    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            res = client.models.generate_content(model=model, contents=prompt_base, config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None)
            return res.text
        except:
            continue
    return "El duelo por honor seguía siendo una práctica clandestina en 1870."