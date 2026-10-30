# Auditoria da geocodificação das escolas de Ourinhos (30/10/2026)

**Origem da auditoria:** arquivo `resultado_tomtom_colab.zip`, disponibilizado para conferência. Este relatório **não contém coordenadas derivadas da API**.

## Resultado

- 31 registros de pesquisa, todos com coordenadas sugeridas pela TomTom.
- 28 localizações classificadas pelo notebook como pontuais prováveis: 15 por endereço/número, 13 por nome/POI.
- 3 localizações exigem revisão: 1 correspondência por nome possivelmente incorreta, 1 apenas em nível de rua, 1 em rua incompatível.
- 29 pares distintos de coordenadas, porque 2 escolas apresentam duplicação de respostas.
- Os 31 IDs e as 28 colunas correspondem à estrutura atual de `data/escolas.csv`.

**Importante:** ponto sugerido não é sinônimo de coordenada escolar confirmada. Não usar resultados de rua/CEP/endereço divergente como localização precisa.

## Três escolas para revisão

| Registro | Escola | Problema | Endereço público confirmado |
|---|---|---|---|
| ESC-a4796cf184 | EE Dr. Ary Corrêa | POI localizado próximo ao nº 400; formulário e cadastro oficial indicam nº 245 | Rua Antônio Henrique Rolli, 245 — Jardim Europa |
| ESC-216e3921c1 | EMEF Dr. Salem Abujamra | Serviço retornou somente posição de rua | Rua Ezelino Zório Maulen, 15 — C. H. Orlando Quagliato |
| ESC-af1985f061 | EMEF Profª Evani Maioral Ribeiro Carneiro | Resultado estimado em outra rua; **não usar como ponto escolar** | Rua Alberto Mori, 455 — Parque Minas Gerais |

**Fontes:**
- Secretaria de Educação SP, cadastro Ary Corrêa: https://transparencia.educacao.sp.gov.br/Home/DetalhesEscola?codesc=900916
- SME Ourinhos, escolas municipais (Salem): https://smeourinhos.sp.gov.br/
- Prefeitura de Ourinhos, endereços municipais (Evani): https://www.ourinhos.sp.gov.br/portal/noticias/0/3/6314/inscricoes-para-o-bolsa-trabalho-em-ourinhos-comecam-na-proxima-terca-24

## Duplicações de respondentes

- Escola Estadual Prof. Dalton Morato Villas Boas: 2 respostas da mesma unidade.
- Escola Estadual Orlando Quagliato: 2 respostas da mesma unidade.

Essas respostas não devem ser descartadas automaticamente, pois podem conter respostas diferentes para os indicadores. Entretanto, o mapa não deve interpretar cada resposta como uma escola física diferente.

## Publicação das coordenadas

**Não foi feito commit do CSV com geocódigos TomTom.** A documentação de termos gerais da plataforma restringe armazenamento/cache de resultados sem as permissões contratuais correspondentes. É necessário verificar direito de retenção permanente antes de gravá-los no repositório (ainda que privado).

- Termos: https://docs.tomtom.com/legal/terms-and-conditions
- Alternativa com fonte persistível: coordenadas próprias validadas presencialmente, levantamento municipal, ou dados abertos com licença compatível.

O Streamlit permanece configurado para **ler somente CSV do GitHub**, sem chamar API de geocodificação ao navegar. O código foi atualizado para **não plotar estimativas de endereço em rua divergente** como escolas.
