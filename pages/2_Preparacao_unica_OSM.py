"""Preparação geográfica UMA VEZ. Não é uma função de consulta do dashboard."""
import hmac
import io
import re
import sys
import time
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from preparar_dados import id_curto, ler_csv, valor

OSM_URL = "https://nominatim.openstreetmap.org/search"
BOUNDS = (-23.20, -22.75, -50.15, -49.65)
IDENTIFICACAO = "DiagnosticoCulturalOurinhos/1.0 (https://github.com/migmiguel29/diagnostico-cultural-ourinhos)"

st.set_page_config(page_title="Preparação geográfica | Ourinhos", page_icon="📍", layout="wide")
st.title("📍 Preparação geográfica — execução única")
st.caption("Ferramenta administrativa provisória: o dashboard público lê somente os CSVs do GitHub.")

def config(nome):
    try:
        return str(st.secrets.get(nome, "")).strip()
    except (FileNotFoundError, KeyError):
        return ""

senha_definida = config("PREPARACAO_SENHA")
if not senha_definida:
    st.error("Configure PREPARACAO_SENHA em App settings → Secrets para habilitar esta etapa administrativa.")
    st.stop()

if not st.session_state.get("preparador_autorizado", False):
    digitada = st.text_input("Senha de preparação", type="password")
    if st.button("Entrar", type="primary"):
        if hmac.compare_digest(digitada, senha_definida):
            st.session_state["preparador_autorizado"] = True
            st.rerun()
        else:
            st.error("Senha inválida.")
    st.stop()

st.info(
    "O processamento é realizado somente quando você clicar em Iniciar. "
    "O CSV original fica na memória durante a sessão. "
    "Somente o CSV minimizado será baixado para integrar o GitHub. "
    "Não publique este formulário de preparação depois de concluir a geocodificação."
)
st.caption(
    "Para armazenar coordenadas permanentemente, usamos OpenStreetMap/Nominatim "
    "em vez da API TomTom, que pode impor restrições ao armazenamento de resultados."
)
st.markdown(
    "[Política de uso Nominatim](https://operations.osmfoundation.org/policies/nominatim/) · "
    "[Diretrizes de geocodificação OSM](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Geocoding_-_Guideline)"
)

def normaliza(s):
    t = unicodedata.normalize("NFKD", str(s))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()

def consultar(s, endereco, numero, nome):
    # Sem busca ao vivo em visitas comuns. Somente lote pequeno, individualmente acionado.
    resposta = s.get(OSM_URL, params={
        "q": endereco, "countrycodes": "br", "format": "jsonv2",
        "addressdetails": 1, "limit": 3
    }, timeout=30)
    resposta.raise_for_status()
    for item in resposta.json():
        addr = item.get("address") or {}
        lat = float(item.get("lat", "nan"))
        lon = float(item.get("lon", "nan"))
        if not (BOUNDS[0] <= lat <= BOUNDS[1] and BOUNDS[2] <= lon <= BOUNDS[3]):
            continue
        municipio = " ".join(str(addr.get(x, "")) for x in ("city", "town", "municipality", "county"))
        if "ourinhos" not in normaliza(municipio):
            continue
        numero_retorno = str(addr.get("house_number", "")).strip()
        tipo = str(item.get("type", "")).lower()
        categoria = str(item.get("category", item.get("class", ""))).lower()
        # Não transformar posição de rua/bairro em ponto supostamente exato de escola.
        if numero_retorno and normaliza(numero_retorno) == normaliza(numero):
            return lat, lon, "OSM: endereço com número (revisar)"
        if categoria == "amenity" and tipo == "school":
            titulo = str(item.get("name", ""))
            p = normaliza(nome).split()
            a = normaliza(titulo)
            significativas = [x for x in p if len(x) > 3 and x not in {"escola", "municipal", "estadual", "ensino"}]
            if titulo and significativas and sum(x in a for x in significativas) >= min(2, len(significativas)):
                return lat, lon, "OSM: escola identificada por nome (revisar)"
    return float("nan"), float("nan"), "Sem correspondência pontual confiável"

def abrir_original(arquivo):
    dados = arquivo.getvalue()
    if len(dados) > 10_000_000:
        raise ValueError("Arquivo maior que 10 MB.")
    if arquivo.name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            entradas = [a for a in z.infolist() if a.filename.lower().endswith(".csv") and not a.is_dir()]
            if len(entradas) != 1 or entradas[0].file_size > 10_000_000:
                raise ValueError("O ZIP deve conter exatamente um arquivo CSV de até 10 MB.")
            dados = z.read(entradas[0])
    df = pd.read_csv(io.BytesIO(dados), dtype=str).fillna("")
    if df.shape[1] < 42 or "Segmento" not in str(df.columns[8]):
        raise ValueError("Arquivo incompatível com o formulário de escolas.")
    return df

