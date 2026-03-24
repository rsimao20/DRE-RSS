import requests
import json
import os
import re
from datetime import datetime

KEYWORDS = ["outsystems", "low-code", "low code", "uipath"]

ENDPOINT = "https://diariodarepublica.pt/dr/screenservices/dr/Pesquisas/PesquisaResultado/DataActionGetPesquisas"

HEADERS_GET = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
HEADERS_POST = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def get_version_info():
    # Obter moduleVersion
    r1 = requests.get("https://diariodarepublica.pt/dr/moduleservices/moduleversioninfo", params={str(int(__import__('time').time()*1000)): ""}, headers=HEADERS_GET, timeout=15)
    module_version = r1.json().get("versionToken", "")

    # Obter apiVersion a partir da página principal
    r2 = requests.get("https://diariodarepublica.pt/dr/pesquisa", headers=HEADERS_GET, timeout=15)
    match = re.search(r'moduleinfo\?([^"\']+)', r2.text)
    api_version = match.group(1) if match else module_version

    return {"moduleVersion": module_version, "apiVersion": api_version}

print("A obter versao do DRE...")
version_info = get_version_info()
print(f"moduleVersion: {version_info['moduleVersion'][:20]}...")

todos_resultados = []

for keyword in KEYWORDS:
    print(f"A pesquisar: '{keyword}'...")
    pagina = 1
    while True:
        payload = {
            "versionInfo": version_info,
            "viewName": "Pesquisas.PesquisaResultado",
            "screenData": {
                "variables": {
                    "FiltrosDePesquisa": {
                        "tipoConteudo": {"List": ["AtosSerie2"]},
                        "serie": {"List": ["II"]},
                        "parte": "L - Contratos públicos",
                        "texto": keyword,
                        "numero": "",
                        "ano": "0",
                        "suplemento": "0",
                        "dataPublicacao": "",
                        "dataPublicacaoDe": "1900-01-01",
                        "dataPublicacaoAte": "1900-01-01",
                        "apendice": "",
                        "fasciculo": "",
                        "tipo": {"List": [], "EmptyListItem": ""},
                        "emissor": {"List": [], "EmptyListItem": ""},
                        "sumario": "",
                        "entidadeProponente": {"List": [], "EmptyListItem": ""},
                        "numeroDR": "",
                        "paginaInicial": "0",
                        "paginaFinal": "0",
                        "dataAssinatura": "",
                        "dataDistribuicao": "",
                        "entidadePrincipal": {"List": [], "EmptyListItem": ""},
                        "entidadeEmitente": {"List": [], "EmptyListItem": ""},
                        "apenasEmVigor": True
                    },
                    "PaginaAtual": pagina,
                    "ItensPorPagina": 25,
                    "TipoOrdenacaoSelecionado": "MaisRecente"
                }
            }
        }

        resp = requests.post(ENDPOINT, headers=HEADERS_POST, json=payload, timeout=30)

        if resp.status_code != 200 or not resp.text.strip():
            print(f"  Erro: {resp.status_code}")
            break

        data = resp.json()
        resultados = data.get("data", {}).get("Resultados", {}).get("List", [])
        total = data.get("data", {}).get("TotalResultados", 0)

        if not resultados:
            print(f"  Nenhum resultado activo para '{keyword}'")
            break

        for r in resultados:
            todos_resultados.append({
                "keyword": keyword,
                "titulo": r.get("Titulo", ""),
                "sumario": r.get("Sumario", ""),
                "data_publicacao": r.get("DataPublicacao", ""),
                "link": "https://diariodarepublica.pt" + r.get("LinkDetalhe", ""),
                "emissor": r.get("Emissor", ""),
                "em_vigor": r.get("EmVigor", False)
            })

        print(f"  Pagina {pagina}: {len(resultados)} resultados (total: {total})")

        if pagina * 25 >= total:
            break
        pagina += 1

print(f"\nTotal encontrado: {len(todos_resultados)}")

os.makedirs("data", exist_ok=True)
with open("data/outsystems_resultados.json", "w", encoding="utf-8") as f:
    json.dump({
        "data_pesquisa": datetime.now().isoformat(),
        "total": len(todos_resultados),
        "resultados": todos_resultados
    }, f, ensure_ascii=False, indent=2)

print("Guardado em data/outsystems_resultados.json")