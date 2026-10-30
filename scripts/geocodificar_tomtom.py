"""Geocodifica endereços escolares com TomTom, sem salvar endereços privados.

Primeiro: python scripts/preparar_dados.py --escolas caminho.zip --agentes caminho.zip
Depois: TOMTOM_API_KEY=... python scripts/geocodificar_tomtom.py --escolas caminho.zip
Windows PowerShell: $env:TOMTOM_API_KEY='...'
"""
import argparse
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests

from preparar_dados import BASE, id_curto, ler_csv, valor

API = 'https://api.tomtom.com/search/2/geocode'
# Envelope geográfico amplo para rejeitar municípios muito distantes; NÃO equivale a verificação cartográfica.
BBOX = (-23.20, -22.75, -50.15, -49.65)  # min_lat, max_lat, min_lon, max_lon


def geocodificar(endereco: str, chave: str, session: requests.Session | None = None) -> dict:
    s = session or requests.Session()
    from urllib.parse import quote
    url = f'{API}/{quote(endereco, safe="")}.json'
    resposta = s.get(url, params={'key':chave, 'limit':3, 'countrySet':'BR', 'language':'pt-BR', 'lat':-22.979, 'lon':-49.871}, timeout=25)
    resposta.raise_for_status()
    resultados = resposta.json().get('results', [])
    for r in resultados:
        endereco_encontrado = r.get('address', {})
        municipio = str(endereco_encontrado.get('municipality', ''))
        pais = str(endereco_encontrado.get('countryCode', ''))
        # Importante: NÃO aceitar centroide do bairro, cidade ou rua como coordenada pontual do prédio.
        tipo = r.get('type', '')
        score = float((r.get('matchConfidence') or {}).get('score', 0))
        pos = r.get('position') or {}
        lat, lon = pos.get('lat'), pos.get('lon')
        if lat is None or lon is None:
            continue
        lat, lon = float(lat), float(lon)
        cidade_ok = 'ourinhos' in municipio.casefold()
        if (pais == 'BR' and cidade_ok and tipo in {'Point Address', 'Address Range'}
            and score >= 0.75 and BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lon <= BBOX[3]):
            return {'latitude':lat, 'longitude':lon, 'precisao_geografica':f'{tipo} (conf. {score:.2f})'}
    return {'latitude':float('nan'),'longitude':float('nan'),'precisao_geografica':'pendente de revisão manual'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--escolas', required=True, help='CSV ou ZIP original da pesquisa escolar; não publicar')
    p.add_argument('--saida', default=str(BASE / 'data' / 'escolas.csv'))
    p.add_argument('--intervalo', type=float, default=0.3)
    p.add_argument('--refazer', action='store_true', help='Geocodifica novamente entradas já verificadas')
    args = p.parse_args()
    chave = os.environ.get('TOMTOM_API_KEY','').strip()
    if not chave:
        raise SystemExit('Defina TOMTOM_API_KEY como variável de ambiente; não salve a chave no repositório.')
    bruto = ler_csv(args.escolas)
    publico = pd.read_csv(args.saida, dtype={'id':str})
    if not {'id','latitude','longitude','precisao_geografica'} <= set(publico.columns):
        raise SystemExit('Antes execute preparar_dados.py para criar data/escolas.csv.')
    publico['latitude'] = pd.to_numeric(publico['latitude'], errors='coerce')
    publico['longitude'] = pd.to_numeric(publico['longitude'], errors='coerce')
    indices = {ident:i for i,ident in enumerate(publico['id'])}
    conta = {'encontradas':0,'pendentes':0,'ignoradas':0,'erros':0}
    with requests.Session() as sess:
        for n in range(len(bruto)):
            nome, rua, numero, bairro, cep = [str(valor(bruto, idx).iloc[n]) for idx in [1,2,3,4,5]]
            ident = id_curto('ESC', nome, rua, numero, cep)
            idx = indices.get(ident)
            if idx is None:
                conta['erros'] += 1
                print(f'[{n+1}] ID não encontrado na base pública; regenere com preparar_dados.py')
                continue
            if not args.refazer and pd.notna(publico.at[idx,'latitude']) and pd.notna(publico.at[idx,'longitude']):
                conta['ignoradas'] += 1
                continue
            cep_limpo = re.sub(r'\D','',cep)
            # CEP é usado apenas na chamada externa; não é escrito na base pública.
            num = numero.strip()
            if num.upper() in {'', 'S/N', 'SN', 'S/Nº'}:
                # Endereço sem número não recebe coordenada de rua como escola.
                publico.at[idx,'precisao_geografica'] = 'sem número: revisão manual'
                conta['pendentes'] += 1
                continue
            consulta = f'{rua}, {num}, {bairro}, Ourinhos, SP, Brasil'
            if len(cep_limpo) == 8:
                consulta += f', CEP {cep_limpo}'
            try:
                res = geocodificar(consulta, chave, session=sess)
                for col, val in res.items():
                    publico.at[idx,col] = val
                if pd.notna(res['latitude']):
                    conta['encontradas'] += 1
                else:
                    conta['pendentes'] += 1
                print(f'[{n+1}/{len(bruto)}] {ident}: {res["precisao_geografica"]}')
            except requests.RequestException as exc:
                conta['erros'] += 1
                publico.at[idx,'precisao_geografica'] = 'erro API: revisar'
                print(f'[{n+1}/{len(bruto)}] {ident}: erro HTTP; {type(exc).__name__}')
            finally:
                # Salva progresso a cada linha para recuperação segura se a conexão falhar.
                publico.to_csv(args.saida, index=False, encoding='utf-8')
                time.sleep(max(0,args.intervalo))
    publico.to_csv(args.saida, index=False, encoding='utf-8')
    print('Resultado:', conta)
    print('Revise manualmente as coordenadas e a qualidade antes de publicar o repositório.')

if __name__ == '__main__':
    main()
