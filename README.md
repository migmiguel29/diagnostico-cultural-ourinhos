# Diagnóstico Cultural de Ourinhos

Dashboard de distribuição e acesso à cultura para dados de **31 respostas de escolas (29 locais distintos)** e **7 iniciativas culturais**, construído com Streamlit.

## Situação: georreferenciado

- `data/escolas.csv` contém **31/31 registros com latitude e longitude**, com os nomes públicos dos estabelecimentos, dados culturais minimizados e indicação da origem geográfica.
- **29 localidades escolares únicas**: duas escolas (EE Dalton Morato Villas Boas e EE Orlando Quagliato) tiveram duas respostas cada. Os indicadores da pesquisa mantêm as 31 respostas.
- O levantamento foi obtido uma vez por TomTom no Google Colab e revisado com registros públicos de escolas. Foram retificadas as correspondências de EE Dr. Ary Corrêa, EE Esmeralda Soares Ferraz, EMEF Salem Abujamra, EMEF Jandira Lacerda Zanoni, EMEF Evani Maioral Ribeiro Carneiro e EE Orlando Quagliato (2 registros).
- O painel **não realiza nenhuma consulta à TomTom, Nominatim, ViaCEP ou outra API de geocodificação** quando é aberto. Coordenadas são carregadas do CSV do GitHub. Somente o mapa-base utiliza mosaicos cartográficos OpenStreetMap.
- Todas as coordenadas são pontos de referência cartográfica prováveis, e não medições topográficas in loco.

## Publicação (Streamlit Community Cloud)

1. Acesse https://share.streamlit.io/ e autorize GitHub.
2. Escolha `migmiguel29/diagnostico-cultural-ourinhos`, branch `main`, arquivo `app.py`, Python `3.12`.
3. Clique em Deploy. **Não é necessário configurar nenhuma chave TomTom nem Secrets para visualizar**.
4. As atualizações posteriores de pontos ou indicadores são feitas por commit no CSV do repositório.

## Principais arquivos

```text
app.py                        Dashboard de leitura e filtros geográficos
data/escolas.csv               31 respostas escolares + coordenadas já gravadas
data/agentes.csv                7 iniciativas culturais
requirements.txt               Dependências instaladas pelo Streamlit Cloud
scripts/                      Ferramentas de preparação, não executadas no dashboard
auditoria_geocodificacao_2026-10-30.md  Registro histórico do processo
```

## Fontes complementares das correções

- [Escolas no Brasil — EE Orlando Quagliato](https://www.escolasnobrasil.com/sudeste/orlando-quagliato-ourinhos)
- [Escolas no Brasil — EE Esmeralda Soares Ferraz](https://www.escolasnobrasil.com/sudeste/esmeralda-soares-ferraz-professora-ourinhos)
- [Escolas no Brasil — EE Ary Corrêa](https://www.escolasnobrasil.com/sudeste/ary-correa-doutor-ourinhos)
- [Escolas no Brasil — EMEF Salem Abujamra](https://www.escolasnobrasil.com/sudeste/salem-abujamra-doutor-emef-ourinhos)
- [Escolas no Brasil — EMEF Jandira Lacerda Zanoni](https://www.escolasnobrasil.com/sudeste/jandira-lacerda-zanoni-profa-emef-ourinhos)
- [Escolas no Brasil — EMEF Evani Maioral Ribeiro Carneiro](https://www.escolasnobrasil.com/sudeste/evani-maioral-ribeiro-carneiro-professor-emef-ourinhos)
- [Secretaria Municipal de Educação de Ourinhos](https://smeourinhos.sp.gov.br/)

## Privacidade

O repositório armazena dados minimizados. Não publicar exportações originais dos formulários, nomes dos responsáveis, seus telefones/e-mails nem chaves da TomTom. Os nomes das escolas identificam instituições públicas, não participantes da pesquisa. As iniciativas culturais sem endereço verificável não recebem pontos artificiais no mapa.

Este levantamento reflete os formulários recebidos, não um censo de todas as escolas e iniciativas do município.
