import streamlit as st
import time
from llm_engine import generar_pregunta_trivial, generar_curiosidad

# DECORADOR IMPORTANTE: Aísla el refresco de esta sección
@st.fragment
def render_sidebar_ia(client_text, novel_text):
    """Renderiza las pestañas de Juego y Curiosidades sin bloquear la app."""
    t_quiz, t_cur = st.tabs(["🎮 Juego", "💡 Curiosidades"])
    
    # --- PESTAÑA 1: TRIVIAL ---
    with t_quiz:
        st.write(f"**Puntuación: {st.session_state.quiz_score}/10**")
        
        # Botón para generar pregunta
        if st.button("🎲 Nueva Pregunta") or st.session_state.get("pregunta_actual") is None:
            with st.spinner("Consultando archivos..."):
                q_json = generar_pregunta_trivial(client_text, novel_text)
                st.session_state.pregunta_actual = q_json
                st.rerun()

        if st.session_state.get("pregunta_actual"):
            q_raw = st.session_state.pregunta_actual
            
            # Control de robustez (Lista vs Diccionario)
            if isinstance(q_raw, list) and len(q_raw) > 0:
                q = q_raw[0]
            elif isinstance(q_raw, dict):
                q = q_raw
            else:
                st.error("Error formato IA. Reintentando...")
                st.session_state.pregunta_actual = None
                st.rerun()

            with st.form("quiz_side"):
                st.write(f"**{q.get('pregunta', 'Pregunta ilegible')}**")
                
                opciones = q.get('opciones', [])
                if not opciones:
                    st.warning("Error en opciones.")
                    st.stop()
                    
                ans = st.radio("Respuesta:", opciones)
                
                if st.form_submit_button("Responder"):
                    if ans == q.get('correcta'):
                        st.session_state.quiz_score += 1
                        st.session_state.pregunta_actual = None
                        st.success("¡Correcto! 🎉")
                        time.sleep(1); st.rerun()
                    else: 
                        st.error("❌ Incorrecto. Inténtalo de nuevo.")

    # --- PESTAÑA 2: CURIOSIDADES ---
    with t_cur:
        if "curiosidad_ia" not in st.session_state:
            # Texto por defecto (Carga instantánea)
            st.session_state.curiosidad_ia = "España vivió el fin del absolutismo, el exilio liberal, guerras carlistas e inestabilidad política tras la muerte de Fernando VII."
            
        st.info(f"💡 {st.session_state.curiosidad_ia}")
        
        if st.button("🔄 Generar Nueva Curiosidad"):
            with st.spinner("Investigando..."):
                dato = generar_curiosidad(client_text)
                st.session_state.curiosidad_ia = dato
                st.rerun()