## IMPORTAÇÃO DAS BIBLIOTECAS
import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data # armazena o arquivo em cache
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso', icon="✅")
    time.sleep(5) #timer de 5 segundos
    sucesso.empty() #apaga a mensagem após o timer

st.title('DADOS BRUTOS :shopping_trolley:')

## DADOS
url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

### Estrutura dos filtros
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

with st.sidebar:
    st.title('Filtros')
    with st.expander('Nome do produto'):
        produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
    with st.expander('Preço do produto'):
        preco = st.slider('Selecione o preço', 0, 5000, (0, 5000)) #tupla (0,5000) define o valor padrão mínimo e máximo, em vez de passar um só valor
    with st.expander('Data da compra'):
        data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
    with st.expander('Categoria do produto'):
        categoria = st.multiselect('Selecione a categoria', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
    with st.expander('Valor do frete'):
        frete = st.slider('Selecione o preço do frete', dados['Frete'].min(), dados['Frete'].max(), (dados['Frete'].min(), dados['Frete'].max()))
    with st.expander('Vendedores'):
        vendedor = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
    with st.expander('Local da compra'):
        local_compra = st.multiselect('Selecione o local', dados['Local da compra'].unique(), dados['Local da compra'].unique())
    with st.expander('Avaliação da compra'):
        avaliacao = st.multiselect('Selecione a avaliação', dados['Avaliação da compra'].unique(), dados['Avaliação da compra'].unique())
    with st.expander('Tipo de pagamento'):
        tipo_pgto = st.multiselect('Selecione o tipo de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
    with st.expander('Quantidade de parcelas'):
        parcelas = st.slider('Quantidade de parcelas', dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max(), (dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max()))

### Filtragem
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
`Categoria do Produto` in @categoria and \
@frete[0] <= Frete <= @frete[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local_compra and \
`Avaliação da compra` in @avaliacao and \
`Tipo de pagamento` in @tipo_pgto and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas filtradas')

st.markdown('Escreva um nome para o arquivo')
col1, col2 = st.columns(2)
with col1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with col2:
    st.download_button('Download', data = converte_csv(dados_filtrados), file_name=nome_arquivo, mime = 'text/csv', on_click=mensagem_sucesso)
    
