import os
import streamlit as st
from google import genai
from google.genai import types
from tavily import TavilyClient
from estilos import aplicar_identidad_acclaim, mostrar_logo_sidebar

@st.cache_resource
def iniciar_clientes():
    g_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options={'timeout': 25000})
    t_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    return g_client, t_client

client, tavily = iniciar_clientes()
EMPRESA = "Acclaim Energy"
VOCERA = "María José Treviño"
DOMINIOS_EXCLUIDOS = ["acclaimenergy.com", "acclaimenergy.com.mx", "://acclaimenergy.com", "://acclaimenergy.com.mx"]

st.set_page_config(page_title="Acclaim Energy IA Agent", layout="wide", initial_sidebar_state="expanded")
aplicar_identidad_acclaim()

if "reglas_aprendidas" not in st.session_state:
    st.session_state.reglas_aprendidas = []
if "consulta_rapida" not in st.session_state:
    st.session_state.consulta_rapida = ""

with st.sidebar:
    mostrar_logo_sidebar()
    st.divider()
    st.markdown("**Ficha de Monitoreo**")
    st.markdown(f'<div style="background-color:#F7F7F8;padding:0.9rem;border-radius:8px;border-left:3px solid #75787B;font-size:0.9rem;"><strong>Empresa:</strong> {EMPRESA}<br><strong>Vocera LATAM:</strong> {VOCERA}<br><strong>Fuentes:</strong> Medios y terceros</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Memoria y Aprendizaje**")
    if st.session_state.reglas_aprendidas:
        for i, regla in enumerate(st.session_state.reglas_aprendidas, 1):
            st.markdown(f"**{i}.** {regla}")
        if st.button("Limpiar reglas", use_container_width=True):
            st.session_state.reglas_aprendidas = []
            st.rerun()
    nueva_regla = st.text_area("Agregar instrucción:", placeholder="Ej. Excluir directorios como ZoomInfo.", height=85)
    if st.button("Guardar regla", use_container_width=True):
        if nueva_regla.strip():
            st.session_state.reglas_aprendidas.append(nueva_regla.strip())
            st.rerun()

st.markdown(f'<div class="banner-acclaim"><div><h1>Acclaim Energy IA Agent</h1><p>Monitoreo en medios externos sobre {EMPRESA} y {VOCERA}</p><div class="tagline-acclaim">innovation. expertise. results.</div></div></div>', unsafe_allow_html=True)

st.caption("Consultas rápidas sugeridas:")
c1, c2, c3 = st.columns(3)
if c1.button("Noticias recientes 2026", use_container_width=True):
    st.session_state.consulta_rapida = "Noticias recientes y menciones en prensa en 2026"
if c2.button("Entrevistas María José Treviño", use_container_width=True):
    st.session_state.consulta_rapida = "Entrevistas, columnas y participación en eventos de María José Treviño"
if c3.button("Análisis mercado energético", use_container_width=True):
    st.session_state.consulta_rapida = "Análisis y declaraciones sobre el mercado eléctrico y energético en Latinoamérica"

pregunta = st.text_input("Consulta personalizada:", value=st.session_state.consulta_rapida, placeholder="Escribe el tema o noticia que deseas investigar...")

def llamar_gemini(prompt_texto):
    for modelo in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]:
        try:
            resp = client.models.generate_content(model=modelo, contents=prompt_texto, config=types.GenerateContentConfig(temperature=0.2))
            return resp.text
        except Exception as err:
            ultimo = err
    raise ultimo

if st.button("Investigar ahora", type="primary"):
    if not pregunta.strip():
        st.warning("Por favor escribe una consulta o selecciona una opción rápida.")
    else:
        estado = st.status("Rastreando fuentes externas...", expanded=True)
        try:
            reglas = st.session_state.reglas_aprendidas
            filtro_extra = " ".join(reglas) if reglas else ""
            estado.write("1/3 Analizando prensa externa sobre la empresa...")
            res_emp = tavily.search(query=f"{EMPRESA} Mexico Latinoamerica {pregunta} {filtro_extra}", search_depth="advanced", max_results=6, exclude_domains=DOMINIOS_EXCLUIDOS)
            estado.write("2/3 Buscando intervenciones de María José Treviño...")
            res_voc = tavily.search(query=f"{VOCERA} Acclaim Energy {pregunta} {filtro_extra}", search_depth="advanced", max_results=5, exclude_domains=DOMINIOS_EXCLUIDOS)
            
            vistas, limpias = set(), []
            for r in res_emp['results'] + res_voc['results']:
                if r['url'] not in vistas and r.get('score', 0) >= 0.25:
                    vistas.add(r['url'])
                    limpias.append(f"TÍTULO: {r['title']}\nURL: {r['url']}\nCONTENIDO: {r['content'][:1200]}")
            
            if not limpias:
                estado.update(label="Sin hallazgos relevantes", state="complete", expanded=False)
                st.info("No se encontraron artículos externos para esta búsqueda.")
            else:
                contexto = ("\n\n" + "=" * 20 + "\n\n").join(limpias)
                aprendizaje = ("\nREGLAS APRENDIDAS OBLIGATORIAS:\n" + "\n".join(f"- {r}" for r in reglas)) if reglas else ""
                estado.write("3/3 Estructurando reporte ejecutivo...")
                prompt = f"Eres analista senior de inteligencia corporativa para {EMPRESA} y {VOCERA}. Redacta un reporte COMPLETO y DETALLADO basado solo en estas fuentes externas.{aprendizaje}\nREGLAS: 1) Incrusta cada enlace Markdown [Nombre del Medio](URL) directamente dentro del párrafo donde lo citas (no hagas lista al final). 2) Usa voz activa, oraciones claras y desarrolla el contexto energético de cada nota. 3) No inventes datos.\nFUENTES:\n{contexto}\nCONSULTA: {pregunta}"
                reporte = llamar_gemini(prompt)
                estado.update(label="Reporte listo", state="complete", expanded=False)
                st.markdown(f'<div class="tarjeta-reporte">{reporte}</div>', unsafe_allow_html=True)
                st.download_button("Descargar reporte (.md)", data=reporte, file_name="reporte_acclaim_energy.md", mime="text/markdown")
        except Exception as e:
            estado.update(label="Error en la búsqueda", state="error")
            st.error(f"Ocurrió un error: {e}")
