import feedparser
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

RSS_URL = "https://files.diariodarepublica.pt/rss/serie2&parte=l-html.xml"
KEYWORDS = ["outsystems", "out systems", "low-code outsystems"]

resultados = []

print("A pesquisar concursos com OutSystems no DRE...")
feed = feedparser.parse(RSS_URL)
print(f"Total de anuncios no RSS: {len(feed.entries)}")

for i, entry in enumerate(feed.entries):
        titulo = entry.get('title', '')
        link = entry.get('link', '')
        data_pub = entry.get('published', '')
        resumo = entry.get('summary', '')

    # Verificar primeiro no titulo e resumo (rapido)
        texto_basico = (titulo + ' ' + resumo).lower()
        encontrado = any(kw.lower() in texto_basico for kw in KEYWORDS)

    # Se nao encontrou, vai buscar o texto completo da pagina HTML
        if not encontrado and link:
                    try:
                                    time.sleep(0.5)  # respeitar o servidor
            resp = requests.get(link, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                                soup = BeautifulSoup(resp.text, 'html.parser')
                                texto_pagina = soup.get_text().lower()
                                encontrado = any(kw.lower() in texto_pagina for kw in KEYWORDS)
except Exception as e:
            print(f"  Erro ao aceder {link}: {e}")

    if encontrado:
                resultado = {
                                "titulo": titulo,
                                "link": link,
                                "data": data_pub,
                                "resumo": resumo
                }
                resultados.append(resultado)
                print(f"MATCH: {titulo}")
                print(f"  {link}")

    # Progresso a cada 10 anuncios
    if (i + 1) % 10 == 0:
                print(f"  ...verificados {i+1}/{len(feed.entries)}")

print(f"\nTotal de concursos OutSystems encontrados: {len(resultados)}")

# Garantir que a pasta data existe
os.makedirs('data', exist_ok=True)

# Guardar resultados em JSON
output = {
        "data_pesquisa": datetime.now().isoformat(),
        "total": len(resultados),
        "resultados": resultados
}

with open('data/outsystems_resultados.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

print("Resultados guardados em data/outsystems_resultados.json")

# Mostrar resumo final
if resultados:
        print("\n=== CONCURSOS ENCONTRADOS ===")
    for r in resultados:
                print(f"- {r['titulo']}")
                print(f"  {r['link']}")
else:
    print("\nNenhum concurso com OutSystems encontrado hoje.")
