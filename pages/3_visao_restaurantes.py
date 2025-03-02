# ============================================================================
#                       IMPORTAÇÃO DE BIBLIOTECAS
# ============================================================================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
import folium
from PIL import Image
from streamlit_folium import folium_static
from datetime import datetime
import numpy as np

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

# ============================================================================
#                          DEFINIÇÃO DAS FUNÇÕES
# ============================================================================

def clean_code(df1):
    """ Está função tem a responsabilidade de limpar o dataframe 
         Tipos de limpeza:
         1. Remoção dos NaN
         2. Mudança do tipo da coluna de dados
         3. Remoção dos espaços das variáveis de texto
         4. Formatação da coluna de datas
         5. Limpeza da coluna de tempo (remoção do texto da variável númerica)

         Input: Dataframe
         Output: Dataframe

         1. Remoção dos NaN        
         2. Mudança do tipo da coluna de dados
         3. Remoção dos espaços das variáveis de texto
         4. Formatação da coluna de data
         5. Limpeza da coluna de tempo (remoção do texto da variável númerica)

    """
    
    # Passo 1 da limpeza: Limpeza dos valores NaN das colunas
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN ', :]
    df1 = df1.loc[df1['City'] != 'NaN ', :]
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN ', :]
    df1 = df1.loc[df1['Weatherconditions'] != 'conditions NaN', :]
    df1 = df1.loc[df1['Festival'] != 'NaN ', :]
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :]
    df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ', :]

    # Passo 2.  Mudança do tipo da coluna de dados
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int ) #Convertendo a coluna Age de texto para número
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float ) #Convertendo a coluna Ratings de texto para número decimal (float)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int ) #Convertendo multiple_deliveries de texto para numero interior (int)

    # Passo 3: Remoção dos espaços das variáveis de texto
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # Passo 4: Formatação da coluna de data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y') # Convertendo a coluna order_date de texto para data
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U') #Criação da coluna de semana, que vai de 1 a 52

    # Passo 5: Limpeza da coluna de tempo (remoção do texto da variável númerica)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split ('(min)')[1]) #Limpando o (min) da coluna Time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1


def distance(df1, resultado_img):
    """ - Opção resultado_img == False tem a responsabilidade de calcular a distância média dos resturantes aos locais de entrega via card
        - Opção resultado_img == True tem a responsabilidade de calcular a distância média dos resturantes aos locais de entrega via grafico"""
    if resultado_img == False:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, colunas].apply(lambda x:  haversine ((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
        distancia_media = np.round(df1['distance'].mean(), 2)
        return distancia_media
    else:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, colunas].apply(lambda x:  haversine ((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)      
        distancia_media = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=distancia_media['City'], values=distancia_media['distance'], pull=[0, 0.05,0])])
        return fig


def avg_std_time_delivery(df1, operation, festival):
    """ Está função tem a responsabilidade de calcular o tempo médio e o desvio padrão do tempo de entrega durantes os Festivais
        Parâmetros:
            Input: 
            - df: Dataframe com os dados necessários para o cálculo
            - operation: Tipo de operação que precisa ser calculada
                'avg_time':  cálcula o tempo médio
                'std_time':  cálcula o desvio padrão do tempo
            Output:
                - df: Dataframe com 2 colunas e 1 linha
     """
    df_aux = df1.loc[:,['Festival' , 'Time_taken(min)']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, operation],2)
    valor = df_aux.values[0]
    return valor

