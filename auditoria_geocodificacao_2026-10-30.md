# Auditoria de georreferenciamento — Ourinhos, 30/10/2026

**Situação atual:** CSV final incorporado ao repositório em `data/escolas.csv`.

- 31 respostas escolares com coordenadas; 29 locais distintos devido a duas instituições com respostas duplicadas.
- A rodada inicial com TomTom forneceu 31 candidatos, mas apresentava 3 revisões explícitas e outras correspondências incoerentes. **Não foram publicadas sem conferir.**
- Corrigidos por fontes públicas os registros de Ary Corrêa, Salem Abujamra, Evani Maioral Ribeiro Carneiro, Esmeralda Soares Ferraz, Jandira Lacerda Zanoni e 2 respostas da Orlando Quagliato.
- Todos os pontos foram preservados com código de proveniência em `precisao_geografica`. Pontos de referência de cadastros são prováveis, não medição GPS presencial.

## Correções com fontes complementares

| Escola | Fonte de geolocalização | Observação |
|---|---|---|
| EE Dr. Ary Corrêa | [Cadastro escolar](https://www.escolasnobrasil.com/sudeste/ary-correa-doutor-ourinhos) | POI inicial apontava número divergente; cadastro informa nº 245 |
| EMEF Dr. Salem Abujamra | [Cadastro escolar](https://www.escolasnobrasil.com/sudeste/salem-abujamra-doutor-emef-ourinhos) | Consulta inicial retornou apenas o centro da rua |
| EMEF Evani Maioral Ribeiro Carneiro | [Cadastro escolar](https://www.escolasnobrasil.com/sudeste/evani-maioral-ribeiro-carneiro-professor-emef-ourinhos) | Consulta inicial retornou outro logradouro; referências oficiais atuais podem divergir de registros antigos |
| EE Profª Esmeralda Soares Ferraz | [Cadastro escolar](https://www.escolasnobrasil.com/sudeste/esmeralda-soares-ferraz-professora-ourinhos) | TomTom havia escolhido a Rua Sérgio Oliveira de Moraes; correto é Rua Prudente de Moraes |
| EMEF Profª Jandira Lacerda Zanoni | [Cadastro escolar](https://www.escolasnobrasil.com/sudeste/jandira-lacerda-zanoni-profa-emef-ourinhos) | A TomTom apontava outra região; referência conferida com o bairro Jardim Itamaraty |
| EE Orlando Quagliato (duas respostas) | [Cadastro escolar](https://www.escolasnobrasil.com/sudeste/orlando-quagliato-ourinhos) | Escola rural; a coordenada anterior estava aproximadamente 9 km distante da referência escolar |

## Duplicações

- EE Prof. Dalton Morato Villas Boas: duas respostas no mesmo local.
- EE Orlando Quagliato: duas respostas no mesmo local.

## Política de dados

O solicitante confirmou que seu contrato TomTom permite a retenção dos resultados. O CSV público minimizado contém nomes de escolas, coordenadas e indicadores, sem nomes/contatos dos responsáveis. O dashboard apenas lê dados versionados, sem consulta de geocodificação.

## Limitações

Os resultados são pontos cartográficos prováveis: a qualidade não é equivalente a uma medição topográfica ou visita em campo. O registro foi feito a partir de dados de formulários e cadastros externos com eventuais diferenças de endereço e atualização.
