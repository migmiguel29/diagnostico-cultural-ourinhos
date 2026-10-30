"""Gera bases institucionais minimizadas sem contatos, nomes de responsáveis ou textos livres.
Uso: python scripts/preparar_dados.py --escolas /caminho/escolas.zip --agentes /caminho/agentes.zip
"""
import argparse
import hashlib
import io
import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]


def ler_csv(arquivo: str | Path) -> pd.DataFrame:
    arquivo = Path(arquivo)
    if arquivo.suffix.lower() == '.zip':
        with zipfile.ZipFile(arquivo) as z:
            nomes = [n for n in z.namelist() if n.lower().endswith('.csv') and not n.startswith('__MACOSX')]
            if len(nomes) != 1:
                raise ValueError('O ZIP deve conter exatamente um CSV.')
            conteudo = z.read(nomes[0])
            df = pd.read_csv(io.BytesIO(conteudo), dtype=str)
    else:
        df = pd.read_csv(arquivo, dtype=str)
    return df.fillna('').astype(str)


def valor(df: pd.DataFrame, indice: int) -> pd.Series:
    return df.iloc[:, indice].fillna('').astype(str).str.strip()


def limpa(s: str) -> str:
    return ' '.join(str(s).strip().split())


def normaliza(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', limpa(s)) if not unicodedata.combining(c)).casefold()


def bairro_canonico(valor_bairro: str) -> str:
    """Agrupa variantes óbvias de grafia; sem inferir mudanças de bairro."""
    chave = normaliza(valor_bairro).strip(' .')
    equivalencias = {
        'cohab': 'COHAB',
        'cdhu': 'CDHU',
        'faz santa maria': 'Fazenda Santa Maria',
        'fazenda santa maria': 'Fazenda Santa Maria',
        'vila moraes': 'Vila Moraes',
    }
    return equivalencias.get(chave, limpa(valor_bairro).title())


def id_curto(prefixo: str, *partes: str) -> str:
    chave = '¦'.join(normaliza(p) for p in partes)
    return prefixo + '-' + hashlib.sha256(chave.encode('utf-8')).hexdigest()[:10]


def preparar_escolas(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] < 42 or 'Segmento' not in df.columns[8]:
        raise ValueError('Arquivo de escolas não reconhecido: esperado exportação do formulário escolar de 42 colunas.')
    out = pd.DataFrame(index=df.index)
    out['id'] = [id_curto('ESC', nome, rua, numero, cep) for nome, rua, numero, cep in zip(valor(df, 1), valor(df, 2), valor(df, 3), valor(df, 5))]
    out['unidade'] = [f'Escola {i:02d}' for i in range(1, len(df) + 1)]
    out['segmento'] = valor(df, 8).str.upper()
    out['bairro'] = valor(df, 4).apply(bairro_canonico)
    out['bairro_chave'] = out['bairro'].apply(normaliza)
    out['espaco_leitura'] = valor(df, 14)
    out['acervo'] = valor(df, 16)
    out['renovacao_acervo'] = valor(df, 17)
    out['acervo_virtual'] = valor(df, 19)
    out['emprestimos'] = valor(df, 21)
    out['infraestrutura_nota'] = pd.to_numeric(valor(df, 22), errors='coerce')
    for j, col in [(23, 'iluminacao'), (24, 'climatizacao'), (25, 'mobiliario'), (26, 'estrutura_predial')]:
        out[col] = valor(df, j)
    out['projetos_leitura'] = valor(df, 28)
    out['acessibilidade_inclusao'] = valor(df, 31)
    out['acess_arquitetonica'] = valor(df, 32)
    out['acess_visual'] = valor(df, 33)
    out['acess_auditiva'] = valor(df, 34)
    out['acess_cognitiva'] = valor(df, 35)
    out['acess_tecnologica'] = valor(df, 36)
    out['acess_pedagogica'] = valor(df, 37)
    out['acess_atitudinal'] = valor(df, 38)
    out['programas_inclusao'] = valor(df, 39)
    # A localização somente é preenchida por geocodificação validada, nunca por coordenadas fictícias.
    out['latitude'] = float('nan')
    out['longitude'] = float('nan')
    out['precisao_geografica'] = ''
    return out.reset_index(drop=True)


def preparar_agentes(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] < 44 or 'Nome da instituição' not in df.columns[1]:
        raise ValueError('Arquivo de agentes culturais não reconhecido: esperado 44 colunas.')
    out = pd.DataFrame(index=df.index)
    out['id'] = [id_curto('AGE', nome) for nome in valor(df, 1)]
    out['iniciativa'] = [f'Iniciativa {i:02d}' for i in range(1, len(df) + 1)]
    # "Bairros de atuação" pode ser "Toda a cidade" e NÃO é um endereço geocodificável.
    out['abrangencia_declarada'] = valor(df, 6)
    out['cnpj'] = valor(df, 8)
    out['perfil'] = valor(df, 9)
    out['tempo_atividade'] = valor(df, 10)
    out['areas_atuacao'] = valor(df, 11)
    out['publicos_atendidos'] = valor(df, 12)
    out['pessoas_ano_faixa'] = valor(df, 13)
    out['acoes'] = valor(df, 14)
    out['frequencia'] = valor(df, 15)
    out['acoes_inclusao'] = valor(df, 16)
    out['recursos_acessibilidade'] = valor(df, 17)
    out['infraestrutura'] = valor(df, 18)
    out['acervo_livros'] = valor(df, 19)
    out['fomento'] = valor(df, 20)
    for j, label in [(21,'recursos_financeiros'),(22,'espaco_fisico'),(23,'aquisicao_livros'),(24,'equipamentos'),(25,'formacao_profissionais'),(26,'divulgacao'),(27,'participacao_publico'),(28,'acessibilidade'),(29,'captacao_recursos'),(30,'parcerias')]:
        out['desafio_'+label] = valor(df, j)
    for j,label in [(31,'acesso_livro'),(32,'incentivo_leitura'),(33,'programacao_literaria'),(34,'autores_locais'),(35,'mediadores'),(36,'bibliotecas'),(37,'acessibilidade_cultural'),(38,'politicas_publicas')]:
        out['avaliacao_'+label] = valor(df, j)
    out['eixos_prioritarios'] = valor(df, 39)
    out['participar_plano'] = valor(df, 40)
    out['integrar_forum'] = valor(df, 41)
    return out.reset_index(drop=True)


def preparar(arquivo_escolas: str, arquivo_agentes: str, pasta_saida: Path = BASE / 'data', preservar_geo: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    escolas = preparar_escolas(ler_csv(arquivo_escolas))
    agentes = preparar_agentes(ler_csv(arquivo_agentes))
    pasta_saida.mkdir(parents=True, exist_ok=True)
    arquivo_saida = pasta_saida / 'escolas.csv'
    if preservar_geo and arquivo_saida.exists():
        anteriores = pd.read_csv(arquivo_saida, dtype={'id':str})
        keep = ['id','latitude','longitude','precisao_geografica']
        if set(keep).issubset(anteriores.columns):
            escolas = escolas.drop(columns=keep[1:]).merge(anteriores[keep].drop_duplicates('id'), on='id', how='left')
    escolas.to_csv(arquivo_saida, index=False, encoding='utf-8')
    agentes.to_csv(pasta_saida / 'agentes.csv', index=False, encoding='utf-8')
    return escolas, agentes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--escolas', required=True, help='CSV ou ZIP de respostas escolares (mantido fora do repositório)')
    parser.add_argument('--agentes', required=True, help='CSV ou ZIP de respostas das iniciativas (mantido fora do repositório)')
    parser.add_argument('--saida', default=str(BASE / 'data'))
    parser.add_argument('--descartar-coordenadas', action='store_true')
    args = parser.parse_args()
    e, a = preparar(args.escolas, args.agentes, Path(args.saida), not args.descartar_coordenadas)
    print(f'Gerados {len(e)} registros de escolas e {len(a)} iniciativas. Dados pessoais/endereços não exportados.')
