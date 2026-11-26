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

# Dominios oficiales a excluir para enfocarse solo en medios y fuentes externas
DOMINIOS_EXCLUIDOS = [
    "acclaimenergy.com",
    "acclaimenergy.com.mx",
    "://acclaimenergy.com",
    "://acclaimenergy.com.mx"
]

st.set_page_config(page_title=f"Agente: {EMPRESA}", page_icon="⚡")
st.title(f"⚡ Agente de Prensa y Terceros: {EMPRESA}")
st.write(f"Monitoreo en medios externos sobre **{EMPRESA}** y **{VOCERA}**.")

pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej. Entrevistas, menciones en prensa o eventos en 2026")

if st.button("Investigar", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta primero.")
    else:
        estado = st.status("Iniciando investigación en fuentes externas...", expanded=True)
        try:
            estado.write("1/2 Buscando en prensa y sitios de terceros...")
            if any(p in pregunta.lower() for p in ["maria", "maría", "treviño"]):
                consulta = f'"{VOCERA}" "{EMPRESA}" {pregunta}'
            else:
                consulta = f'"{EMPRESA}" {pregunta}'
                
            # exclude_domains bloquea los sitios oficiales de la empresa
            resultados = tavily.search(
                query=consulta,
                search_depth="basic",
                max_results=6,
                exclude_domains=DOMINIOS_EXCLUIDOS
            )
            
            contexto_web = "\n".join([f"- {r['title']} ({r['url']}): {r['content'][:450]}" for r in resultados['results']])
            
            estado.write("2/2 Redactando resumen ejecutivo...")
            prompt = f"""
            Eres un analista de inteligencia corporativa y monitoreo de medios especializado en {EMPRESA} y en {VOCERA}.
            Analiza exclusivamente lo que dicen fuentes externas, medios de comunicación y terceros sobre la empresa o su directiva.
            Reglas:
            - Resume de forma ejecutiva y clara usando solo la información proporcionada abajo.
            - No incluyas información proveniente de sitios oficiales de {EMPRESA}.
            - Cita siempre el medio o fuente externa con enlaces Markdown clickeables.
            
            Información de terceros encontrada:
            {contexto_web}
            
            Consulta: {pregunta}
            """
            
            modelos_respaldo = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.5-flash"]
            respuesta_texto = None
            ultimo_error = None
            
            for modelo in modelos_respaldo:
                try:
                    respuesta = client.models.generate_content(
                        model=modelo,
                        contents=prompt
                    )
                    respuesta_texto = respuesta.text
                    break
                except Exception as err:
                    ultimo_error = err
                    continue
            
            if respuesta_texto:
                estado.update(label="¡Investigación en medios completada!", state="complete", expanded=False)
                st.markdown(respuesta_texto)
            else:
                raise ultimo_error
                
        except Exception as e:
            estado.update(label="Se detuvo la búsqueda", state="error")
            st.error(f"Ocurrió un error al consultar los modelos: {e}")
