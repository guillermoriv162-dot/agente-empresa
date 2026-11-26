import os
import time
import streamlit as st
from google import genai
from tavily import TavilyClient

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

EMPRESA = "Acclaim Energy"
VOCERA = "María José Treviño"

st.set_page_config(page_title=f"Agente: {EMPRESA}", page_icon="🔎")
st.title(f"🔎 Agente de Monitoreo: {EMPRESA}")
st.write(f"Consulta noticias y actividad reciente sobre **{EMPRESA}** y **{VOCERA}**.")

pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej. Noticias recientes de Acclaim Energy en 2026 o entrevistas de María José Treviño")

if st.button("Investigar", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta primero.")
    else:
        with st.spinner("Buscando en internet y analizando resultados..."):
            # Búsqueda inteligente: si mencionas a María José busca sobre ella; si no, busca amplio sobre la empresa
            if "maria" in pregunta.lower() or "maría" in pregunta.lower() or "treviño" in pregunta.lower():
                consulta = f'"{VOCERA}" "{EMPRESA}" {pregunta}'
            else:
                consulta = f'"{EMPRESA}" {pregunta}'
                
            resultados = tavily.search(query=consulta, search_depth="basic", max_results=7)
            
            contexto_web = "\n".join([f"- {r['title']} ({r['url']}): {r['content'][:600]}" for r in resultados['results']])
            
            prompt = f"""
            Eres un analista corporativo especializado en {EMPRESA} y en {VOCERA} (directora en México/Latinoamérica).
            Analiza la información encontrada en internet y responde de forma completa, clara y estructurada con viñetas.
            Reglas:
            - Usa únicamente los datos proporcionados abajo.
            - Cita siempre la fuente con enlaces Markdown clickeables.
            - Menciona fechas si aparecen en los textos.
            
            Información encontrada en la web:
            {contexto_web}
            
            Consulta del usuario: {pregunta}
            """
            
            # Reintento automático por si el servidor de Google tiene saturación momentánea
            for intento in range(3):
                try:
                    respuesta = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )
                    st.markdown(respuesta.text)
                    break
                except Exception as e:
                    if intento < 2:
                        time.sleep(3)
                    else:
                        st.error("El servidor de Google está saturado en este momento. Intenta pulsar 'Investigar' nuevamente en unos segundos.")
