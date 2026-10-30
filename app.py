"""Diagnóstico cultural de Ourinhos — painel demonstrativo gerado a partir de dois questionários."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium

BASE = Path(__file__).resolve().parent
CENTRO = [-22.97900009, -49.87099838]  # Referência municipal, não geocodificação das unidades.
CORES = ['#136B77','#DE8F4F','#5667AA','#8A6AA0','#4E936D','#C06A82']
SEG_CORES = {'EE':'blue','PEI':'purple','EMEF':'green','EMEI':'orange','NEI':'red'}

st.set_page_config(page_title='Diagnóstico Cultural | Ourinhos', page_icon='📚', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container {padding-top: 1.6rem; max-width: 1300px;}
h1,h2,h3 {letter-spacing:-.025em;}
[data-testid="stMetric"] {background:#f5f8fa; border:1px solid #e1e8ed; border-radius:12px; padding:15px;}
.smallnote {font-size:.90rem;color:#53616d;}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def ler_bases():
    escolas = pd.read_csv(BASE/'data'/'escolas.csv', dtype={'id':str}).fillna('')
    agentes = pd.read_csv(BASE/'data'/'agentes.csv', dtype={'id':str}).fillna('')
    for col in ['latitude','longitude','infraestrutura_nota']:
        if col in escolas:
            escolas[col] = pd.to_numeric(escolas[col],errors='coerce')
    return escolas, agentes


def percent(n, total):
    return f'{100*n/total:.1f}%' if total else '—'


def barras_categoricas(df, coluna, titulo, *, ordem=None, horizontal=True):
    if df.empty or coluna not in df:
        st.info('Sem respostas no filtro selecionado.')
        return
    s = df[coluna].replace('',pd.NA).dropna().value_counts()
    if s.empty:
        st.info('Não há respostas disponíveis para este indicador.')
        return
    if ordem:
        s = s.reindex([x for x in ordem if x in s.index],fill_value=0)
    tab = s.rename_axis('Categoria').reset_index(name='Respostas')
    if horizontal:
        tab = tab.iloc[::-1]
        fig=px.bar(tab, x='Respostas', y='Categoria', orientation='h', text='Respostas', color_discrete_sequence=CORES)
        fig.update_yaxes(title=None)
        fig.update_xaxes(title='Número de respostas', dtick=1)
    else:
        fig=px.bar(tab,x='Categoria',y='Respostas',text='Respostas',color_discrete_sequence=CORES)
        fig.update_xaxes(title=None)
        fig.update_yaxes(title='Número de respostas',dtick=1)
    fig.update_traces(textposition='outside',cliponaxis=False)
    fig.update_layout(title=titulo, height=max(300,min(540,210+37*len(tab))), margin=dict(l=8,r=15,t=55,b=15), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def multiescolha(df, coluna, titulo, nmax=10):
    if df.empty or coluna not in df:
        st.info('Sem dados.'); return
    itens = df[coluna].replace('',pd.NA).dropna().str.split(';').explode().dropna().str.strip()
    itens = itens[itens.ne('')]
    vc = itens.value_counts().head(nmax)
    if vc.empty:
        st.info('Sem dados.'); return
    tab = vc.rename_axis('Item').reset_index(name='Menções').iloc[::-1]
    fig=px.bar(tab,x='Menções',y='Item',orientation='h',text='Menções', color_discrete_sequence=CORES)
    fig.update_layout(title=titulo,height=max(320,160+38*len(tab)), margin=dict(l=8,r=12,t=50,b=25),showlegend=False)
    fig.update_yaxes(title=None)
    fig.update_xaxes(title='Menções (múltipla escolha)',dtick=1)
    fig.update_traces(textposition='outside',cliponaxis=False)
    st.plotly_chart(fig,use_container_width=True)


def exibir_mapa(df):
    mapa=folium.Map(location=CENTRO, zoom_start=12, tiles='OpenStreetMap',control_scale=True)
    validos=df.dropna(subset=['latitude','longitude']).copy()
    validos=validos[validos['latitude'].between(-23.20,-22.75) & validos['longitude'].between(-50.15,-49.65)]
    for _,r in validos.iterrows():
        # Os pop-ups não exibem nomes de responsáveis, telefones, e-mails ou respostas individuais.
        legenda=f"{r['unidade']} — {r['segmento']} — {r['bairro']}"
        folium.Marker(location=[float(r['latitude']),float(r['longitude'])], tooltip=legenda,
            popup=folium.Popup(legenda, max_width=360),
            icon=folium.Icon(color=SEG_CORES.get(r['segmento'],'gray'),icon='book',prefix='fa')).add_to(mapa)
    st_folium(mapa, width=None, height=530, returned_objects=[], key='mapa_cultural')
    if validos.empty:
        st.warning('A base atual ainda não contém coordenadas verificadas. A preparação geográfica é uma etapa única e separada; o dashboard apenas lê o CSV versionado no GitHub.')
    else:
        st.caption(f'{len(validos)} unidade(s) com coordenadas verificadas nos filtros atuais. Base cartográfica: © OpenStreetMap; coordenadas carregadas de data/escolas.csv, sem chamada a serviços de geocodificação.')
    return validos

escolas, agentes = ler_bases()
st.title('📚 Mapa do acesso à leitura e à cultura')
st.caption('Ourinhos (SP)  ·  Diagnóstico para planejamento cultural  ·  Dados declarados nos questionários de 2026')
st.info('Leitura dos indicadores: estes números representam apenas os formulários recebidos, não um censo de todos os equipamentos culturais ou escolares do município.',icon='ℹ️')

with st.sidebar:
    st.header('Filtros da pesquisa')
    segs=st.multiselect('Segmentos escolares', sorted(escolas['segmento'].dropna().unique()),default=sorted(escolas['segmento'].dropna().unique()))
    filtradas=escolas[escolas['segmento'].isin(segs)].copy()
    bairros=sorted(filtradas['bairro'].dropna().unique())
    bairro_escolhido=st.multiselect('Bairros / localidades escolares',bairros,default=bairros)
    filtradas=filtradas[filtradas['bairro'].isin(bairro_escolhido)]
    st.divider()
    tipos=st.multiselect('Perfil das iniciativas culturais',sorted(agentes['perfil'].unique()),default=sorted(agentes['perfil'].unique()))
    agentes_filtrados=agentes[agentes['perfil'].isin(tipos)].copy()
    st.divider()
    st.caption(f'Escolas no filtro: {len(filtradas)}/{len(escolas)}')
    st.caption(f'Iniciativas no filtro: {len(agentes_filtrados)}/{len(agentes)}')

aba_geral, aba_escola, aba_agentes, aba_mapa, aba_qualidade = st.tabs(['Visão geral','Escolas e bibliotecas','Iniciativas culturais','Mapa geográfico','Metodologia e qualidade'])

with aba_geral:
    st.subheader('Indicadores essenciais')
    a,b,c,d = st.columns(4)
    a.metric('Escolas respondentes',len(filtradas))
    b.metric('Com biblioteca ou sala de leitura',int(filtradas['espaco_leitura'].isin(['Biblioteca','Sala de Leitura']).sum()),percent(int(filtradas['espaco_leitura'].isin(['Biblioteca','Sala de Leitura']).sum()),len(filtradas)))
    c.metric('Com projeto de leitura',int(filtradas['projetos_leitura'].eq('Sim').sum()),percent(int(filtradas['projetos_leitura'].eq('Sim').sum()),len(filtradas)))
    d.metric('Iniciativas culturais',len(agentes_filtrados))
    x,y=st.columns(2)
    with x:
        barras_categoricas(filtradas,'espaco_leitura','Equipamento de leitura nas escolas',ordem=['Biblioteca','Sala de Leitura','Nenhuma das alternativas'])
    with y:
        barras_categoricas(filtradas,'segmento','Respondentes por segmento escolar')
    x,y=st.columns(2)
    with x:
        barras_categoricas(filtradas,'projetos_leitura','Projetos de incentivo à leitura')
    with y:
        barras_categoricas(agentes_filtrados,'frequencia','Frequência de atividades culturais')
    sem_espaco_projeto = int((filtradas['espaco_leitura'].eq('Nenhuma das alternativas') & filtradas['projetos_leitura'].eq('Sim')).sum())
    st.markdown(f'**Achado para o planejamento:** {sem_espaco_projeto} escola(s) no filtro realizam projetos de leitura apesar de não declararem biblioteca nem sala de leitura. Isso sinaliza oportunidade de avaliar a infraestrutura, não de concluir que falta acesso ao livro.')
    st.caption('Os filtros de escolas e iniciativas funcionam independentemente; não representam amostras comparáveis entre si.')

with aba_escola:
    st.subheader('Infraestrutura e oportunidades de leitura')
    a,b,c=st.columns(3)
    a.metric('Bibliotecas declaradas',int(filtradas['espaco_leitura'].eq('Biblioteca').sum()))
    b.metric('Salas de leitura declaradas',int(filtradas['espaco_leitura'].eq('Sala de Leitura').sum()))
    c.metric('Sem espaço declarado',int(filtradas['espaco_leitura'].eq('Nenhuma das alternativas').sum()))
    x,y=st.columns(2)
    with x:
        barras_categoricas(filtradas,'acervo','Tamanho dos acervos declarados')
    with y:
        barras_categoricas(filtradas,'emprestimos','Faixa de empréstimos por semana')
    x,y=st.columns(2)
    with x:
        barras_categoricas(filtradas,'acervo_virtual','Acesso a acervo virtual')
    with y:
        barras_categoricas(filtradas,'acessibilidade_inclusao','Acessibilidade e/ou inclusão declarada')
    st.subheader('Avaliação da infraestrutura')
    if filtradas['infraestrutura_nota'].notna().sum():
        nota=filtradas['infraestrutura_nota'].dropna()
        st.metric('Avaliação média do espaço (respostas válidas)',f'{nota.mean():.2f} / 5',f'{len(nota)} respostas',delta_color='off')
        st.caption('A escala 1–5 é autorrelatada; não houve vistoria técnica.')
    dimensoes={'iluminacao':'Iluminação','climatizacao':'Climatização','mobiliario':'Mobiliário','estrutura_predial':'Estrutura predial'}
    votos=[]
    for col,nome in dimensoes.items():
        for v,qtd in filtradas[col].replace('',pd.NA).dropna().value_counts().items():
            votos.append({'Dimensão':nome,'Avaliação':v,'Respostas':int(qtd)})
    if votos:
        graf=px.bar(pd.DataFrame(votos),x='Dimensão',y='Respostas',color='Avaliação',barmode='stack',
            category_orders={'Avaliação':['Péssimo','Ruim','Regular','Bom','Ótimo']},
            color_discrete_map={'Péssimo':'#B24A48','Ruim':'#D9896B','Regular':'#D8B052','Bom':'#62A6A0','Ótimo':'#3E7A83'})
        graf.update_layout(height=385,margin=dict(t=20,l=5,r=5,b=15))
        st.plotly_chart(graf,use_container_width=True)
    st.subheader('Distribuição territorial declarada')
    barras_categoricas(filtradas,'bairro','Quantidade de escolas por bairro / localidade')

with aba_agentes:
    st.subheader('Atuação das iniciativas culturais')
    a,b,c,d=st.columns(4)
    a.metric('Iniciativas respondentes',len(agentes_filtrados))
    b.metric('Com CNPJ declarado',int(agentes_filtrados['cnpj'].eq('Sim').sum()))
    c.metric('Com interesse no fórum',int(agentes_filtrados['integrar_forum'].eq('Sim').sum()))
    d.metric('Com acervo de livros',int((~agentes_filtrados['acervo_livros'].isin(['Não possui',''])).sum()))
    x,y=st.columns(2)
    with x:
        barras_categoricas(agentes_filtrados,'perfil','Perfis organizacionais')
    with y:
        barras_categoricas(agentes_filtrados,'pessoas_ano_faixa','Pessoas atendidas por ano — faixas declaradas')
    x,y=st.columns(2)
    with x:
        multiescolha(agentes_filtrados,'areas_atuacao','Áreas de atuação (múltiplas respostas)')
    with y:
        multiescolha(agentes_filtrados,'eixos_prioritarios','Eixos prioritários do plano (múltiplas respostas)')
    st.subheader('Desafios percebidos pelas iniciativas')
    desafios=[('desafio_recursos_financeiros','Financeiro'),('desafio_espaco_fisico','Espaço físico'),('desafio_aquisicao_livros','Aquisição de livros'),('desafio_equipamentos','Equipamentos'),('desafio_formacao_profissionais','Formação'),('desafio_divulgacao','Divulgação'),('desafio_participacao_publico','Participação'),('desafio_acessibilidade','Acessibilidade'),('desafio_captacao_recursos','Captação'),('desafio_parcerias','Parcerias')]
    vals=[]
    for col,nome in desafios:
        n=int(agentes_filtrados[col].isin(['Grande','Muito grande']).sum())
        válidas=int(agentes_filtrados[col].ne('').sum())
        vals.append({'Desafio':nome,'Grande ou muito grande':n,'Respostas válidas':válidas})
    resultado=pd.DataFrame(vals).sort_values('Grande ou muito grande',ascending=True)
    fig=px.bar(resultado,x='Grande ou muito grande',y='Desafio',orientation='h',text='Grande ou muito grande',color_discrete_sequence=CORES)
    fig.update_xaxes(dtick=1,title='Iniciativas que indicaram desafio grande ou muito grande')
    fig.update_yaxes(title=None)
    fig.update_traces(textposition='outside',cliponaxis=False)
    fig.update_layout(height=455,margin=dict(l=8,r=10,t=15,b=15))
    st.plotly_chart(fig,use_container_width=True)
    st.caption('Amostra pequena: a soma de menções não equivale a pessoas atendidas. As respostas representam percepções institucionais.')
    st.subheader('Avaliação das políticas e serviços culturais')
    avaliacoes=[('avaliacao_acesso_livro','Acesso ao livro'),('avaliacao_incentivo_leitura','Incentivo à leitura'),('avaliacao_programacao_literaria','Programação'),('avaliacao_autores_locais','Autores locais'),('avaliacao_mediadores','Mediadores'),('avaliacao_bibliotecas','Bibliotecas'),('avaliacao_acessibilidade_cultural','Acessibilidade'),('avaliacao_politicas_publicas','Políticas públicas')]
    votos=[]
    for col,nome in avaliacoes:
        for nota,num in agentes_filtrados[col].replace('',pd.NA).dropna().value_counts().items():
            votos.append({'Dimensão':nome,'Avaliação':nota,'Respostas':int(num)})
    if votos:
        fig=px.bar(pd.DataFrame(votos),x='Dimensão',y='Respostas',color='Avaliação',barmode='stack',
            category_orders={'Avaliação':['Muito ruim','Ruim','Regular','Bom','Muito bom']},
            color_discrete_map={'Muito ruim':'#B24A48','Ruim':'#D9896B','Regular':'#D8B052','Bom':'#62A6A0','Muito bom':'#3E7A83'})
        fig.update_layout(height=420,margin=dict(t=20,l=5,r=5,b=20))
        st.plotly_chart(fig,use_container_width=True)

with aba_mapa:
    st.subheader('Georreferenciamento dos equipamentos escolares')
    mapeaveis = filtradas.dropna(subset=['latitude','longitude'])
    a,b,c=st.columns(3)
    a.metric('Escolas no filtro',len(filtradas))
    b.metric('Geocodificadas',len(mapeaveis))
    c.metric('Pendentes',len(filtradas)-len(mapeaveis))
    st.caption('Marcadores só aparecem quando há latitude e longitude validadas por endereço. A ausência de um marcador não significa ausência de serviço.')
    exibir_mapa(filtradas)
    st.markdown('**Iniciativas culturais:** o formulário informa áreas amplas de atuação, como “toda a cidade”, sem endereço pontual. Elas são analisadas estatisticamente, mas não recebem um marcador inventado.')
    st.caption('O mapa utiliza OpenStreetMap para visualização e coordenadas previamente gravadas em data/escolas.csv. Nenhuma API de geocodificação é chamada durante a visualização. Não é um mapa de calor da população, nem uma medida de acessibilidade por distância.')

with aba_qualidade:
    st.subheader('Origem e qualidade da informação')
    st.markdown('''
    **Origem:** duas exportações CSV de formulários sobre (1) equipamentos escolares e acervos e (2) iniciativas culturais, vinculadas ao planejamento de políticas culturais de Ourinhos.

    **Universo:** respostas obtidas até a exportação, sem extrapolação para todas as escolas ou para toda a oferta cultural da cidade. Não há ponderação por população ou matrículas.

    **Privacidade:** a versão destinada ao GitHub retira nomes e contatos de responsáveis, e-mails, telefones, endereços e observações livres. Os identificadores de unidades são pseudônimos; dados geográficos exatos podem permitir reidentificar uma instituição. Antes da publicação, verificar a autorização institucional e finalidade do consentimento.

    **Geocodificação:** coordenadas são preparadas previamente, por fonte aberta ou oficial, verificadas quanto ao município e registradas no CSV. Endereços incompletos ou resultados sem correspondência pontual ficam pendentes.

    **Iniciativas:** abrangências como “toda a cidade” não representam um local físico verificável, portanto não são plotadas como pontos.

    **Interpretação:** múltiplas escolhas podem somar mais do que o número de respondentes; campos pulados não entram na contagem das categorias exibidas.
    ''')
    st.subheader('Cobertura das respostas escolares')
    dados=[]
    for col,nome in [('espaco_leitura','Espaço de leitura'),('acervo','Acervo'),('emprestimos','Empréstimos'),('infraestrutura_nota','Nota de infraestrutura'),('projetos_leitura','Projetos de leitura'),('acessibilidade_inclusao','Acessibilidade')]:
        s=filtradas[col]
        n=int(s.notna().sum()) if col=='infraestrutura_nota' else int(s.fillna('').ne('').sum())
        dados.append({'Indicador':nome,'Respostas disponíveis':n,'Total filtrado':len(filtradas),'Cobertura':percent(n,len(filtradas))})
    st.dataframe(pd.DataFrame(dados),hide_index=True,use_container_width=True)
    # Apenas um resumo agregado é disponibilizado; os CSVs de linha não são baixados por esta interface.
    agregadas=escolas.groupby('segmento',dropna=False).agg(
        escolas=('id','size'),
        com_espaco_leitura=('espaco_leitura',lambda s:s.isin(['Biblioteca','Sala de Leitura']).sum()),
        com_projetos=('projetos_leitura',lambda s:s.eq('Sim').sum()),
        com_acessibilidade=('acessibilidade_inclusao',lambda s:s.eq('Sim').sum())
    ).reset_index()
    st.download_button('Baixar resumo agregado por segmento (CSV)',data=agregadas.to_csv(index=False).encode('utf-8-sig'),file_name='resumo_cultura_ourinhos.csv',mime='text/csv')
    st.caption('Dados conferidos a partir das duas exportações de formulários; as posições geográficas dependem de geocodificação posterior e revisão humana.')

st.divider()
st.caption('Painel demonstrativo de planejamento cultural • Ourinhos/SP • Não publicar bases originais dos formulários no repositório.')
