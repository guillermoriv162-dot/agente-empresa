import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types
from tavily import TavilyClient

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

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
    1. Resumen Ejecutivo (Los 3 movimientos más relevantes de la semana).
    2. Regulación, CENACE y Tarifas Eléctricas (Cambios normativos, precios marginales, capacidad y transmisión).
    3. Generación, Transición Energética y Nearshoring (Demanda industrial y proyectos renovables).
    4. Menciones del Sector y Acclaim Energy (Actividad pública y contexto competitivo).

    REGLAS:
    - Incrusta los enlaces [Nombre del Medio](URL) directamente dentro de cada párrafo.
    - Usa voz activa, tono ejecutivo y datos precisos. Prohibido inventar cifras o fechas.

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
    raise RuntimeError("No se pudo generar el reporte con los modelos disponibles.")

def enviar_correo(contenido, fecha):
    remitente = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    destinatario = os.environ["CORREO_DESTINO"] # Tu correo de Microsoft 365 / Outlook del trabajo

    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = f"REPORTE-MERCADO-ELECTRICO Semana {fecha}"

    msg.attach(MIMEText(contenido, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp." + "gmail.com", 465) as server:
        server.login(remitente, password)
        server.send_message(msg)

if __name__ == "__main__":
    texto_reporte, fecha = generar_reporte()
    enviar_correo(texto_reporte, fecha)
    print("Reporte semanal generado y enviado correctamente.")
