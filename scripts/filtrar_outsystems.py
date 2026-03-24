import feedparser
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

RSS_URL = "https://files.diariodarepublica.pt/rss/serie2&parte=l-html.xml"
KEYWORDS = ["mendix"]
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
    dados = {
        "data_pesquisa": datetime.now().isoformat(),
        "total": len(resultados),
        "resultados": resultados
    }
    json.dump(dados, f, ensure_ascii=False, indent=2)