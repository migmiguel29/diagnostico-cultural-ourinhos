"""Verificações de formato, integridade e minimização de dados (sem API de rede)."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
e=pd.read_csv(ROOT/'data'/'escolas.csv')
a=pd.read_csv(ROOT/'data'/'agentes.csv')
assert len(e)==31, f'{len(e)} escolas em vez de 31'
assert len(a)==7, f'{len(a)} iniciativas em vez de 7'
assert e['id'].is_unique and a['id'].is_unique
assert int(e['espaco_leitura'].isin(['Biblioteca','Sala de Leitura']).sum())==22
assert int(e['projetos_leitura'].eq('Sim').sum())==28
assert int(e['acessibilidade_inclusao'].eq('Sim').sum())==26
assert int(a['integrar_forum'].eq('Sim').sum())==6
for df in [e,a]:
    for col in df.columns:
        assert all(x not in col.lower() for x in ['telefone','email','e-mail','responsavel','responsável','endereco','endereço','observacao','observação','cep','rua','nome_do_responsavel']), col
assert e['latitude'].notna().sum()==0, 'As coordenadas devem ser geocodificadas, não inventadas'
print('Verificações concluídas: base minimizada e indicadores coerentes.')
