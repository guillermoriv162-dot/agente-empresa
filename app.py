import os
import streamlit as st
from google import genai
from tavily import TavilyClient

@st.cache_resource
def iniciar_clientes():
    g_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'timeout': 20000})
    t_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    return g_client, t_client

client, tavily = iniciar_clientes()

EMPRESA = "Acclaim Energy"
VOCERA = "María José Treviño"

st.set_page_config(page_title=f"Agente: {EMPRESA}", page_icon="⚡")
st.title(f"⚡ Agente Rápido: {EMPRESA}")
st.write(f"Monitoreo sobre **{EMPRESA}** y **{VOCERA}**.")

pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej. Noticias recientes de Acclaim Energy en 2026")

if st.button("Investigar", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta primero.")
    else:
        estado = st.status("Iniciando investigación...", expanded=True)
        try:
            estado.write("1/2 Buscando noticias en internet...")
            if any(p in pregunta.lower() for p in ["maria", "maría", "treviño"]):
                consulta = f'"{VOCERA}" "{EMPRESA}" {pregunta}'
            else:
                consulta = f'"{EMPRESA}" {pregunta}'
                
            resultados = tavily.search(query=consulta, search_depth="basic", max_results=5)
            contexto_web = "\n".join([f"- {r['title']} ({r['url']}): {r['content'][:400]}" for r in resultados['results']])
            
            estado.write("2/2 Redactando resumen con IA...")
            prompt = f"""
            Eres un analista corporativo especializado en {EMPRESA} y en {VOCERA}.
            Resume de forma ejecutiva usando solo esta información web. Incluye enlaces Markdown clickeables.
            
            Información:
            {contexto_web}
            
            Consulta: {pregunta}
            """
            
            respuesta = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            estado.update(label="¡Investigación completada!", state="complete", expanded=False)
            st.markdown(respuesta.text)
            
        except Exception as e:
            estado.update(label="Se detuvo la búsqueda", state="error")
            st.error(f"Ocurrió un retraso o error: {e}")
