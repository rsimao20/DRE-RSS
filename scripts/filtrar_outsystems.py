import requests
import json
import os
from datetime import datetime
import re

KEYWORDS = ["outsystems", "low-code", "low code", "uipath"]

ENDPOINT = "https://diariodarepublica.pt/dr/screenservices/dr/Pesquisas/PesquisaResultado/DataActionGetPesquisas"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_version_info():
    """Busca o moduleVersion e apiVersion actuais do site do DRE"""
    resp = requests.get("https://diariodarepublica.pt/dr/pesquisa", headers={"User-Agent": HEADERS["User-Agent"]})
    module = re.search(r'"moduleVersion":"([^"]+)"', resp.text)
    api = re.search(r'"apiVersion":"([^"]+)"', resp.text)
    if module and api:
        return {"moduleVersion": module.group(1), "apiVersion": api.group(1)}
    return {"moduleVersion": "", "apiVersion": ""}

print("A obter versao do DRE...")
version_info = get_version_info()
print(f"moduleVersion: {version_info['moduleVersion']}")

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

        resp = requests.post(ENDPOINT, headers=HEADERS, json=payload, timeout=30)
        
        if resp.status_code != 200 or not resp.text.strip():
            print(f"  Erro na resposta: {resp.status_code}")
            break

        data = resp.json()
        resultados = data.get("data", {}).get("Resultados", {}).get("List", [])
        total = data.get("data", {}).get("TotalResultados", 0)

        if not resultados:
            print(f"  Nenhum resultado para '{keyword}'")
            break

        for r in resultados:
            todos_resultados.append({
                "keyword": keyword,
                "titulo": r.get("Titulo", ""),
                "sumario": r.get("Sumario", ""),
                "data_publicacao": r.get("DataPublicacao", ""),
                "link": r.get("LinkDetalhe", ""),
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