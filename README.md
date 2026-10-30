# 📚 Diagnóstico cultural de Ourinhos — Streamlit

Aplicação de indicadores sobre acesso à leitura, equipamentos escolares e iniciativas culturais com georreferenciamento pontual por **TomTom Search Geocoding API** e mapas exibidos em **OpenStreetMap + Folium**.

## Diagnóstico inicial

- 31 respostas escolares: 18 salas de leitura, 4 bibliotecas e 9 sem esses espaços declarados.
- 28 escolas informam projetos de incentivo à leitura; 26 declaram iniciativas de acessibilidade/inclusão. **Entre as 9 sem biblioteca ou sala declarada, 8 realizam projetos de leitura.**
- 7 respostas de iniciativas culturais; 6 demonstram interesse em integrar o fórum municipal.
- As **31 escolas** possuem campos de endereço preenchidos, mas **não foram geocodificadas automaticamente**, pois não foi fornecida uma chave TomTom.
- A pesquisa de iniciativas culturais informa regiões amplas de atuação, **não endereços de sedes**. Não se atribuem coordenadas fictícias.
- Uma escola tem CEP de nove dígitos no CSV original; revise essa informação antes da geocodificação.

**Atenção:** dados amostrais. Não interpretá-los como censo municipal nem associar proximidade geográfica a acesso efetivo sem informações populacionais e de transporte.

## 1. Executar localmente

Recomendado: Python 3.11 ou 3.12.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O painel já funciona com os arquivos preparados `data/escolas.csv` e `data/agentes.csv`. O mapa informa a ausência de coordenadas até a etapa 2. **Não é necessário ter chave TomTom para consultar os gráficos.**

## 2. Geocodificar escolas com a TomTom

1. Crie uma API Key em [TomTom Developer](https://developer.tomtom.com/).
2. Mantenha o CSV ou ZIP **original** de respostas escolares em uma pasta local fora do repositório. Os arquivos foram fornecidos na conversa, mas **não são incluídos neste projeto** porque contêm contatos, responsáveis e endereços.
3. Configure a variável de ambiente no computador, sem colar a chave no código.

**PowerShell (Windows):**

```powershell
$env:TOMTOM_API_KEY = 'SUA_CHAVE_TOMTOM'
python scripts/geocodificar_tomtom.py --escolas "C:\caminho\formulario_escolas.zip"
```

**Linux/macOS:**

```bash
export TOMTOM_API_KEY='SUA_CHAVE_TOMTOM'
python scripts/geocodificar_tomtom.py --escolas '/caminho/formulario_escolas.zip'
```

O script lê os endereços originais em memória e salva **somente** latitude, longitude e classe da correspondência no `data/escolas.csv`. Verifica município Ourinhos, país BR, tipo de retorno pontual e confiança mínima de 0,75; respostas sem correspondência confiável não recebem marcadores. Revise manualmente a localização de cada unidade, especialmente ruas com nomes repetidos, escolas rurais e endereço `S/N`. Uma correspondência por intervalo de números não garante a localização exata da entrada do imóvel.

Em seguida execute `streamlit run app.py` novamente. O painel exibirá os pontos existentes e a quantidade de escolas ainda pendentes.

## 3. Atualizar as pesquisas

Com novas exportações dos Google Forms, execute localmente:

```bash
python scripts/preparar_dados.py --escolas "/caminho/escolas.zip" --agentes "/caminho/iniciativas.zip"
python scripts/geocodificar_tomtom.py --escolas "/caminho/escolas.zip"
```

A primeira etapa gera CSVs depurados e preserva as geocodificações existentes para IDs iguais. Se as perguntas mudarem de ordem, **revise os índices dos campos nos scripts** antes de atualizar: o importador valida o formato dos dois questionários atuais.

## 4. Publicar GitHub → Streamlit Community Cloud

1. Crie um **repositório novo** no GitHub.
2. Envie os arquivos e pastas deste projeto (**sem incluir** ZIPs ou CSVs brutos ou chave TomTom).
3. Vá a [share.streamlit.io](https://share.streamlit.io/) e escolha **Create app / Deploy app**; conecte o repositório.
4. Informe a branch e `app.py` como arquivo principal.
5. Em `Advanced settings`, pode usar Python 3.12. Não precisa incluir a chave TomTom na nuvem, porque a geocodificação é executada localmente antes do deploy.
6. Atualizações dos CSVs depurados no GitHub atualizam o dashboard após a publicação.

## 5. Privacidade e validação

Os dados do projeto são uma **versão minimizada**, não uma garantia de anonimato. Os arquivos públicos removem nomes de responsáveis, contatos, endereços completos, CEPs e descrições em texto livre. Mantêm segmento, bairro e indicadores institucionais, que ainda podem permitir inferências sobre as escolas, sobretudo quando acompanhados de coordenadas. Por isso:

- Revise com a coordenação da pesquisa se o consentimento cobre **publicação na internet** de indicadores por unidade/iniciativa e coordenadas exatas. Se não, publique **apenas agregados** e use o projeto em ambiente de acesso restrito para detalhamento geográfico.
- Nunca suba as respostas brutas para um repositório público.
- Não compartilhe a chave TomTom. Geocodificação roda fora do Streamlit; mapas usam OpenStreetMap, sem expor chave no navegador.
- Para mapear iniciativas culturais com pontos físicos, faça uma **pesquisa adicional** sobre a sede ou local de atividade autorizado, e só então implemente essa camada.
- Para calcular lacunas de acesso, será necessário cruzar malha territorial, população e deslocamento. Os dados atuais só permitem distribuição e indicadores declarados.

## Integração contínua no GitHub

O arquivo `.github/workflows/validar.yml` verifica automaticamente a sintaxe do projeto e a consistência dos indicadores em cada atualização do repositório. Essa validação não executa uma instância visual do Streamlit nem testa a API TomTom ao vivo.

## Estrutura

```text
app.py                          Dashboard Streamlit
requirements.txt                Dependências Python
.streamlit/config.toml          Tema
scripts/preparar_dados.py       Importação e minimização dos dois CSVs
scripts/geocodificar_tomtom.py  Endereçamento via API TomTom
scripts/__init__.py             Pacote
scripts/testes_basicos.py       Verificações dos CSVs gerados
scripts/testes_geocodificador.py Testes simulados do geocodificador
.github/workflows/validar.yml   Testes automáticos no GitHub
data/escolas.csv                Indicadores escolares sem dados de contato
data/agentes.csv               Indicadores culturais sem dados de contato
```

Referências técnicas: [TomTom Geocode v2](https://docs.tomtom.com/geocoding-api/documentation/tomtom-maps/v1/geocode) · [Deploy Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) · [Gestão de segredos](https://docs.streamlit.io/deploy/concepts/secrets).
