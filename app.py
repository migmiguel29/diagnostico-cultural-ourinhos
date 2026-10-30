"""Inicializador do dashboard. O pacote é extraído localmente na primeira execução."""
from pathlib import Path
import base64
import io
import lzma
import runpy
import tarfile

BASE = Path(__file__).resolve().parent
DESTINO = BASE / ".projeto_extraido"
MARCADOR = DESTINO / "app.py"
if not MARCADOR.exists():
    partes = sorted((BASE / "bundle").glob("parte-*.txt"))
    if not partes:
        raise RuntimeError("Pacote do projeto não encontrado em bundle/.")
    payload = "".join(p.read_text(encoding="ascii").strip() for p in partes)
    dados = lzma.decompress(base64.b64decode(payload))
    with tarfile.open(fileobj=io.BytesIO(dados), mode="r:") as arq:
        for membro in arq.getmembers():
            if not membro.isfile():
                continue
            caminho = Path(membro.name)
            if caminho.is_absolute() or ".." in caminho.parts:
                raise RuntimeError("Caminho inválido no pacote do projeto")
            saida = DESTINO / caminho
            saida.parent.mkdir(parents=True, exist_ok=True)
            saida.write_bytes(arq.extractfile(membro).read())
runpy.run_path(str(MARCADOR), run_name="__main__")
