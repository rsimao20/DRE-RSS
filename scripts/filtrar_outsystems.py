import requests
import json
import os
from datetime import datetime

KEYWORDS = ["outsystems", "low-code", "low code", "uipath"]

ENDPOINT = "https://diariodarepublica.pt/dr/screenservices/dr/Pesquisas/PesquisaResultado/DataActionGetPesquisas"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

todos_resultados = []

for keyword in KEYWORDS:
    print(f"A pesquisar: '{keyword}'...")
    pagina = 1
    while True:
        payload = {
            "versionInfo": {
                "moduleVersion": "E5y+zrHdOkI5dvEiHpFZsw",
                "apiVersion": "6Bnghy+TVcnOZSN2FpzXbQ"
            },
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
        data = resp.json()

        resultados = data.get("data", {}).get("Resultados", {}).get("List", [])
        total = data.get("data", {}).get("TotalResultados", 0)

        if not resultados:
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

        print(f"  Página {pagina}: {len(resultados)} resultados (total: {total})")

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