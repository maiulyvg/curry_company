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

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

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

def calculate_big_number(col, operation):
    """ Está função tem a responsabilidade de calcular os cards no topo do dashboard """
    if operation == 'max':
        resultado = df1.loc[:, col].max()
    elif operation == 'min':
        resultado = df1.loc[:, col].min()
    return resultado

def top_delivers (df1, top_asc):
    """ Está função tem a responsabilidade de calcular os  10 entregadores mais rápidos e mais lentos por cidade """
    df_aux1 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).min().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())
    df_aux2 = df_aux1.loc[df_aux1['City'] == 'Metropolitian',:].head(10)
    df_aux3 = df_aux1.loc[df_aux1['City'] == 'Urban',:].head(10)
    df_aux4 = df_aux1.loc[df_aux1['City'] == 'Semi-Urban',:].head(10)
    df_aux = pd.concat([df_aux2, df_aux3, df_aux4]).reset_index(drop=True)
    return df_aux



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

st.markdown('# Marcketplace - Visão Entregadores ')

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

## Terceiro Filtro
st.sidebar.markdown("### Quais as condiççõs climáticas?")
weatherconditions_options = st.sidebar.multiselect(
    'Escolha as opções desejadas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny'])

st.sidebar.markdown("""---""")

# Rodapé
st.sidebar.markdown(" ### Desenvolvido por Maiuly Gomes")

# Conexão do filtro de data com o dataset
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Conexão do filtro de trânsito com o dataset
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Conexão do filtro de condição do tempo com o dataset
linhas_selecionadas = df1['Weatherconditions'].isin(weatherconditions_options)
df1 = df1.loc[linhas_selecionadas, :]

# st.dataframe(df1) # Para demonstração do dataset no streamilit

# =====================================
#  Layout Streamlit - Definição abas            
# =====================================

# Criação das abas
tab1, tab2 = st.tabs(['Visão Gerencial','-'])

# ======================================
#  Layout Streamlit - Primeira aba
# ======================================

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')


        with col1:
            # A maior idade dos entregadores
            number = calculate_big_number('Delivery_person_Age', operation='max')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 15px; font-weight: bold; color: gray;">Maior idade registrada entre os entregadores</p>
                    <p style="margin: 0; font-size: 30px; ;">{number}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            # A menor idade dos entregadores
            number = calculate_big_number('Delivery_person_Age', operation='min')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 15px; font-weight: bold; color: gray;">Menor idade registrada entre os entregadores</p>
                    <p style="margin: 0; font-size: 30px; ;">{number}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            # A melhor nota referente a condicao do veiculo
            number = calculate_big_number('Vehicle_condition', operation='max')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 15px; font-weight: bold; color: gray;">Melhor nota da condição do veículo</p>
                    <p style="margin: 0; font-size: 30px; ;">{number}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
        with col4:
            # A pior nota referente a condicao do veiculo
            number = calculate_big_number('Vehicle_condition', operation='min')
            st.markdown(
                f"""
                <div style="text-align: center; padding: 6px; border-radius: 0px; background-color: #f0f2f6;">
                    <p style="margin: 0; font-size: 15px; font-weight: bold; color: gray;">Pior nota da condição do veículo</p>
                    <p style="margin: 0; font-size: 30px; ;">{number}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
                        
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)

        with col1:
            # Avaliação médida por entregador
            st.markdown(' ##### Avaliação média por Entregador')
            df_avg_ratings_per_person = df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().sort_values(['Delivery_person_Ratings'], ascending =False).reset_index()
            st.dataframe(df_avg_ratings_per_person)

        with col2:
            # Avaliação média e o desvio padrão por tipo de tráfego
            st.markdown(' ##### Avaliação média por tipo de tráfego')
            ratings_per_trafic = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings' : ['mean', 'std']})
            ratings_per_trafic.columns = ['mean_rating_traffic', 'std_rating_traffic']
            ratings_per_trafic = ratings_per_trafic.reset_index()
            st.dataframe(ratings_per_trafic)

            # Avaliação média e o desvio padrão por condições climáticas
            st.markdown(' ##### Avaliação média por tipo de clima')
            ratings_per_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            ratings_per_weather.columns = ['mean_rating_weather', 'std_rating_weather']
            ratings_per_weather = ratings_per_weather.reset_index()
            st.dataframe(ratings_per_weather)

    
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)

        with col1:
            # 10 entregadores mais rápidos por cidade
            df_aux = top_delivers (df1, top_asc=True)
            st.markdown(' ##### Top Entregadores mais rápidos')
            st.dataframe(df_aux)

        with col2:
            # 10 entregadores mais lentos por cidade
            df_aux = top_delivers (df1, top_asc=False)
            st.markdown(' ##### Top Entregadores mais lentos')
            st.dataframe(df_aux)