def avg_std_time_graph_table (df1, resultado_img):
    """  - Opção resultado_img == True tem a responsabilidade de desenhar o gráfico da distribuição do tempo por cidade
         - Opção resultado_img == False tem a responsabilidade de desenhar a tabela da distribuição do tempo por cidade e tipo de pedido  """
    if resultado_img == True:
        df_aux = df1.loc[:,['City' , 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
        df_aux.columns = ['avg_time_city', 'std_time_city']
        df_aux = df_aux.reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time_city'], error_y=dict(type='data', array=df_aux['std_time_city'])))
        fig.update_layout(barmode='group')
        return fig
    else:
        fig = df1.loc[:,['City' , 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
        fig.columns = ['avg_time_city_pedido', 'std_time_city_pedido']
        fig.reset_index()
        st.dataframe(fig)

def avg_std_time_on_traffic (df1):
    """ Está função tem a responsabilidade de desenhar o gráfico do Tempo médio por Tipo de Tráfego """
    df_aux = df1.loc[:,['City' , 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['avg_time_city_trafico', 'std_time_city_trafico']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time_city_trafico', color='std_time_city_trafico', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time_city_trafico']))
    return fig


# ============================================================================
#                        LÓGICA DO CÓDIGO
# ============================================================================

# =====================================
#       Importação do Dataset                    
# =====================================
df = pd.read_csv ('dataset/train.csv')
df1 = df.copy() # Backup do dataframe

# =====================================
#       Limpeza dos dados                
# =====================================
df1 = clean_code(df1)

# =====================================
#  Layout Streamlit - Barra Lateral               
# =====================================
st.markdown('# Marcketplace - Visão Restaurantes')

# Importação do logo
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

# Criação do Menu a esquerda
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

## Primeiro Filtro
st.sidebar.markdown("### Selecione uma data limite")
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime( 2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

## Segundo Filtro
st.sidebar.markdown("### Quais as condições do trânsito?")
traffic_options = st.sidebar.multiselect(
    'Escolha as opções desejadas',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")

# Rodapé
st.sidebar.markdown(" ### Desenvolvido por Maiuly Gomes")

# Conexão do filtro de data com o dataset
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Conexão do filtro de trânsito com o dataset
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# st.dataframe(df1) # Para demonstração do dataset no streamilit

# =====================================
#  Layout Streamlit - Definição abas            
# =====================================

# Criação das abas
tab1, tab2 = st.tabs(['Visão Gerencial', '-'])

# ======================================
#  Layout Streamlit - Primeira aba
# ======================================

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            # Quantidade de entregadores únicos
            qtde_entregadores = len(df1.loc[:,'Delivery_person_ID'].unique())
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 13px; font-weight: bold; color: gray;">N° Entregadores existentes</p>
                    <p style="margin: 0; font-size: 30px; ;">{qtde_entregadores}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            # Distância média dos resturantes e dos locais de entrega
            distancia_media = distance(df1,resultado_img=False)
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 13px; font-weight: bold; color: gray;">Distância Média de descolamento</p>
                    <p style="margin: 0; font-size: 30px; ;">{distancia_media}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            # Tempo médio de entrega durantes os Festivais
            valor = avg_std_time_delivery(df1, operation='avg_time', festival='Yes ')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 10px; font-weight: bold; color: gray;">Tempo médio de descolamento com Festival</p>
                    <p style="margin: 0; font-size: 30px; ;">{valor}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


        with col4:
            # Desvio padrão do Tempo de entrega com Festival
            valor = avg_std_time_delivery(df1, operation='std_time', festival='Yes ')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 10px; font-weight: bold; color: gray;">STD do Tempo de descolamento com Festival</p>
                    <p style="margin: 0; font-size: 30px; ;">{valor}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


        with  col5:
            # Tempo de entrega médio sem Festival
            valor = avg_std_time_delivery(df1, operation='avg_time', festival='No ')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 10px; font-weight: bold; color: gray;">Tempo médio de descolamento sem Festival</p>
                    <p style="margin: 0; font-size: 30px; ;">{valor}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


        with col6:
            # Desvio padrão do Tempo de entrega sem Festival
            valor = avg_std_time_delivery(df1, operation='std_time', festival='No ')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 10px; font-weight: bold; color: gray;">STD do Tempo de descolamento sem Festival</p>
                    <p style="margin: 0; font-size: 30px; ;">{valor}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("""---""")
    st.title('Distribuição pelo Tempo')
    with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Gráfico de barras - Distribuição do Tempo por Cidade
                st.markdown(' ##### Distribuição do Tempo por Cidade')
                fig = avg_std_time_graph_table (df1, resultado_img=True)
                st.plotly_chart(fig)
                
            with col2:
                # Tabela - Tempo de entrega médio e desvio padrão por cidade e tipo de pedido
                st.markdown(' ##### Tempo de entrega médio e desvio padrão por cidade e tipo de pedido')
                fig = avg_std_time_graph_table (df1, resultado_img=False)
                st.dataframe(fig)

    st.markdown("""---""")
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza - Tempo médio de entrega por Cidade
            st.markdown(' ##### Tempo médio de entrega por Cidade')
            fig = distance(df1,resultado_img=True)
            st.plotly_chart(fig)

        with col2:
            # Gráfico de sol - Tempo médio por Tipo de Tráfego
            st.markdown(' ##### Tempo médio por Tipo de Tráfego')
            fig = avg_std_time_on_traffic (df1)
            st.plotly_chart(fig)
