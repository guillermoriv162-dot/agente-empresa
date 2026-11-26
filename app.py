import os
import streamlit as st
from google import genai
from google.genai import types
from tavily import TavilyClient

@st.cache_resource
def iniciar_clientes():
    g_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'timeout': 30000})
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

st.set_page_config(page_title=f"Agente: {EMPRESA}", page_icon="🛡️", layout="wide")
st.title(f"🛡️ Inteligencia Corporativa Verificada: {EMPRESA}")
st.write(f"Monitoreo estricto en medios externos sobre **{EMPRESA}** y **{VOCERA}** (cero relleno, 100% verificado).")

# Guarda historial de correcciones en la sesión para que aprenda de tus observaciones
if "reglas_aprendidas" not in st.session_state:
    st.session_state.reglas_aprendidas = []

pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej. Entrevistas de María José Treviño o presencia en prensa en 2026")

def llamar_gemini(prompt_texto):
    modelos_respaldo = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
    ultimo_error = None
    for modelo in modelos_respaldo:
        try:
            resp = client.models.generate_content(
                model=modelo,
                contents=prompt_texto,
                config=types.GenerateContentConfig(temperature=0.0) # 0.0 elimina creatividad y relleno
            )
            return resp.text
        except Exception as err:
            ultimo_error = err
            continue
    raise ultimo_error

if st.button("Investigar", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta primero.")
    else:
        estado = st.status("Ejecutando investigación verificada...", expanded=True)
        try:
            estado.write("1/4 Buscando en prensa externa sobre Acclaim Energy...")
            res_empresa = tavily.search(
                query=f"{EMPRESA} Mexico Latinoamerica {pregunta}",
                search_depth="advanced",
                max_results=6,
                exclude_domains=DOMINIOS_EXCLUIDOS
            )
            
            estado.write("2/4 Buscando menciones y entrevistas de María José Treviño...")
            res_vocera = tavily.search(
                query=f"{VOCERA} Acclaim Energy {pregunta}",
                search_depth="advanced",
                max_results=5,
                exclude_domains=DOMINIOS_EXCLUIDOS
            )
            
            # Filtro estricto: descarta resultados irrelevantes o duplicados
            urls_vistas = set()
            fuentes_limpias = []
            for r in res_empresa['results'] + res_vocera['results']:
                if r['url'] not in urls_vistas and r.get('score', 0) >= 0.45:
                    urls_vistas.add(r['url'])
                    fuentes_limpias.append(f"TÍTULO: {r['title']}\nURL: {r['url']}\nCONTENIDO: {r['content'][:1000]}")
            
            if not fuentes_limpias:
                estado.update(label="Sin hallazgos relevantes en prensa", state="complete", expanded=False)
                st.info(f"No se encontraron artículos externos relevantes y verificables sobre '{pregunta}'. Intenta con términos más amplios.")
            else:
                contexto_web = "\n\n---\n\n".join(fuentes_limpias)
                reglas_extra = "\n".join([f"- {r}" for r in st.session_state.reglas_aprendidas])
                
                estado.write("3/4 Redactando borrador inicial con citas incrustadas...")
                prompt_borrador = f"""
                Eres un analista de inteligencia corporativa. Redacta un reporte basado ÚNICAMENTE en las fuentes externas de abajo.
                
                REGLAS INQUEBRANTABLES:
                1. PROHIBIDO RELLENAR: Si solo hay 1 o 2 datos reales, reporta únicamente esos. Nunca agregues introducciones genéricas, conclusiones vacías ni contexto inventado.
                2. ENLACES INCRUSTADOS: Inserta el enlace Markdown [Nombre del Medio o Artículo](URL) directamente dentro de la oración donde afirmas cada dato. No hagas lista de fuentes al final.
                3. PRECISIÓN TOTAL: Si una fecha o cifra no está escrita en las fuentes, no la menciones.
                {f"4. CORRECCIONES APRENDIDAS DEL USUARIO:{chr(10)}{reglas_extra}" if reglas_extra else ""}

                FUENTES EXTERNAS:
                {contexto_web}

                CONSULTA: {pregunta}
                """
                borrador = llamar_gemini(prompt_borrador)
                
                estado.write("4/4 Auditando el borrador para eliminar relleno o datos no verificados...")
                prompt_auditor = f"""
                Actúa como un auditor editorial estricto. Compara el BORRADOR contra las FUENTES EXTERNAS originales.
                
                Tu única tarea es limpiar el borrador:
                - ELIMINA cualquier frase de relleno, opinión general o dato que no esté respaldado textualmente por las fuentes.
                - VERIFICA que cada afirmación tenga su enlace Markdown incrustado correctamente dentro del texto.
                - Si todo es preciso y directo, devuelve el texto limpio listo para el usuario (sin agregar comentarios tuyos como "Aquí está el texto revisado").

                FUENTES EXTERNAS:
                {contexto_web}

                BORRADOR A AUDITAR:
                {borrador}
                """
                reporte_final = llamar_gemini(prompt_auditor)
                
                estado.update(label="¡Reporte auditado y verificado!", state="complete", expanded=False)
                st.session_state.ultimo_reporte = reporte_final
                st.markdown(reporte_final)
                
        except Exception as e:
            estado.update(label="Se detuvo la búsqueda", state="error")
            st.error(f"Ocurrió un error: {e}")

# Módulo de aprendizaje continuo en vivo
if "ultimo_reporte" in st.session_state:
    st.divider()
    with st.expander("🧠 ¿Notaste algún error o relleno? Enséñale al agente para futuras búsquedas"):
        correccion = st.text_input("Escribe qué debe corregir o evitar (ej. 'No incluyas directorios empresariales como ZoomInfo' o 'Sé más directo en las citas'):")
        if st.button("Guardar aprendizaje"):
            if correccion.strip():
                st.session_state.reglas_aprendidas.append(correccion.strip())
                st.success("¡Aprendido! El agente aplicará esta regla en las próximas consultas.")
