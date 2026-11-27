import os
import re
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google import genai
from google.genai import types
from tavily import TavilyClient
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

ROJO_ACCLAIM = RGBColor(191, 13, 62)   # Pantone 193 (#BF0D3E)
GRIS_ACCLAIM = RGBColor(117, 120, 123) # Cool Gray 9 (#75787B)
TEXTO_OSCURO = RGBColor(51, 55, 59)

def generar_reporte():
    temas = [
        "mercado electrico mayorista Mexico CENACE CRE noticias semana",
        "tarifas electricas CFE industria energia renovable Mexico Latinoamerica",
        "Acclaim Energy Maria Jose Treviño mercado energetico noticias"
    ]
    vistas, fuentes = set(), []
    for consulta in temas:
        res = tavily.search(query=consulta, search_depth="advanced", max_results=5, days=7)
        for r in res['results']:
            if r['url'] not in vistas:
                vistas.add(r['url'])
                fuentes.append(f"TÍTULO: {r['title']}\nURL: {r['url']}\nCONTENIDO: {r['content'][:1200]}")

    contexto = ("\n\n" + "=" * 20 + "\n\n").join(fuentes)
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
    Eres un analista senior de inteligencia energética para Acclaim Energy.
    Redacta un REPORTE SEMANAL EXHAUSTIVO Y EJECUTIVO del mercado eléctrico en México y Latinoamérica (Semana del {fecha_hoy}) basado EXCLUSIVAMENTE en las fuentes recopiladas abajo.

    ESTRUCTURA OBLIGATORIA:
    ## 1. Resumen Ejecutivo
    ## 2. Regulación, CENACE y Tarifas Eléctricas
    ## 3. Generación, Transición Energética y Nearshoring
    ## 4. Menciones del Sector y Acclaim Energy

    REGLAS DE FORMATO:
    - Usa ## para los 4 títulos principales.
    - Usa **negritas** para resaltar conceptos clave al inicio de cada viñeta o párrafo.
    - Escribe los enlaces en formato legible: Nombre del Medio (URL).
    - Prohibido inventar cifras o fechas que no estén en las fuentes.

    FUENTES DE LOS ÚLTIMOS 7 DÍAS:
    {contexto}
    """

    for modelo in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]:
        try:
            resp = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2)
            )
            return resp.text, fecha_hoy
        except Exception:
            continue
    raise RuntimeError("No se pudo generar el reporte.")

def agregar_texto_formateado(parrafo, texto):
    # Convierte **negritas** de Markdown en negritas reales de Word
    partes = re.split(r'(\*\*.*?\*\*)', texto)
    for parte in partes:
        if parte.startswith('**') and parte.endswith('**'):
            run = parrafo.add_run(parte[2:-2])
            run.bold = True
            run.font.color.rgb = TEXTO_OSCURO
        else:
            run = parrafo.add_run(parte)
            run.font.color.rgb = TEXTO_OSCURO

def crear_word_institucional(contenido, fecha):
    doc = Document()
    estilo_normal = doc.styles['Normal']
    estilo_normal.font.name = 'Calibri'
    estilo_normal.font.size = Pt(11)

    # --- ENCABEZADO CON LOGO ---
    seccion = doc.sections[0]
    header = seccion.header
    p_head = header.paragraphs[0]
    p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists("logo.png"):
        p_head.add_run().add_picture("logo.png", width=Inches(1.6))
    elif os.path.exists("logo.jpg"):
        p_head.add_run().add_picture("logo.jpg", width=Inches(1.6))

    # --- PIE DE PÁGINA INSTITUCIONAL ---
    footer = seccion.footer
    p_foot = footer.paragraphs[0]
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_foot = p_foot.add_run("Acclaim Energy Advisors  |  innovation. expertise. results.  |  Reporte Confidencial de Inteligencia Energética")
    r_foot.font.size = Pt(8.5)
    r_foot.font.color.rgb = GRIS_ACCLAIM

    # --- PORTADA / TÍTULO DEL REPORTE ---
    p_titulo = doc.add_paragraph()
    r_tit = p_titulo.add_run("REPORTE SEMANAL DE INTELIGENCIA ENERGÉTICA")
    r_tit.bold = True
    r_tit.font.size = Pt(18)
    r_tit.font.color.rgb = ROJO_ACCLAIM

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run(f"Mercado Eléctrico en México y Latinoamérica  •  Semana del {fecha}")
    r_sub.bold = True
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = GRIS_ACCLAIM

    # Línea divisoria roja institucional
    p_linea = doc.add_paragraph()
    pPr = p_linea._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="1" w:color="BF0D3E"/></w:pBdr>')
    pPr.append(pBdr)

    # --- CONTENIDO DEL REPORTE ---
    for linea in contenido.split("\n"):
        linea = linea.strip()
        if not linea or linea == "---":
            continue
        if linea.startswith("## "):
            p_h = doc.add_paragraph()
            p_h.paragraph_format.space_before = Pt(14)
            p_h.paragraph_format.space_after = Pt(4)
            r_h = p_h.add_run(linea.replace("## ", "").strip())
            r_h.bold = True
            r_h.font.size = Pt(13)
            r_h.font.color.rgb = ROJO_ACCLAIM
        elif linea.startswith("# "):
            continue
        elif linea.startswith("- ") or linea.startswith("* "):
            p_b = doc.add_paragraph(style='List Bullet')
            agregar_texto_formateado(p_b, linea[2:].strip())
        else:
            p_txt = doc.add_paragraph()
            p_txt.paragraph_format.space_after = Pt(6)
            agregar_texto_formateado(p_txt, linea)

    nombre_archivo = f"Reporte_Mercado_Electrico_{fecha}.docx"
    doc.save(nombre_archivo)
    return nombre_archivo

def enviar_correo(archivo_docx, fecha):
    msg = MIMEMultipart()
    msg["From"] = os.environ["GMAIL_USER"]
    msg["To"] = os.environ["CORREO_DESTINO"]
    msg["Subject"] = f"REPORTE-MERCADO-ELECTRICO Semana {fecha}"

    cuerpo = f"Adjunto se encuentra el Reporte Semanal de Inteligencia Energética correspondiente a la semana del {fecha}."
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    with open(archivo_docx, "rb") as f:
        adjunto = MIMEApplication(f.read(), _subtype="vnd.openxmlformats-officedocument.wordprocessingml.document")
        adjunto.add_header("Content-Disposition", "attachment", filename=archivo_docx)
        msg.attach(adjunto)

    with smtplib.SMTP_SSL("smtp." + "gmail.com", 465) as server:
        server.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"])
        server.send_message(msg)

if __name__ == "__main__":
    texto_reporte, fecha = generar_reporte()
    nombre_word = crear_word_institucional(texto_reporte, fecha)
    enviar_correo(nombre_word, fecha)
    print("Reporte Word generado y enviado correctamente.")
