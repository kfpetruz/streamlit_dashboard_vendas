## IMPORTAÇÃO DAS BIBLIOTECAS
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title= 'Dashboard de Vendas', layout= 'wide', page_icon=":abacus:") #para as colunas não se sobreporem

## FUNÇÕES
def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000 #se valor não for <1000, divide por 1000 e rotorna a linha abaixo
    return f'{prefixo} {valor:.2f} milhões'
    

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

## DADOS
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'] #lista para o filltro lateral

#incluindo filtros nessa posição porque eles virarão parâmetros para a chamada na API
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Regiao', regioes)

if regiao == 'Brasil': #como não existe "Brasil" na base, se ele for selecionado, vamos apenas deixar o filtro vazio
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'região': regiao.lower(), 'ano': ano}

response = requests.get(url, params= query_string) #fazendo a requisição à API
dados = pd.DataFrame.from_dict(response.json()) #transformando a resposta em um .json e passando-o para um DataFrame
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique()) 
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


## TABELAS
### Aba Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on= 'Local da compra', right_index=True).sort_values('Preço', ascending=False)
    #removemos duplicadas baseado na coluna 'Local da compra', trouxemos as 3 col, mergeamos este com o dataframe anterior. Right index é pq, ao fazer o merge, a coluna local será o index
 
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))[['Preço']].sum().reset_index() #Agrupando os dados por mês
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Aba Quantidade de Vendas
qtd_vendas_estados = dados.groupby('Local da compra')[['Preço']].count() 
qtd_vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(qtd_vendas_estados, left_on= 'Local da compra', right_index=True).sort_values('Preço', ascending=False)
    #removemos duplicadas baseado na coluna 'Local da compra', trouxemos as 3 col, mergeamos este com o dataframe anterior. Right index é pq, ao fazer o merge, a coluna local será o index
qtd_vendas_estados.rename(columns={'Preço': 'Quantidade de Vendas'}, inplace = True)
 
qtd_vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))[['Preço']].count().reset_index()
qtd_vendas_mensal['Ano'] = qtd_vendas_mensal['Data da Compra'].dt.year
qtd_vendas_mensal['Mes'] = qtd_vendas_mensal['Data da Compra'].dt.month_name()
qtd_vendas_mensal.rename(columns={'Preço': 'Quantidade de Vendas'}, inplace = True)

qtd_vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)
qtd_vendas_categorias.rename(columns={'Preço': 'Quantidade de Vendas'}, inplace = True)

### Aba Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])) #Agregação por soma e contagem


## GRÁFICOS
### Aba Receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon': False}, #não mostrar lat e lon ao passar o mouse
                                  title = 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()), # range de valores do eixo y
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita') # Atualizando o título do eixo Y 

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto= True, #Ligar os rótulos de dados
                             title = 'Top Estados por Receita')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto= True,
                                title = 'Receita por Categoria') 
#Nesse não precisamos passar x e y pq a tabela só tem as duas informações que usaremos
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

### Aba Quantidade de Vendas
fig_mapa_qtd_vendas = px.scatter_geo(qtd_vendas_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Quantidade de Vendas', 
                                  template = 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon': False}, #não mostrar lat e lon ao passar o mouse
                                  title = 'Quantidade de Vendas por Estado')

fig_qtd_vendas_mensal = px.line(qtd_vendas_mensal,
                             x = 'Mes',
                             y = 'Quantidade de Vendas',
                             markers = True,
                             range_y = (0, qtd_vendas_mensal.max()), #range de valores do eixo y
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Quantidade de Vendas Mensal')
fig_qtd_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas') #Atualizando o título do eixo Y

fig_qtd_vendas_estados = px.bar(qtd_vendas_estados.head(),
                             x = 'Local da compra',
                             y = 'Quantidade de Vendas',
                             text_auto= True, #Ligar os rótulos de dados
                             title = 'Top Estados por Quantidade de Vendas')
fig_qtd_vendas_estados.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_qtd_vendas_categorias = px.bar(qtd_vendas_categorias,
                                text_auto= True,
                                title = 'Quantidade de Vendas por Categoria') 
#Nesse não precisamos passar x e y pq a tabela só tem as duas informações que usaremos
fig_qtd_vendas_categorias.update_layout(yaxis_title = 'Quantidade de Vendas')


## VISUALIZAÇÃO NO STREAMLIT
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    col1, col2 = st.columns(2)
    with col1: #utilizando a cláusula with, mas poderíamos escrever apenas "col1." antes da métrica
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$')) #identado para ficar dentro do with
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0])) #pegando o primeiro valor da tupla que shape retorna, que é a quantidade de registros
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1: 
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_qtd_vendas, use_container_width=True)
        st.plotly_chart(fig_qtd_vendas_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtd_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_qtd_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1: 
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (Receita)')
        fig_receita_vendedores.update_layout(yaxis_title = 'Receita')
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                      x = 'count',
                                      y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                      text_auto=True,
                                      title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        fig_vendas_vendedores.update_layout(yaxis_title = 'Quantidade de Vendas')
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)


#st.dataframe(dados)

