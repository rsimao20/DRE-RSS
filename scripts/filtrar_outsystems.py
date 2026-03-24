import feedparser
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

RSS_URL = "https://files.diariodarepublica.pt/rss/serie2&parte=l-html.xml"
KEYWORDS = ["outsystems", "OutSystems", "out systems"]

resultados = []

print(f"🔍 A pesquisar concursos com OutSystems no DRE...")
feed = feedparser.parse(RSS_URL)
print(f"📋 Total de anúncios encontrados: {len(feed.entries)}")

for entry in feed.entries:
    texto_completo = (entry.get('title', '') + ' ' + entry.get('summary', '')).lower()
    
    if any(kw.lower() in texto_completo for kw in KEYWORDS):
        resultado = {
            "titulo": entry.get('title', ''),
            "link": entry.get('link', ''),
            "data": entry.get('published', ''),
            "resumo": entry.get('summary', '')
        }
        resultados.append(resultado)
        print(f"✅ MATCH: {entry.get('title', '')}")
        print(f"   🔗 {entry.get('link', '')}")
        print()

print(f"\n📊 Total de concursos OutSystems encontrados: {len(resultados)}")

# Guardar resultados em JSON
with open('data/outsystems_resultados.json', 'w', encoding='utf-8') as f:
    json.dump({
        "data_pesquisa": datetime.now().isoformat(),
        "total": len(resultados),
        "resultados": resultados
    }, f, ensure_ascii=False, indent=2)

print("💾 Resultados guardados em data/outsystems_resultados.json")