arquivo = st.file_uploader("Carregar ZIP/CSV ORIGINAL das escolas (somente nesta etapa)", type=["csv", "zip"])
if arquivo is not None:
    try:
        original = abrir_original(arquivo)
    except (ValueError, UnicodeError, zipfile.BadZipFile, pd.errors.ParserError) as e:
        st.error(f"Falha ao ler o arquivo: {e}")
        st.stop()
    st.write(f"Escolas na exportação: **{len(original)}**")
    st.warning(
        "Os endereços serão enviados ao serviço externo Nominatim/OSM uma única vez "
        "para localizar as escolas. Antes de usar, confira se essa finalidade é permitida "
        "pelo consentimento e pelas políticas da pesquisa."
    )
    if st.button("Iniciar geocodificação única", type="primary"):
        publico = pd.read_csv(ROOT / "data/escolas.csv", dtype={"id": str})
        for k in ("latitude", "longitude"):
            publico[k] = pd.to_numeric(publico[k], errors="coerce")
        indices = {ident: idx for idx, ident in publico["id"].items()}
        resumos = {"aceitos_para_revisao": 0, "pendentes": 0, "sem_id": 0, "erro_rede": 0}
        estado = st.progress(0)
        situacao = st.empty()
        cache = {}
        with requests.Session() as sess:
            sess.headers.update({"User-Agent": IDENTIFICACAO, "Accept-Language": "pt-BR"})
            for i in range(len(original)):
                nome, rua, numero, bairro, cep = [
                    str(valor(original, j).iloc[i]) for j in (1, 2, 3, 4, 5)
                ]
                ident = id_curto("ESC", nome, rua, numero, cep)
                ix = indices.get(ident)
                if ix is None:
                    resumos["sem_id"] += 1
                elif not rua or not numero or numero.upper() in {"S/N", "SN", "S/Nº"}:
                    publico.at[ix, "precisao_geografica"] = "sem número: revisão manual"
                    resumos["pendentes"] += 1
                elif pd.notna(publico.at[ix, "latitude"]) and pd.notna(publico.at[ix, "longitude"]):
                    resumos["aceitos_para_revisao"] += 1
                else:
                    endereco = f"{rua}, {numero}, {bairro}, Ourinhos, São Paulo, Brasil"
                    try:
                        if endereco not in cache:
                            lat, lon, qualidade = consultar(sess, endereco, numero, nome)
                            cache[endereco] = (lat, lon, qualidade)
                            time.sleep(1.2)  # 1 thread, <= 1 requisição por segundo
                        lat, lon, qualidade = cache[endereco]
                        publico.at[ix, "latitude"] = lat
                        publico.at[ix, "longitude"] = lon
                        publico.at[ix, "precisao_geografica"] = qualidade
                        if pd.notna(lat) and pd.notna(lon):
                            resumos["aceitos_para_revisao"] += 1
                        else:
                            resumos["pendentes"] += 1
                    except requests.RequestException:
                        publico.at[ix, "precisao_geografica"] = "erro de rede: revisar"
                        resumos["erro_rede"] += 1
                estado.progress((i + 1) / len(original))
                situacao.caption(f"Processados: {i + 1} / {len(original)}")
        st.session_state["resultado_csv"] = publico.to_csv(index=False).encode("utf-8-sig")
        st.session_state["resultado_resumo"] = resumos
        st.session_state["resultado_preview"] = publico[
            ["id", "unidade", "bairro", "latitude", "longitude", "precisao_geografica"]
        ].copy()

if "resultado_csv" in st.session_state:
    st.success("Lote concluído. Coordenadas candidatas precisam de revisão antes da divulgação.")
    st.json(st.session_state["resultado_resumo"])
    st.dataframe(st.session_state["resultado_preview"], hide_index=True, use_container_width=True)
    st.download_button(
        "Baixar data/escolas.csv minimizado",
        st.session_state["resultado_csv"],
        file_name="escolas.csv",
        mime="text/csv",
        type="primary",
    )
    st.warning(
        "O CSV baixado ainda requer validação cartográfica e autorização institucional. "
        "Não coloque o ZIP original, nomes de responsáveis, endereços ou senhas no GitHub. "
        "Após integrar o CSV, remova esta página administrativa para deixar só a visualização."
    )
