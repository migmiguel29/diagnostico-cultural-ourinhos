"""Geocodificação pontual online, com upload temporário e exportação minimizada."""
import hmac
import io
import re
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from geocodificar_tomtom import geocodificar
from preparar_dados import id_curto

st.set_page_config(page_title="Geocodificação TomTom | Ourinhos", page_icon="📍", layout="wide")
st.title("📍 Geocodificar escolas pela internet")
st.caption("Etapa administrativa: arquivo original não é salvo no GitHub nem nos arquivos da aplicação.")


def segredo(nome):
    try:
        return str(st.secrets.get(nome, "")).strip()
    except (FileNotFoundError, KeyError):
        return ""


senha_correta = segredo("GEOCODIFICADOR_SENHA")
chave = segredo("TOMTOM_API_KEY")
if not senha_correta:
    st.error("O administrador deve configurar GEOCODIFICADOR_SENHA nos Secrets do Streamlit.")
    st.stop()

if not st.session_state.get("geo_autorizado", False):
    senha = st.text_input("Senha administrativa", type="password")
    if st.button("Entrar", type="primary"):
        if hmac.compare_digest(senha, senha_correta):
            st.session_state["geo_autorizado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

if not chave:
    st.error("Configure TOMTOM_API_KEY nos Secrets da aplicação antes de geocodificar.")
    st.stop()

st.info(
    "Envie a exportação ORIGINAL das escolas (CSV ou ZIP com um CSV). "
    "O arquivo é processado em memória. Apenas ID pseudonimizado, latitude, longitude "
    "e qualidade da correspondência vão para o resultado. "
    "O arquivo original e a chave NÃO devem ser enviados ao GitHub."
)


def ler_upload(arquivo):
    dados = arquivo.getvalue()
    if len(dados) > 10_000_000:
        raise ValueError("Arquivo acima do limite permitido (10 MB).")
    if arquivo.name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            csvs = [
                x for x in z.infolist()
                if x.filename.lower().endswith(".csv")
                and not x.is_dir() and not x.filename.startswith("__MACOSX")
            ]
            if len(csvs) != 1 or csvs[0].file_size > 10_000_000:
                raise ValueError("O ZIP deve conter exatamente um CSV de até 10 MB.")
            dados = z.read(csvs[0])
    tabela = pd.read_csv(io.BytesIO(dados), dtype=str).fillna("")
    if tabela.shape[1] < 42 or "Segmento" not in str(tabela.columns[8]):
        raise ValueError("Arquivo não reconhecido: selecione a exportação das escolas, com 42 colunas.")
    return tabela


arquivo = st.file_uploader("Respostas escolares originais", type=["csv", "zip"])
if arquivo:
    try:
        bruto = ler_upload(arquivo)
    except (ValueError, UnicodeError, zipfile.BadZipFile, pd.errors.ParserError) as erro:
        st.error(f"Não foi possível ler a exportação: {erro}")
        st.stop()
    st.write(f"Registros recebidos: **{len(bruto)}**")
    st.warning(
        "O serviço TomTom receberá os endereços para localizar os imóveis. "
        "Confira a autorização de uso desses dados antes de continuar."
    )
    if st.button("Iniciar geocodificação TomTom", type="primary"):
        publico = pd.read_csv(ROOT / "data" / "escolas.csv", dtype={"id": str})
        if not {"id", "latitude", "longitude", "precisao_geografica"}.issubset(publico.columns):
            st.error("A base minimizada data/escolas.csv não tem as colunas esperadas.")
            st.stop()
        for coluna in ["latitude", "longitude"]:
            publico[coluna] = pd.to_numeric(publico[coluna], errors="coerce")
        posicoes = {ident: n for n, ident in enumerate(publico["id"])}
        contagem = {"encontradas": 0, "pendentes": 0, "ja_geocodificadas": 0, "sem_correspondencia_id": 0, "erros_api": 0}
        barra = st.progress(0)
        mensagem = st.empty()
        with requests.Session() as sess:
            for n in range(len(bruto)):
                nome, rua, numero, bairro, cep = [
                    str(bruto.iat[n, j]).strip() for j in (1, 2, 3, 4, 5)
                ]
                ident = id_curto("ESC", nome, rua, numero, cep)
                idx = posicoes.get(ident)
                if idx is None:
                    contagem["sem_correspondencia_id"] += 1
                elif pd.notna(publico.at[idx, "latitude"]) and pd.notna(publico.at[idx, "longitude"]):
                    contagem["ja_geocodificadas"] += 1
                elif numero.upper() in {"", "S/N", "SN", "S/Nº"}:
                    publico.at[idx, "precisao_geografica"] = "sem número: revisar manualmente"
                    contagem["pendentes"] += 1
                else:
                    consulta = f"{rua}, {numero}, {bairro}, Ourinhos, SP, Brasil"
                    cep_numeros = re.sub(r"\D", "", cep)
                    if len(cep_numeros) == 8:
                        consulta += f", CEP {cep_numeros}"
                    try:
                        resultado = geocodificar(consulta, chave, session=sess)
                        for coluna, valor in resultado.items():
                            publico.at[idx, coluna] = valor
                        if pd.notna(resultado["latitude"]):
                            contagem["encontradas"] += 1
                        else:
                            contagem["pendentes"] += 1
                    except requests.RequestException:
                        contagem["erros_api"] += 1
                        publico.at[idx, "precisao_geografica"] = "erro na API: revisar"
                    time.sleep(0.25)
                barra.progress((n + 1) / len(bruto))
                mensagem.caption(f"Processados {n + 1} de {len(bruto)} registros")
        st.session_state["geo_csv"] = publico.to_csv(index=False).encode("utf-8-sig")
        st.session_state["geo_resumo"] = contagem
        st.session_state["geo_preview"] = publico[["unidade", "bairro", "latitude", "longitude", "precisao_geografica"]].copy()

if "geo_csv" in st.session_state:
    st.success("Consulta concluída. Revise os resultados antes da publicação.")
    st.json(st.session_state["geo_resumo"])
    resumo = st.session_state["geo_preview"]
    st.dataframe(resumo, hide_index=True, use_container_width=True)
    validos = resumo.dropna(subset=["latitude", "longitude"])
    if not validos.empty:
        st.map(validos.rename(columns={"latitude": "lat", "longitude": "lon"}), latitude="lat", longitude="lon")
    st.download_button(
        "Baixar data/escolas.csv atualizado (sem endereços ou contatos)",
        data=st.session_state["geo_csv"],
        file_name="escolas.csv",
        mime="text/csv",
        type="primary",
    )
    st.warning(
        "As coordenadas são sugestões do geocodificador: valide as escolas no mapa "
        "e a autorização institucional antes de publicar coordenadas exatas. "
        "O resultado não é persistido na nuvem automaticamente."
    )
    st.markdown(
        "Depois de baixar o CSV minimizado, envie-o ao projeto para atualizar "
        "o arquivo **data/escolas.csv** no GitHub. O Streamlit atualizará o painel."
    )
