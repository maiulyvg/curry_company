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

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')


# ============================================================================
#                          DEFINIÇÃO DAS FUNÇÕES
# ============================================================================

def clean_code(df1):
    """" Está função tem a responsabilidade de limpar o dataframe 
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

def order_metric(df1):
    """" Está função tem a responsabilidade de desenhar o gráfico de barras (PRIMEIRO GRÁFICO DA ABA 1)  """
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar( df_aux, x = 'Order_Date', y = 'ID')
    return fig


def traffic_order_share(df1):
    """" Está função tem a responsabilidade de desenhar o gráfico de pizza (SEGUNDO GRÁFICO DA ABA 1)  """
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values= 'entregas_perc', names='Road_traffic_density')
    fig.update_layout(legend_title="Legenda dos Tipos de Tráfego")
    return fig

def traffic_order_city (df1):
    """" Está função tem a responsabilidade de desenhar o gráfico de bolha (TERCEIRO GRÁFICO DA ABA 1)  """
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby( ['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x = 'City', y= 'Road_traffic_density', size= 'ID', color='City')
    fig.update_layout(legend_title="Legenda das modalidades de Cidades")
    return fig

def order_by_week (df1):
    """" Está função tem a responsabilidade de desenhar o gráfico de linha (PRIMEIRO GRÁFICO DA ABA 2)  """
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig

def order_share_by_week (df1):
    """" Está função tem a responsabilidade de desenhar o gráfico de linha (SEGUNDO GRÁFICO DA ABA 2)  """
    df_aux01 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux02 = df1.loc[:,['Delivery_person_ID', 'ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID']/ df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x = 'week_of_year', y='order_by_deliver')
    return fig

def country_maps (df1):
    """" Está função tem a responsabilidade de desenhar o mapa (PRIMEIRO GRÁFICO DA ABA 3)  """
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    fig = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], title={"text": "Localização central de cada cidade por tipo de tráfego", "x": 0.5, "xanchor": "center", "font": {"size": 16, "family": "Arial", "color": "black"}}, popup=location_info[['City', 'Road_traffic_density']]).add_to(fig)
    folium_static(fig, width = 1024, height = 600)
    return None

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
st.markdown('# Marcketplace - Visão Cliente ')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# ======================================
#  Layout Streamlit - Primeira aba
# ======================================

# Visão Gerencial
with tab1:
    with st.container():
        # PRIMEIRO GRÁFICO DA ABA 1
        st.title('Order by Day')
        st.markdown(' ##### Quantidade de pedidos por dia')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    # Divisão do container em duas partes menores
    with st.container():
        st.title('Traffic Order')
        col1, col2 = st.columns(2)
        with col1:
            # SEGUNDO GRÁFICO DA ABA 1
            st.markdown(' ##### Distribuição dos pedidos por tipo de tráfego')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # TERCEIRO GRÁFICO DA ABA 1
            st.markdown(' ##### Comparação do volume de pedidos por cidade e por tipo de tráfego')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)

# ======================================
#   Layout Streamlit - Segunda aba
# ======================================

# Visão Tática            
with tab2:
        st.title('Order by Week')
        with st.container():
            # PRIMEIRO GRÁFICO DA ABA 2
            st.markdown(' ##### Quantidade de pedidos por semana')
            fig = order_by_week(df1)
            st.plotly_chart(fig, use_container_width=True)

        with st.container():
            # SEGUNDO GRÁFICO DA ABA 2
            st.markdown(' ##### Quantidade de pedidos por entregador por semana')
            fig = order_share_by_week (df1)
            st.plotly_chart(fig, use_container_width=True)

# ======================================
#  Layout Streamlit - Terceira aba
# ======================================

# Visão Geográfica
with tab3:
    # PRIMEIRO GRÁFICO DA ABA 3
    st.title('Country Maps')
    st.markdown(' ##### Localização central de cada cidade por tipo de tráfego')
    country_maps (df1)

