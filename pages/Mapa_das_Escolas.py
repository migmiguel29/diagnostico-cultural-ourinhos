"""Mapa geográfico dedicado, sem geocodificação online.
Usa apenas data/escolas.csv versionado no GitHub.
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapa das escolas | Cultura Ourinhos", page_icon="📍", layout="wide")
st.title("📍 Escolas de Ourinhos — mapa georreferenciado")
st.caption("Coordenadas previamente registradas no GitHub. Não há consultas à TomTom.")
raiz = Path(__file__).resolve().parents[1]
arquivo = raiz / "data" / "escolas.csv"

@st.cache_data(show_spinner=False)
def carregar():
    tabela = pd.read_csv(arquivo, dtype={"id": str})
    for campo in ["latitude", "longitude"]:
        tabela[campo] = pd.to_numeric(tabela[campo], errors="coerce")
    tabela = tabela.dropna(subset=["latitude", "longitude"])
    tabela = tabela[
        tabela["latitude"].between(-23.20, -22.75) &
        tabela["longitude"].between(-50.15, -49.65)
    ]
    # Não exibir referências municipais e endereços que foram rejeitados.
    qualidade = tabela["precisao_geografica"].fillna("").astype(str).str.upper()
    tabela = tabela.loc[
        ~qualidade.str.contains("MUNICIPIO_REFERENCIA|NAO_LOCALIZADA|ENDERECO_ESTIMADO", regex=True)
    ]
    return tabela

dados = carregar()
if dados.empty:
    st.error("Nenhuma coordenada válida em data/escolas.csv. Confira o arquivo no GitHub.")
    st.stop()

# As duplicações são respostas à pesquisa, não prédios adicionais.
locais = dados.groupby(["latitude", "longitude"], as_index=False).agg(
    unidade=("unidade", "first"),
    bairro=("bairro", "first"),
    segmento=("segmento", "first"),
    precisao_geografica=("precisao_geografica", "first"),
    respostas=("id", "size"),
)
segmentos = sorted(locais["segmento"].dropna().unique().tolist())
selecionados = st.multiselect("Filtrar segmento escolar", segmentos, default=segmentos)
filtrados = locais[locais["segmento"].isin(selecionados)].copy()

a, b, c = st.columns(3)
a.metric("Respostas na base", len(dados))
b.metric("Escolas distintas", len(locais))
c.metric("Pontos no filtro", len(filtrados))
st.caption("O total de respostas pode ser maior que o de escolas: há unidades com dois formulários.")

if filtrados.empty:
    st.warning("O filtro escolhido não tem escolas. Selecione ao menos um segmento.")
    st.stop()

palette = {
    "EE": "#2876B5", "PEI": "#7444AC", "EMEF": "#238A52",
    "EMEI": "#D97B28", "NEI": "#B73F51"
}
m = folium.Map(
    location=[float(filtrados["latitude"].mean()), float(filtrados["longitude"].mean())],
    zoom_start=12, tiles="OpenStreetMap", control_scale=True
)
grupo = MarkerCluster(name="Escolas", showCoverageOnHover=False).add_to(m)
for _, r in filtrados.iterrows():
    texto = (
        f"<b>{r['unidade']}</b><br>{r['segmento']} — {r['bairro']}<br>"
        f"{r['respostas']} resposta(s) do formulário<br>"
        f"{r['precisao_geografica']}"
    )
    folium.CircleMarker(
        [float(r["latitude"]), float(r["longitude"])],
        radius=9, color="#ffffff", weight=2, fill=True,
        fill_color=palette.get(r["segmento"], "#136B77"),
        fill_opacity=0.95,
        tooltip=str(r["unidade"]),
        popup=folium.Popup(texto, max_width=340)
    ).add_to(grupo)
m.fit_bounds([
    [float(filtrados.latitude.min()), float(filtrados.longitude.min())],
    [float(filtrados.latitude.max()), float(filtrados.longitude.max())]
], padding=(32, 32), max_zoom=14)

st.subheader("Mapa interativo")
st_folium(m, height=590, width=None, returned_objects=[], key="escolas_mapa_fixo")
st.caption("Clique nos agrupamentos para expandir e nos pontos para identificar a escola. © OpenStreetMap.")

# Fallback sem Leaflet, Mapbox e nem tiles externos: pontos estão no HTML Plotly.
st.subheader("Localização por coordenadas — visualização alternativa")
st.caption("Se o mapa interativo for bloqueado pelo navegador, os mesmos pontos devem aparecer abaixo, mesmo sem carregar o mapa-base.")
fig = px.scatter(
    filtrados, x="longitude", y="latitude", color="segmento", hover_name="unidade",
    hover_data={"bairro": True, "respostas": True, "latitude": ":.6f", "longitude": ":.6f"},
    color_discrete_map=palette, height=490, size_max=15
)
fig.update_traces(marker=dict(size=12, line=dict(color="white", width=1)))
fig.update_yaxes(scaleanchor="x", scaleratio=1, title="Latitude", showgrid=True)
fig.update_xaxes(title="Longitude", showgrid=True)
fig.update_layout(margin=dict(l=10, r=10, b=5, t=5))
st.plotly_chart(fig, use_container_width=True)

with st.expander("Conferir todas as escolas e coordenadas", expanded=False):
    st.dataframe(
        filtrados[["unidade", "segmento", "bairro", "latitude", "longitude", "respostas", "precisao_geografica"]]
          .sort_values("unidade"),
        hide_index=True, use_container_width=True
    )
st.caption("Os pontos são posições cartográficas prováveis, não levantamentos topográficos.")
