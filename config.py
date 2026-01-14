# config.py

LINK_INSTAGRAM = "https://www.instagram.com/susanaaguirrezabal?igsh=MXByMmVmNXdtMm5vcg=="

SINOPSIS = """Inspirada en la inmortal obra de Charlotte Brontë, “Jane Eyre”. Pasión, misterio y una mujer que desafía el destino. Leonor Polo no es una mujer común. Sobreviviente de una infancia cruel y de un hospicio gris, se convierte en institutriz en la deslumbrante Villa Aurora en la Sevilla del siglo XIX. Allí, el carismático Maximiliano Alcázar despierta en ella una pasión prohibida, mientras la sombra de un secreto amenaza con destruirlo todo. Lejos, en el brumoso Londres victoriano, Leonor se reinventa como librera, forjando su independencia."""

# --- DISEÑO INMERSIVO V2.0 (GÓTICO ROMÁNTICO) ---
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Crimson+Text:wght@400;600&display=swap');

    /* 1. FONDO GENERAL Y COLOR (Modo Oscuro Elegante) */
    .stApp {
        background-color: #0e1117; /* Azul noche muy oscuro */
        color: #e0e0e0; /* Blanco hueso */
        font-family: 'Crimson Text', serif;
    }

    /* 2. TIPOGRAFÍA */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
        color: #d4af37 !important; /* Dorado apagado */
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Textos generales */
    p, li, label, .stMarkdown, .stText, .stCaption, .stRadio p, .stAlert p {
        color: #e0e0e0 !important;
        font-family: 'Crimson Text', serif;
        font-size: 1.1rem;
    }

    /* 3. BOTONES (Estilo Minimalista Dorado) */
    .stButton > button {
        background-color: transparent !important;
        color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
        font-family: 'Playfair Display', serif !important;
        border-radius: 5px !important;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background-color: #d4af37 !important;
        color: #0e1117 !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
        transform: scale(1.02);
    }

    /* 4. CONTENEDORES DE TEXTO */
    .info-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid #d4af37;
        border-left: 4px solid #d4af37;
        padding: 20px;
        border-radius: 5px;
        color: #e0e0e0 !important;
    }

    /* 5. IMÁGENES INTELIGENTES */
    img {
        border: 1px solid #d4af37 !important;
        transition: transform 0.3s;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    img:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); }

    /* Avatares circulares en columnas */
    [data-testid="stColumn"] img {
        border-radius: 50% !important;
        aspect-ratio: 1 / 1;
        object-fit: cover;
    }

    /* 6. CHAT Y SIDEBAR */
    [data-testid="stSidebar"] { background-color: #0e1117 !important; border-right: 1px solid #333; }
    
    div[data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; }
    div[data-testid="stChatMessage"]:has(div[aria-label="assistant"]) {
        background-color: rgba(212, 175, 55, 0.1) !important;
        border-left: 2px solid #d4af37 !important;
        padding: 15px; border-radius: 5px;
    }
    
    .stChatInput textarea { 
        background-color: #1e212b !important; 
        border: 1px solid #d4af37 !important;
        color: #e0e0e0 !important;
        caret-color: #d4af37 !important;
    }
    
    /* Ocultar elementos molestos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: transparent !important;}
    [data-testid="stSidebarCollapsedControl"] {
        color: #d4af37 !important;
        background-color: rgba(14, 17, 23, 0.2); /* Fondo sutil para contraste */
        z-index: 999999 !important; /* Siempre visible */
    }
    
    /* Estilo para las alertas (st.info) */
    div[data-testid="stAlert"] {
        background-color: rgba(212, 175, 55, 0.1) !important;
        border: 1px solid #d4af37 !important;
    }

    /* MÓVIL */
    @media only screen and (max-width: 768px) {
        .block-container { padding-top: 2rem !important; }
        h1 { font-size: 1.6rem !important; border: none; }
        .stButton button { width: 100% !important; margin-bottom: 5px; }
    }

    /* --- TARJETA DE PERSONAJE (FLIP CARD) --- */
    .contenedor-personaje {
        perspective: 1000px;
        background-color: transparent;
        width: 100%;
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }

    .tarjeta {
        position: relative;
        width: 200px;  /* Ajustado para columnas de Streamlit */
        height: 280px;
        text-align: center;
        transition: transform 0.8s;
        transform-style: preserve-3d;
        pointer-events: none; /* CLAVE: La tarjeta no captura clics, pasan al botón invisible */
    }

    /* FLIP TRIGGER: Hovering the COLUMN triggers the flip (fixes conflict with invisible button) */
    [data-testid="stColumn"]:hover .tarjeta {
        transform: rotateY(180deg);
    }

    .cara-frontal, .cara-trasera {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* ESTILO FRONTAL */
    .cara-frontal {
        background: #1a1a1a;
        border: 2px solid #d4af37;
    }

    .marco-imagen {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 3px double #d4af37;
        overflow: hidden;
        margin-bottom: 15px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        /* Fix for image overflow in some browsers */
        transform: translateZ(0); 
    }

    .marco-imagen img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.9;
    }

    .nombre-personaje {
        font-family: 'Cinzel', serif;
        color: #d4af37;
        font-size: 20px;
        margin-top: 10px;
        text-shadow: 1px 1px 2px black;
    }

    /* ESTILO TRASERO */
    .cara-trasera {
        background-color: #f4e4bc;
        color: #2c2c2c !important; /* Forzamos color oscuro en el papel */
        transform: rotateY(180deg);
        border: 2px solid #d4af37;
        padding: 15px;
        font-family: 'Crimson Text', serif;
    }
    
    .cara-trasera div { color: #2c2c2c !important; } /* Asegurar contraste */

    .titulo-trasero {
        font-family: 'Cinzel', serif;
        font-weight: bold;
        color: #5a4a42 !important;
        border-bottom: 1px solid #d4af37;
        margin-bottom: 10px;
        padding-bottom: 5px;
    }
    
    .texto-descripcion {
        font-size: 14px;
        font-style: italic;
        line-height: 1.3;
    }
    
    .alias {
        margin-top: 15px;
        font-size: 10px;
        color: #555 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
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
        "voice_style": "Voz joven (20 años), dulce y cristalina, con matiz de miedo contenido.",
        "role": "La Institutriz",
        "description": "Una mujer que desafía al destino. De un hospicio gris a la deslumbrante Villa Aurora."
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
        "voice_style": "Voz masculina profunda, acento español de andalucia, culto, lenta, grave y amenazante.",
        "role": "El Patrón",
        "description": "Dueño de Villa Aurora. Un hombre atormentado por secretos y sombras."
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
        "voice_style": "Voz de mujer anciana, acento español de andalucia, tono seco, áspero, severo y cortante.",
        "role": "El Ama de Llaves",
        "description": "Fiel guardiana del orden y de los pecados inconfesables de la casa."
    },
    "elena": {
        "name": "Elena", "short_name": "Elena", "avatar": "img/elena.png", 
        "greeting": "La brisa trae recuerdos de cuando éramos niñas...",
        "base_instruction": """Eres el espíritu de Elena.
        RELACIONES: Amiga de Leonor muerta en el hospicio. Eres su ángel de la guarda.
        CONTEXTO: Solo vives en la mente de Leonor.
        PERSONALIDAD: Dulce, etérea, onírica, inocente y llena de luz.""",
        "voice_name": "Kore", 
        "voice_style": "Voz etérea, muy suave, casi susurrando. Tono nostálgico y triste.",
        "role": "El Recuerdo",
        "description": "La amiga perdida. Una voz que susurra desde el pasado y guía tu conciencia."
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
        "voice_style": "Voz de locutora profesional, española, culta. Tono neutro y claro.",
        "role": "La Autora",
        "description": "La pluma que teje el destino. Pregúntale sobre el proceso creativo."
    }
}