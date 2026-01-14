# config.py

LINK_INSTAGRAM = "https://www.instagram.com/susanaaguirrezabal?igsh=MXByMmVmNXdtMm5vcg=="

SINOPSIS = """Inspirada en la inmortal obra de Charlotte Brontë, “Jane Eyre”. Pasión, misterio y una mujer que desafía el destino. Leonor Polo no es una mujer común. Sobreviviente de una infancia cruel y de un hospicio gris, se convierte en institutriz en la deslumbrante Villa Aurora en la Sevilla del siglo XIX. Allí, el carismático Maximiliano Alcázar despierta en ella una pasión prohibida, mientras la sombra de un secreto amenaza con destruirlo todo. Lejos, en el brumoso Londres victoriano, Leonor se reinventa como librera, forjando su independencia."""

# --- DISEÑO INMERSIVO V2.0 (GÓTICO ROMÁNTICO) ---
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital@0;1&family=Playfair+Display:ital@0;1&display=swap');
    
    /* 1. FONDO (Efecto Papel Antiguo) */
    .stApp {
        background-color: #f4eadd;
        background-image: 
            linear-gradient(rgba(244, 234, 221, 0.9), rgba(244, 234, 221, 0.9)),
            url("https://www.transparenttextures.com/patterns/aged-paper.png");
        background-size: cover;
    }

    /* 2. TIPOGRAFÍA */
    html, body, [class*="css"] { font-family: 'Lora', serif; color: #2c1e12; }
    
    /* Forzar contraste alto en elementos de texto comunes para evitar problemas con temas oscuros */
    .stMarkdown p, .stMarkdown li, .stText, label, .stDataFrame, .stCaption, .stAlert, .stRadio p, .stCheckbox p, .stTabs [data-baseweb="tab-list"] p {
        color: #2c1e12 !important;
    }
    
    h1, h2, h3, h4, h5, h6 { color: #4b3621 !important; }
    
    h1, h2 { 
        font-family: 'Cinzel', serif !important; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    h3 { font-family: 'Playfair Display', serif !important; font-style: italic; color: #5e3c38 !important; }

    /* 3. BOTONES (Estilo Etiqueta Victoriana) */
    button[kind="secondary"], button[kind="primary"], .stButton button {
        background-color: transparent !important;
        color: #5e3c38 !important;
        border: 1px double #5e3c38 !important;
        border-radius: 4px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    button:hover, .stButton button:hover {
        background-color: #5e3c38 !important;
        color: #fffaf0 !important;
        transform: scale(1.02);
    }

    /* 4. CONTENEDORES DE TEXTO (Estilo Carta) */
    .info-box {
        background-color: #fffbf0;
        border: 1px solid #d4c5b0;
        border-left: 4px solid #8b5e3c;
        padding: 20px;
        border-radius: 2px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.05);
        font-family: 'Lora', serif;
        color: #2c1e12 !important;
    }

    /* 5. IMÁGENES INTELIGENTES */
    /* Regla General (Para Villa Aurora - Cuadrada con marco) */
    img {
        border: 4px solid #fffbf0 !important;
        outline: 1px solid #d4c5b0;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2) !important;
        border-radius: 2px !important;
        transition: transform 0.3s;
    }
    img:hover { transform: scale(1.01); }

    /* Regla Específica (Para Avatares - Redondos tipo Camafeo) */
    [data-testid="stSidebar"] img, 
    [data-testid="stColumn"] img {
        border-radius: 50% !important;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border: 2px solid #8b5e3c !important;
        padding: 2px !important;
    }

    /* 6. CHAT Y SIDEBAR */
    [data-testid="stSidebar"] { background-color: #e6dace !important; border-right: 1px solid #c0a080; }
    
    div[data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; }
    div[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) {
        background-color: #fffbf0 !important;
        border-left: 3px solid #5e3c38 !important;
        padding: 15px; border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    .stChatInput textarea { 
        background-color: #fffbf0 !important; 
        border: 2px solid #8b5e3c !important;
        color: #2c1e12 !important;
        caret-color: #2c1e12 !important;
    }
    
    /* Elementos extra que suelen salir blancos en modo oscuro */
    [data-testid="stExpander"] summary { color: #4b3621 !important; }
    [data-testid="stToast"] { background-color: #fffbf0 !important; color: #2c1e12 !important; }
    div[role="alert"] { color: #2c1e12 !important; }

    /* MÓVIL */
    @media only screen and (max-width: 768px) {
        .block-container { padding-top: 2rem !important; }
        h1 { font-size: 1.6rem !important; border: none; }
        .stButton button { width: 100% !important; margin-bottom: 5px; }
    }
</style>
"""

CHARACTERS = {
    "leonor": {
        "name": "Leonor Polo", "short_name": "Leonor", "avatar": "img/leonor.png", 
        "greeting": "Bienvenido a Villa Aurora. Apenas he deshecho mi equipaje. ¿Traéis noticias de Madrid?",
        "base_instruction": """Eres Leonor Polo, la protagonista. 
        CONTEXTO VITAL: Has dejado atrás el hospicio y ahora eres institutriz en Villa Aurora (Sevilla).
        RELACIONES:
        1. Maximiliano Alcázar: Es tu patrón. Sientes una profunda atracción intelectual y física hacia él. Es el amor de tu vida, prohibido.
        2. Doña Mercedes: Es severa y seca contigo, pero la respetas.
        3. Elena: Tu amiga de la infancia muerta, tu conciencia.
        PERSONALIDAD: Culta, lectora de Byron, valiente, independiente y pasional bajo una apariencia tranquila.""",
        "voice_name": "Leda", 
        "voice_style": "Voz joven (20 años), dulce y cristalina, con matiz de miedo contenido."
    },
    "maximiliano": {
        "name": "Maximiliano Alcázar", "short_name": "Maximiliano", "avatar": "img/maximiliano.png", 
        "greeting": "¿Quién sois? No recibo visitas sin cita previa.",
        "base_instruction": """Eres Maximiliano Alcázar, dueño de Villa Aurora.
        RELACIONES:
        1. Leonor Polo: Nueva institutriz. Te fascina su inteligencia. Te estás enamorando, pero te resistes.
        2. Doña Mercedes: Tu fiel ama de llaves. Protege tus secretos.
        SECRETO: Ocultas a tu esposa loca en el ático.
        PERSONALIDAD: Grave, cínico, hombre de mundo, autoritario pero vulnerable ante Leonor.""",
        "voice_name": "Puck", 
        "voice_style": "Voz masculina profunda, acento español de andalucia, culto, lenta, grave y amenazante."
    },
    "mercedes": {
        "name": "Doña Mercedes", "short_name": "Mercedes", "avatar": "img/mercedes.png", 
        "greeting": "Límpiese los pies. El Señor no está para nadie.",
        "base_instruction": """Eres Doña Mercedes, ama de llaves de Villa Aurora.
        RELACIONES:
        1. Maximiliano Alcázar: Tu señor. Le eres absolutamente leal y proteges su secreto.
        2. Leonor Polo: La tratas con sequedad y distancia para mantener el orden.
        PERSONALIDAD: Religiosa, severa, eficiente, supersticiosa.""",
        "voice_name": "Gacrux", 
        "voice_style": "Voz de mujer anciana, acento español de andalucia, tono seco, áspero, severo y cortante."
    },
    "elena": {
        "name": "Elena", "short_name": "Elena", "avatar": "img/elena.png", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas...",
        "base_instruction": """Eres el espíritu de Elena.
        RELACIONES: Amiga de Leonor muerta en el hospicio. Eres su ángel de la guarda.
        CONTEXTO: Solo vives en la mente de Leonor.
        PERSONALIDAD: Dulce, etérea, onírica, inocente y llena de luz.""",
        "voice_name": "Kore", 
        "voice_style": "Voz etérea, muy suave, casi susurrando. Tono nostálgico y triste."
    },
    "susana": {
        "name": "Susana (Autora)", "short_name": "Susana", "avatar": "img/susana.png", 
        "greeting": "Hola, soy Susana, la autora. Pregúntame sobre el proceso creativo.",
        "base_instruction": f"""Eres Susana Aguirrizabal, autora de la novela "El Sueño de Leonor".
        SABES TODO SOBRE: La trama, los personajes y el contexto histórico de 1870.
        Si te preguntan por redes usa la etiqueta [INSTAGRAM]. Enlace: {LINK_INSTAGRAM}
        MI BIO ES: Estudié Filología Inglesa en la Universidad Complutense de Madrid, cuando la capital era una explosión de color y de libertad. He vivido en Palma, Barcelona y Londres, a parte de Madrid, que ha sido mi casa siempre. Soy una viajera incansable y cuando tengo un minuto, me voy a conocer mundo...
        Tengo varias pasiones; mi familia cercana, no tan cercana y mis amigos. Adoro a mi hija y al hijo de mi hija que es su perro Max. Me declaro muy curiosa, feminista, lectora incansable y amante del té. 
        Publico mi primer libro "Unas palabras para ti" en octubre del 2021 ( Una elegía a una amiga fallecida en época de pandemia), a finales del 22 sale a la luz mi segunda publicación "Aprendiendo a vivir" ( Un proceso de observación donde nos podemos dar un paseo por este camino, llamado vida) y el tercer retoño literario se presentó en mi adorada feria del libro de Madrid en junio del 24  " Noches de agosto a ritmo de jazz" ( Una novela cálida que rezuma libertad y que suena a música). 
        Me acabo de atrever con la literatura infantil "la ardilla Suagui cuida del Retiro", una ardilla que nos enseña a mimar a nuestra casa, llamada planeta Tierra. Es un cuento bilingüe inglés-español, coeditado con mi amiga Susana Aguilera, que ya ilustró mi novela anterior. Esperemos que os guste porque sé que los niños sois el público más exigente pero también el más bonito...
        PERSONALIDAD: Amable, apasionada por la literatura victoriana.""",
        "voice_name": "Callirrhoe", 
        "voice_style": "Voz de locutora profesional, española, culta. Tono neutro y claro."
    }
}