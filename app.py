import os
import streamlit as st
from google import genai
from tavily import TavilyClient

@st.cache_resource
def iniciar_clientes():
    g_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'timeout': 25000})
    t_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    return g_client, t_client

client, tavily = iniciar_clientes()

EMPRESA = "Acclaim Energy"
VOCERA = "María José Treviño"

DOMINIOS_EXCLUIDOS = [
    "acclaimenergy.com",
    "acclaimenergy.com.mx",
    "://acclaimenergy.com",
    "://acclaimenergy.com.mx"
]

st.set_page_config(page_title=f"Agente: {EMPRESA}", page_icon="🔎", layout="wide")
st.title(f"🔎 Inteligencia de Medios Externos: {EMPRESA}")
st.write(f"Monitoreo detallado en prensa, entrevistas y terceros sobre **{EMPRESA}** y **{VOCERA}**.")

pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej. Entrevistas de María José Treviño o presencia en prensa en 2026")

if st.button("Investigar", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta primero.")
    else:
        estado = st.status("Iniciando rastreo profundo en medios externos...", expanded=True)
        try:
            estado.write("1/3 Buscando menciones de la empresa en prensa externa...")
            res_empresa = tavily.search(
                query=f"{EMPRESA} Mexico Latinoamerica {pregunta}",
                search_depth="advanced",
                max_results=6,
                exclude_domains=DOMINIOS_EXCLUIDOS
            )
            
            estado.write("2/3 Buscando entrevistas y participación de María José Treviño...")
            res_vocera = tavily.search(
                query=f"{VOCERA} Acclaim Energy {pregunta}",
                search_depth="advanced",
                max_results=5,
                exclude_domains=DOMINIOS_EXCLUIDOS
            )
            
            urls_vistas = set()
            fuentes_limpias = []
            for r in res_empresa['results'] + res_vocera['results']:
                if r['url'] not in urls_vistas:
                    urls_vistas.add(r['url'])
                    fuentes_limpias.append(f"TÍTULO: {r['title']}\nURL: {r['url']}\nCONTENIDO: {r['content'][:1000]}")
            
            contexto_web = "\n\n---\n\n".join(fuentes_limpias)
            
            estado.write("3/3 Analizando fuentes y redactando reporte detallado...")
            prompt = f"""
            Eres un analista senior de inteligencia corporativa y relaciones públicas especializado en {EMPRESA} y {VOCERA}.
            Tu tarea es redactar un reporte EXHAUSTIVO, DETALLADO y 100% VERÍDICO basado ÚNICAMENTE en las fuentes externas proporcionadas abajo.

            REGLAS ESTRICTAS DE REDACCIÓN Y CITADO:
            1. CERO INVENCIONES: Si una fecha, cifra o declaración no aparece explícitamente en los textos de abajo, NO la incluyas ni la supongas.
            2. ENLACES INCRUSTADOS EN EL TEXTO (MUY IMPORTANTE): NO crees una sección de "Fuentes Consultadas" al final. En su lugar, incrusta cada enlace Markdown clickeable directamente dentro de la oración o viñeta donde mencionas ese dato o noticia. Ejemplo correcto: "De acuerdo con [El Economista](URL), la empresa señaló..." o "En una entrevista para [Energía a Debate](URL), {VOCERA} explicó...".
            3. DETALLE AMPLIO: Desarrolla cada hallazgo explicando el contexto, qué tema energético o corporativo se trató y cuál fue el aporte de {EMPRESA} o {VOCERA}.
            4. ESTRUCTURA DEL REPORTE:
               - **Panorama General:** Resumen ejecutivo de los hallazgos encontrados en medios externos.
               - **Menciones y Noticias sobre {EMPRESA}:** Desglose detallado con cada enlace incrustado en su párrafo correspondiente.
               - **Actividad Pública y Declaraciones de {VOCERA}:** Entrevistas, columnas, paneles o citas encontradas con cada enlace incrustado en su punto correspondiente.

            FUENTES EXTERNAS RECOPILADAS:
            {contexto_web}

            CONSULTA DEL USUARIO: {pregunta}
            """
            
            modelos_respaldo = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
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
                estado.update(label="¡Reporte detallado completado!", state="complete", expanded=False)
                st.markdown(respuesta_texto)
            else:
                raise ultimo_error
                
        except Exception as e:
            estado.update(label="Se detuvo la búsqueda", state="error")
            st.error(f"Ocurrió un error al consultar los modelos: {e}")
