import feedparser
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

RSS_URL = "https://files.diariodarepublica.pt/rss/serie2&parte=l-html.xml"
KEYWORDS = ["OutSystems", "outsystems", "low-code", "out systems", "UiPath", "uipath", "ui path"]

EMAIL_REMETENTE = "rodrigo.simao@fortrevo.com"
EMAIL_DESTINATARIOS = ["simao2002rodrigo@gmail.com", "olga.duarte@fortrevo.com", "sales@fortrevo.com"]
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

def enviar_email(resultados):
    if not GMAIL_APP_PASSWORD:
        print("AVISO: GMAIL_APP_PASSWORD nao esta definida. Email nao sera enviado.")
        return

    assunto = f"[DRE] {len(resultados)} concurso(s) novo(s) encontrado(s)"

    corpo_html = f"""
    <html>
    <body>
        <h2>Concursos Publicos Detetados no DRE</h2>
        <p>Foram encontrados <strong>{len(resultados)}</strong> concurso(s) relevante(s) hoje ({datetime.now().strftime('%d/%m/%Y')}):</p>
        <hr>
    """

    for i, c in enumerate(resultados, 1):
        corpo_html += f"""
        <h3>{i}. {c['titulo']}</h3>
        <p><strong>Data:</strong> {c['data']}</p>
        <p><strong>Link:</strong> <a href="{c['link']}">{c['link']}</a></p>
        <p><strong>Resumo:</strong> {c['resumo']}</p>
        <hr>
        """

    corpo_html += """
        <p>Para obter o resumo do caderno de encargos, descarrega o PDF da plataforma e envia-o ao agente UiPath.</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = ", ".join(EMAIL_DESTINATARIOS)
    msg.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMETENTE, GMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIOS, msg.as_string())
        print(f"Email enviado para: {', '.join(EMAIL_DESTINATARIOS)}")
    except Exception as e:
        print(f"ERRO ao enviar email: {e}")

resultados = []

print("A pesquisar concursos com OutSystems no DRE...")
feed = feedparser.parse(RSS_URL)
print(f"Total de anuncios no RSS: {len(feed.entries)}")

for entry in feed.entries:
    titulo = entry.get('title', '')
    link = entry.get('link', '')
    resumo = entry.get('summary', '')
    texto = (titulo + ' ' + resumo).lower()
    encontrou = any(kw.lower() in texto for kw in KEYWORDS)
    if not encontrou and link:
        resp = requests.get(link, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        texto_pagina = BeautifulSoup(resp.text, 'html.parser').get_text().lower()
        encontrou = any(kw.lower() in texto_pagina for kw in KEYWORDS)
    if encontrou:
        resultados.append({"titulo": titulo, "link": link, "data": entry.get('published', ''), "resumo": resumo})
        print(f"MATCH: {titulo}")
        print(f"  {link}")

print(f"\nTotal encontrado: {len(resultados)}")
os.makedirs('data', exist_ok=True)
with open('data/outsystems_resultados.json', 'w', encoding='utf-8') as f:
    json.dump({"data_pesquisa": datetime.now().isoformat(), "total": len(resultados), "resultados": resultados}, f, ensure_ascii=False, indent=2)
print("Resultados guardados em data/outsystems_resultados.json")

if resultados:
    print(f"\n{len(resultados)} concurso(s) encontrado(s) - a enviar email...")
    enviar_email(resultados)
    print("Concluido.")
else:
    print("\nNenhum concurso encontrado. Nenhum email enviado.")