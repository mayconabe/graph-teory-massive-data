import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(page_title='Teoria de Grafos - Karate Club', layout='wide')

st.title('Teoria de Grafos aplicada ao Zachary\'s Karate Club')
st.markdown('''
Aplicação interativa de conceitos de **Teoria de Grafos** usando o dataset clássico
**Zachary's Karate Club** (rede social de um clube de karatê).
''')

# Carrega o grafo
G = nx.karate_club_graph()
pos = nx.spring_layout(G, seed=42)

# Calcula centralidades
centralidade_grau = nx.degree_centrality(G)
centralidade_prox = nx.closeness_centrality(G)
centralidade_inter = nx.betweenness_centrality(G, normalized=True)
pagerank = nx.pagerank(G)

df_centralidade = pd.DataFrame({
    'grau': pd.Series(centralidade_grau),
    'proximidade': pd.Series(centralidade_prox),
    'intermediacao': pd.Series(centralidade_inter),
    'pagerank': pd.Series(pagerank)
})
df_centralidade.index.name = 'no'

# Comunidades (extra)
from networkx.algorithms import community
comunidades = community.greedy_modularity_communities(G)
comunidade_por_no = {}
for idx, c in enumerate(comunidades):
    for no in c:
        comunidade_por_no[no] = idx

st.sidebar.header('Opções de visualização')

tipo_centralidade = st.sidebar.selectbox(
    'Centralidade para colorir o grafo:',
    ('grau', 'proximidade', 'intermediacao', 'pagerank', 'comunidades')
)

st.sidebar.markdown('---')
st.sidebar.markdown('Selecione a métrica para ordenar a tabela de nós.')
ordem_tabela = st.sidebar.selectbox(
    'Ordenar tabela por:',
    ('grau', 'proximidade', 'intermediacao', 'pagerank')
)

st.sidebar.markdown('---')
top_n = st.sidebar.slider('Exibir Top N nós na tabela:', min_value=5, max_value=34, value=10, step=1)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader('Visualização do Grafo')

    if tipo_centralidade == 'comunidades':
        valores = [comunidade_por_no[n] for n in G.nodes()]
        legenda_label = 'Comunidades'
    else:
        valores = df_centralidade[tipo_centralidade].reindex(G.nodes()).values
        legenda_label = f'Centralidade: {tipo_centralidade}'

    from matplotlib import cm, colors

    fig, ax = plt.subplots(figsize=(8, 6))

    if tipo_centralidade == 'comunidades':
        cmap = cm.get_cmap('viridis')
        norm = colors.Normalize(vmin=min(valores), vmax=max(valores))
    else:
        cmap = cm.get_cmap('viridis')
        norm = colors.Normalize(vmin=min(valores), vmax=max(valores))

    nodes = nx.draw(
        G, pos, with_labels=True,
        node_size=400,
        node_color=valores,
        cmap=cmap,
        ax=ax
    )

    ax.set_title(f'Grafo colorido por {tipo_centralidade}')

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    fig.colorbar(sm, ax=ax, label=legenda_label)

    st.pyplot(fig)
    plt.clf()

with col2:
    st.subheader('Tabela de Centralidades')
    tabela_ord = df_centralidade.sort_values(ordem_tabela, ascending=False).head(top_n)
    st.dataframe(tabela_ord)

st.markdown('---')
st.markdown('''
### Interpretação

- Nós com valores mais altos de **grau** tendem a ser mais populares (mais conexões diretas).  
- Nós com maior **proximidade** conseguem alcançar outros nós com menos passos em média.  
- Nós com alta **intermediação** funcionam como "pontes" entre subgrupos, controlando o fluxo de informação.  
- Nós com alto **PageRank** são importantes não só pela quantidade de conexões, mas também pela importância de quem está conectado a eles.  
- As **comunidades** representam grupos mais densamente conectados entre si, o que pode indicar subgrupos sociais coesos.
''')
