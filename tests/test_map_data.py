"""Validação do conjunto cartográfico publicado; sem consultas externas."""
from pathlib import Path
import pandas as pd

RAIZ=Path(__file__).resolve().parents[1]
df=pd.read_csv(RAIZ / "data" / "escolas.csv")
assert len(df)==31, f"Esperadas 31 respostas, lidas {len(df)}"
assert df["id"].nunique()==31, "Identificadores duplicados"
for c in ("latitude","longitude"):
    df[c]=pd.to_numeric(df[c],errors="coerce")
assert df[["latitude","longitude"]].notna().all().all(), "Pontos sem coordenadas"
assert df.latitude.between(-23.20,-22.75).all(), "Latitudes fora da região"
assert df.longitude.between(-50.15,-49.65).all(), "Longitudes fora da região"
qualidade=df["precisao_geografica"].fillna("").astype(str).str.upper()
exclui=qualidade.str.contains("MUNICIPIO_REFERENCIA|NAO_LOCALIZADA|ENDERECO_ESTIMADO")
aprox=qualidade.str.contains("REVISAR|APROX|ESTIMADO|CEP_AREA|CORRECAO_MANUAL")
visiveis=df.loc[~exclui]
assert len(visiveis)==31, f"Há {len(df)-len(visiveis)} linhas descartadas."
assert visiveis[["latitude","longitude"]].drop_duplicates().shape[0]==29
print(f"OK: {len(df)} respostas, {len(visiveis)} visíveis, 29 localidades, {sum(aprox)} aproximações.")
