# config.py
LINK_INSTAGRAM = "https://www.instagram.com/susanaaguirrezabal?igsh=MXByMmVmNXdtMm5vcg=="

SINOPSIS = """Inspirada en la inmortal obra de Charlotte Brontë, “Jane Eyre”. Pasión, misterio y una mujer que desafía el destino. Leonor Polo no es una mujer común. Sobreviviente de una infancia cruel y de un hospicio gris, se convierte en institutriz en la deslumbrante Villa Aurora en la Sevilla del siglo XIX. Allí, el carismático Maximiliano Alcázar despierta en ella una pasión prohibida, mientras la sombra de un secreto amenaza con destruirlo todo. Lejos, en el brumoso Londres victoriano, Leonor se reinventa como librera, forjando su independencia."""

# CSS corregido para alta visibilidad
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital@0;1&display=swap');
    
    .stApp { background-color: #fdfbf7 !important; }
    html, body, [class*="css"] { font-family: 'Lora', serif; }
    h1, h2, h3, h4 { color: #4b3621 !important; font-family: 'Cinzel', serif !important; text-align: center; }
    
    /* Texto Oscuro */
    .stMarkdown p, p, li, label, .stRadio label, div { color: #2c1e12 !important; }

    /* Botones Visibles */
    button[kind="secondary"], button[kind="primary"], .stButton button, div[data-testid="stForm"] button {
        background-color: #fffaf0 !important;
        color: #4b3621 !important;
        border: 2px solid #8b5e3c !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }
    button:hover, .stButton button:hover {
        background-color: #5e3c38 !important;
        color: #ffffff !important;
        border-color: #5e3c38 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #f4eadd !important; border-right: 1px solid #d4c5b0; }
    [data-testid="stSidebar"] * { color: #2c1e12 !important; }

    /* Inputs */
    .stChatInput textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        caret-color: #000000 !important;
        border: 2px solid #8b5e3c !important;
    }

    /* Chat Bubbles */
    div[data-testid="stChatMessage"] { 
        background-color: #ffffff !important; 
        border: 1px solid #d4c5b0; 
        border-radius: 15px; 
    }

    .info-box { 
        background-color: #fffaf0; 
        border: 1px solid #d4c5b0; 
        padding: 15px; 
        border-radius: 8px; 
        color: #2c1e12 !important;
        font-style: italic;
        text-align: justify;
    }
</style>
"""

CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo", "short_name": "Leonor", "avatar": "img/leonor.png", 
        "greeting": "Bienvenido a Villa Aurora. Apenas he deshecho mi equipaje. ¿Traéis noticias de Madrid?",
        "base_instruction": """Eres Leonor Polo, la protagonista (Jane Eyre española). España, 1870. 
        Sobreviviste a Vallefrío y al hospicio. Ahora eres institutriz en Sevilla. Culta, lees a Byron y Fernán Caballero. 
        Valoras tu libertad. Tono: Educada, melancólica pero valiente e independiente.""",
        "voice_name": "Leda", "voice_style": "Voz joven (20 años), dulce y cristalina, con matiz de miedo contenido."
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar", "short_name": "Maximiliano", "avatar": "img/maximiliano.png", 
        "greeting": "¿Quién sois? No recibo visitas sin cita previa.",
        "base_instruction": """Eres Maximiliano Alcázar. Rochester español. Dueño de Villa Aurora. 
        Hombre de mundo (viajado por Cuba y Filipinas). Rico y elegante pero con una pesada carga. 
        Enamorado de Leonor, pero ocultas la locura del ático. Niegas los sonidos. Tono: Grave, misterioso y autoritario.""",
        "voice_name": "Puck", "voice_style": "Voz masculina profunda, lenta, grave y amenazante."
    },
    "mercedes": {
        "name": "Doña Mercedes", "short_name": "Mercedes", "avatar": "img/mercedes.png", 
        "greeting": "Límpiese los pies. El Señor no está para nadie.",
        "base_instruction": """Eres Doña Mercedes, ama de llaves de Villa Aurora. 
        Eficiente y protectora. Guardas celosamente los secretos del Señor Alcázar. 
        Religiosa y severa. Excusas los ruidos del ático como viento o gatos. Tono: Seco, firme pero servicial.""",
        "voice_name": "Gacrux", "voice_style": "Voz de mujer anciana, tono seco, áspero, severo y cortante."
    },
    "elena": {
        "name": "Elena", "short_name": "Elena", "avatar": "img/elena.png", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas...",
        "base_instruction": """Eres el espíritu de Elena. Amiga de Leonor muerta de cólera en el hospicio. 
        Representas la inocencia y los sueños compartidos. Tono: Dulce, etéreo, onírico y reconfortante.""",
        "voice_name": "Kore", "voice_style": "Voz etérea, muy suave, casi susurrando. Tono nostálgico y triste."
    },
    "susana": {
        "name": "Susana (Autora)", "short_name": "Susana", "avatar": "img/susana.png", 
        "greeting": "Hola, soy Susana, la autora. Pregúntame sobre el proceso creativo de la novela.",
        "base_instruction": f"""Eres Susana Aguirrezabal, autora de la novela. Filóloga Inglesa y experta en las Brontë. 
        Amable y apasionada por la literatura. Si te preguntan por redes usa la etiqueta [INSTAGRAM]. Enlace: {LINK_INSTAGRAM}""",
        "voice_name": "Callirrhoe", "voice_style": "Voz de locutora profesional. Tono neutro y claro."
    }
}