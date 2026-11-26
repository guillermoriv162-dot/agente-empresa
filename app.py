import os
import streamlit as st
from google import genai
from google.genai import types
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

st.set_page_config(page_title="Acclaim Energy IA Agent", layout="wide")
st.title("Acclaim Energy IA Agent")
st.write(f"Monitoreo en medios externos sobre **{EMPRESA}** y **{VOCERA}**.")

# Memoria persistente en la sesión para reglas aprendidas
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
                config=types.GenerateContentConfig(temperature=0.2)
            )
            return resp.text
        except Exception as err:
            ultimo_error = err
            continue
    raise ultimo_error

def optimizar_busqueda_con_aprendizaje(consulta_base, reglas):
    if not reglas:
        return consulta_base
    # Traduce las correcciones del usuario en filtros reales para el motor de búsqueda
    prompt_query = f"""
    Convierte esta búsqueda y las reglas del usuario en una consulta corta para buscador web (máximo 15 palabras, sin comillas innecesarias, usando -palabra si el usuario pidió excluir algún sitio o tema).
    Búsqueda base: {consulta_base}
    Reglas aprendidas: {"; ".join(reglas)}
    Devuelve ÚNICAMENTE la consulta final.
    """
    try:
        return llamar_gemini(prompt_query).strip()
    except Exception:
        return consulta_base

if st.button("Investigar", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta primero.")
    else:
        estado = st.status("Iniciando investigación en medios externos...", expanded=True)
        try:
            reglas = st.session_state.reglas_aprendidas
            
            estado.write("1/3 Buscando menciones de Acclaim Energy en prensa externa...")
            q_empresa = optimizar_busqueda_con_aprendizaje(f"{EMPRESA} Mexico Latinoamerica {pregunta}", reglas)
            res_empresa = tavily.search(
                query=q_empresa,
                search_depth="advanced",
                max_results=6,
                exclude_domains=DOMINIOS_EXCLUIDOS
            )
            
            estado.write("2/3 Buscando entrevistas y participación de María José Treviño...")
            q_vocera = optimizar_busqueda_con_aprendizaje(f"{VOCERA} Acclaim Energy {pregunta}", reglas)
            res_vocera = tavily.search(
                query=q_vocera,
                search_depth="advanced",
                max_results=5,
                exclude_domains=DOMINIOS_EXCLUIDOS
            )
            
            urls_vistas = set()
            fuentes_limpias = []
            for r in res_empresa['results'] + res_vocera['results']:
                if r['url'] not in urls_vistas and r.get('score', 0) >= 0.25:
                    urls_vistas.add(r['url'])
                    fuentes_limpias.append(f"TÍTULO: {r['title']}\nURL: {r['url']}\nCONTENIDO: {r['content'][:1200]}")
            
            if not fuentes_limpias:
                estado.update(label="Sin resultados encontrados", state="complete", expanded=False)
                st.info("No se encontraron artículos externos para esta búsqueda. Prueba con palabras más generales.")
            else:
                contexto_web = "\n\n---\n\n".join(fuentes_limpias)
                bloque_aprendizaje = ""
                if reglas:
                    lista_reglas = "\n".join([f"- OBLIGATORIO: {r}" for r in reglas])
                    bloque_aprendizaje = f"\nINSTRUCCIONES APRENDIDAS DE FEEDBACK ANTERIOR (APLICAR CON MÁXIMA PRIORIDAD):\n{lista_reglas}\n"
                
                estado.write("3/3 Redactando reporte detallado...")
                prompt_final = f"""
                Eres un analista senior de inteligencia corporativa y relaciones públicas especializado en {EMPRESA} y {VOCERA}.
                Redacta un reporte COMPLETO, DETALLADO y bien estructurado basado en las fuentes externas proporcionadas abajo.
                {bloque_aprendizaje}
                REGLAS DE REDACCIÓN:
                1. ENLACES INCRUSTADOS EN EL TEXTO: NO pongas una lista de fuentes al final. Incrusta cada enlace Markdown [Nombre del Medio o Artículo](URL) directamente dentro del párrafo o viñeta donde mencionas cada noticia o declaración.
                2. DESARROLLO AMPLIO: Explica con claridad el contexto de cada nota, qué tema energético o corporativo aborda y cuál fue la participación de {EMPRESA} o {VOCERA}.
                3. RIGOR: No inventes fechas ni cifras que no aparezcan en las fuentes.

                FUENTES EXTERNAS RECOPILADAS:
                {contexto_web}

                CONSULTA DEL USUARIO: {pregunta}
                """
                
                reporte = llamar_gemini(prompt_final)
                estado.update(label="¡Investigación completada!", state="complete", expanded=False)
                st.session_state.ultimo_reporte = reporte
                st.markdown(reporte)
                
        except Exception as e:
            estado.update(label="Se detuvo la búsqueda", state="error")
            st.error(f"Ocurrió un error: {e}")

# Módulo de memoria y aprendizaje activo
st.divider()
with st.expander("Memoria y aprendizaje del agente (Reglas activas)", expanded=bool(st.session_state.reglas_aprendidas)):
    if st.session_state.reglas_aprendidas:
        st.write("**El agente está aplicando estas correcciones en sus búsquedas:**")
        for i, regla in enumerate(st.session_state.reglas_aprendidas, 1):
            st.write(f"{i}. {regla}")
        if st.button("Borrar reglas aprendidas"):
            st.session_state.reglas_aprendidas = []
            st.rerun()
    else:
        st.caption("Aún no has agregado correcciones. Escribe abajo cualquier ajuste que quieras que el agente aplique en las siguientes consultas.")
        
    nueva_regla = st.text_input("Enséñale algo nuevo para las próximas búsquedas:", placeholder="Ej. No incluyas resultados de LinkedIn ni directorios, enfócate en noticias de energía en México")
    if st.button("Guardar aprendizaje"):
        if nueva_regla.strip():
            st.session_state.reglas_aprendidas.append(nueva_regla.strip())
            st.success("¡Regla guardada! Se aplicará automáticamente en la siguiente búsqueda.")
            st.rerun()
