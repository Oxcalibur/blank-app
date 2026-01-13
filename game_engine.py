# game_engine.py
import streamlit as st
import time
from llm_engine import generar_pregunta_trivial, generar_curiosidad

@st.fragment
def render_sidebar_ia(client_text, novel_text):
    """Renderiza las pestañas de Juego y Curiosidades sin recargar la app."""
    t_quiz, t_cur = st.tabs(["🎮 Juego", "💡 Curiosidades"])
    
    # --- TRIVIAL ---
    with t_quiz:
        st.write(f"**Puntuación: {st.session_state.quiz_score}/10**")
        
        # Botón para pedir pregunta
        if st.button("🎲 Nueva Pregunta") or st.session_state.get("pregunta_actual") is None:
            with st.spinner("Generando..."):
                q_json = generar_pregunta_trivial(client_text, novel_text)
                st.session_state.pregunta_actual = q_json
                st.rerun()

        # Mostrar pregunta si existe
        if st.session_state.get("pregunta_actual"):
            q = st.session_state.pregunta_actual
            with st.form("quiz_side"):
                st.write(q['pregunta'])
                ans = st.radio("Respuesta:", q['opciones'])
                if st.form_submit_button("Responder"):
                    if ans == q['correcta']:
                        st.session_state.quiz_score += 1
                        st.session_state.pregunta_actual = None
                        st.success("¡Correcto!")
                        time.sleep(1)
                        st.rerun()
                    else: 
                        st.error(f"Fallo. Era: {q['correcta']}")

    # --- CURIOSIDADES ---
    with t_cur:
        if "curiosidad_ia" not in st.session_state:
            st.session_state.curiosidad_ia = "Descubre un secreto..."
            
        st.info(f"💡 {st.session_state.curiosidad_ia}")
        
        if st.button("🔄 Ver otra curiosidad"):
            dato = generar_curiosidad(client_text)
            st.session_state.curiosidad_ia = dato
            st.rerun()