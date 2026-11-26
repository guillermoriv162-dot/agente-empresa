import os
import streamlit as st
from google import genai
from tavily import TavilyClient

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# --- EDITA ESTOS DOS DATOS CON LA INFORMACIÓN REAL ---
EMPRESA = "Acclaim Energy"
VOCERA = "María José Treviño"
# ----------------------------------------------------

st.set_page_config(page_title=f"Agente: {EMPRESA}", page_icon="🔎")
st.title(f"🔎 Agente de Monitoreo: {EMPRESA}")
st.write(f"Consulta noticias y actividad reciente sobre **{EMPRESA}** y **{VOCERA}** en Latinoamérica.")

pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej. Últimas entrevistas o noticias de esta semana")

if st.button("Investigar", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta primero.")
    else:
        with st.spinner("Buscando en internet y analizando resultados..."):
            consulta = f"{EMPRESA} {VOCERA} Latinoamerica {pregunta}"
            resultados = tavily.search(query=consulta, search_depth="advanced", max_results=5)
            
            contexto_web = "\n".join([f"- {r['title']} ({r['url']}): {r['content']}" for r in resultados['results']])
            
            prompt = f"""
            Eres un analista corporativo especializado en {EMPRESA} y en {VOCERA} (encargada en Latinoamérica).
            Responde usando exclusivamente la información web proporcionada abajo.
            Cita siempre las fuentes con enlaces Markdown clickeables. Si no hay información reciente, indícalo con claridad.
            
            Información web:
            {contexto_web}
            
            Consulta: {pregunta}
            """
            
            respuesta = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            st.markdown(respuesta.text)
