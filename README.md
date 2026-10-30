# Diagnóstico Cultural de Ourinhos — painel Streamlit

Painel com indicadores de **31 escolas** e **7 iniciativas culturais** obtidos dos formulários da pesquisa de 2026. Desenvolvido para ser publicado no **Streamlit Community Cloud**, sem instalação de Python pelo usuário.

## Arquitetura: somente consulta para visitantes

- **data/escolas.csv:** registros escolares, indicadores, latitude, longitude e qualidade dos pontos.
- **data/agentes.csv:** indicadores de iniciativas culturais (sem endereços geocodificáveis).
- **app.py:** lê os dois CSVs locais, plota gráficos, filtros e marcadores com **Folium/OpenStreetMap**.
- O aplicativo **não** faz consulta à TomTom, ao Nominatim ou a qualquer outra API de geocodificação enquanto as pessoas navegam.
- A exibição do mapa-base utiliza imagens OpenStreetMap, mas isso **não é** uma consulta de geocodificação.

**Situação da base (30/10/2026):** os 31 registros de escolas estão disponíveis, porém as colunas de latitude/longitude **ainda não estão preenchidas**. Não há coordenadas inventadas.

## Preparar coordenadas UMA VEZ — online

Para conservar as posições no CSV sem consultas recorrentes, a preparação inicial deve ser realizada **uma única vez** e concluída **antes de divulgar o painel**.

> **Licenciamento:** os termos usuais da API TomTom restringem a retenção permanente dos resultados de geocodificação, salvo condições específicas. Por isso a etapa temporária usa dados OpenStreetMap, cuja diretriz de geocodificação permite armazenar resultados pontuais em bases próprias, com condições e atribuição. Consulte [Termos TomTom](https://docs.tomtom.com/legal/terms-and-conditions) e [Diretrizes da Fundação OSM](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Geocoding_-_Guideline).

1. Acesse https://share.streamlit.io e crie o aplicativo conectado ao repositório **migmiguel29/diagnostico-cultural-ourinhos**, branch **main**, arquivo **app.py**, Python **3.12**.
2. Em **App settings → Secrets**, configure **somente** uma senha de preparação (não precisa de chave TomTom):
   
   ```toml
PREPARACAO_SENHA = "UMA_SENHA_FORTE_DIFERENTE_DA_SUA_CONTA"
```

3. Abra a página **Preparacao unica OSM** no menu da aplicação, informe a senha e envie o **ZIP ou CSV original das respostas escolares**. Não inclua esse arquivo bruto no GitHub.
4. Após aceitar a política de uso do serviço, pressione **Iniciar geocodificação única**. A etapa faz buscas sequenciais, com intervalo superior a um segundo, verifica o município e exige correspondência pontual ou escola identificada. Não são aceitos simples centros de rua ou bairro.
5. Baixe **escolas.csv**, verifique os resultados — especialmente as escolas rurais e endereços incompletos — e envie **somente esse CSV minimizado** nesta conversa, para que seja incorporado ao GitHub em **data/escolas.csv**.
6. Após atualizar o CSV, confirme que o painel mostra os pontos corretamente. Em seguida, desative as páginas administrativas de preparação, remova a senha dos Secrets e deixe **somente app.py** disponível aos visitantes.

**Atenção:** o serviço público Nominatim admite lotes pequenos e pontuais sob limites e termos próprios. A geocodificação **não deve ser repetida toda vez que alguém acessa o aplicativo**, nem automatizada periodicamente. Confira a [política Nominatim](https://operations.osmfoundation.org/policies/nominatim/) antes de executar. O serviço permite no máximo uma requisição por segundo, exige identificação HTTP e cache de resultados.

## Publicar e utilizar

Abra https://share.streamlit.io e faça o deploy de **app.py** usando Python 3.12. Na apresentação pública final, os visitantes apenas consultam o painel e os arquivos CSV. **Não é necessária nenhuma chave TomTom nos Secrets**.

## Estrutura dos arquivos

```text
app.py                         painel com gráficos e mapa por CSV
requirements.txt               dependências
pages/2_Preparacao_unica_OSM.py etapa administrativa provisória (uma vez)
data/escolas.csv               indicadores, latitude/longitude após validação
data/agentes.csv                iniciativas culturais
scripts/preparar_dados.py      importação e minimização de CSVs (manutenção)
scripts/geocodificar_tomtom.py ferramenta legada, não utilizada no app
.github/workflows/validar.yml  checagem de sintaxe
```

## Privacidade e alcance

- **Não publicar os formulários originais:** contêm nomes, telefones, endereços e/ou e-mails de responsáveis.
- Coordenadas precisas identificam estabelecimentos e devem ser divulgadas apenas com autorização institucional e base legal adequadas. Se necessário, use uma versão agregada por bairro.
- Os dados são **respostas de pesquisa**, não censo da oferta cultural de Ourinhos.
- As **7 iniciativas culturais** declararam áreas de atuação; sem endereços completos e verificados, não são representadas por marcadores pontuais.

## Indicadores iniciais

- 31 escolas respondentes.
- 22 declararam biblioteca ou sala de leitura.
- 28 declararam projetos de incentivo à leitura.
- Entre as 9 sem biblioteca nem sala, 8 relataram projetos de leitura.
- 7 iniciativas culturais respondentes.
