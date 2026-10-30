# Diagnóstico Cultural de Ourinhos

Repositório privado do painel Streamlit para análise das respostas de duas pesquisas culturais em Ourinhos (SP).

**Status atual: estrutura inicial publicada; o pacote integral ainda precisa ser enviado.** Não realizar deploy antes de completar o upload.

## Instalação do projeto

1. Descompacte o arquivo `diagnostico_cultural_ourinhos_github.zip` disponibilizado na conversa do ChatGPT.
2. No GitHub, abra este repositório e selecione **Add file → Upload files**.
3. Envie **os arquivos e pastas contidos no ZIP**, preservando a estrutura; não envie o próprio ZIP. Substitua o `app.py` e o `README.md` iniciais pelos arquivos do pacote.
4. Confirme que `app.py`, `requirements.txt`, `data/escolas.csv`, `data/agentes.csv` e `scripts/` aparecem no repositório.
5. No Streamlit Community Cloud, selecione este repositório, branch `main` e arquivo `app.py`.

## Privacidade e geocodificação

- As bases tratadas devem excluir nomes de responsáveis, telefones, e-mails e endereços pessoais.
- Não envie os ZIPs originais dos Google Forms.
- Não envie sua chave TomTom ao GitHub. Execute localmente `scripts/geocodificar_tomtom.py` usando a variável de ambiente `TOMTOM_API_KEY`, valide os resultados e envie somente o CSV tratado.
- As iniciativas culturais não têm endereço suficiente para serem mapeadas pontualmente; não atribua coordenadas presumidas.
- Os dados são uma amostra de respostas, não um censo de todos os equipamentos culturais.

## Situação do levantamento

31 escolas respondentes e 7 iniciativas culturais. Entre 9 escolas sem biblioteca ou sala de leitura declarada, 8 relatam projetos de incentivo à leitura.

A implementação completa, explicações de processamento, validação e atualizações constam do `README.md` incluído no pacote ZIP.
