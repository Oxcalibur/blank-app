# llm_engine.py
from google.genai import types
import random
import json

def generar_respuesta_chat(client, historial, prompt_usuario, personaje_data, contexto_libro):
    """Genera respuesta conversacional."""
    sys_instruction = f"{personaje_data['base_instruction']}\nContexto: {contexto_libro[:15000]}"
    
    # Convertir historial de Streamlit a formato Gemini
    hist_api = [
        types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]) 
        for m in historial
    ]
    
    chat = client.chats.create(
        model="gemini-2.5-flash", 
        config=types.GenerateContentConfig(system_instruction=sys_instruction), 
        history=hist_api
    )
    return chat.send_message(prompt_usuario).text

def generar_recuerdo_personaje(client, personaje_data, contexto_libro):
    """
    Genera un recuerdo en 1ª persona, asegurando que el personaje no alucine 
    con cosas que no sabe (Filtro de Conciencia).
    """
    prompt = f"""
    Actúa estrictamente como {personaje_data['name']}. 
    Búscate a ti mismo en este libro: {contexto_libro[:40000]}. 
    Selecciona una escena donde TÚ aparezcas o algo que TÚ hayas visto.
    Reescríbela en 1ª persona desde tu punto de vista actual. 
    PROHIBIDO decir que no te conoces o hablar como Leonor si no eres ella.
    Máximo 80 palabras.
    """
    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return res.text.strip()

def generar_pregunta_trivial(client, contexto_libro):
    """Genera pregunta JSON para el trivial."""
    tema = random.choice(["la novela", "la vida en 1870"])
    prompt = f"""
    Genera pregunta test sobre {tema}. 
    Contexto libro: {contexto_libro[:3000]}. 
    JSON Output: {{'pregunta':'','opciones':['','',''],'correcta':''}}
    """
    res = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt, 
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(res.text)

def generar_curiosidad(client):
    """Genera dato histórico."""
    prompt = "Dato real sorprendente de 1870 o Romanticismo en España/Europa. Máximo 25 palabras."
    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return res.text