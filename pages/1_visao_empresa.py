# -----------------------------------
# Importar bibliotecas
# -----------------------------------
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from datetime import datetime

st.set_page_config(page_title = 'Visão Empresa', page_icon='📈', layout='wide')

# -----------------------------------
# Funções
# -----------------------------------
def clean_code(df1):
    """ Essa função tem a responsabilidade de limpar o dataframe
    
    Tipo de limpeza:
    1. Remoção dos dados NaN
    2. Mudança dos tipos da coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo (remoção do texto da variável numérica) 

    Input: Dataframe
    Output: Dataframe tratado   
    
    """
    df1 = df1.dropna(subset=['Delivery_person_Age', 'Road_traffic_density', 'City', 'Festival', 'Weatherconditions', 'multiple_deliveries'])
    linhas_nao_nulas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_nao_nulas, :]

    linhas_nao_nulas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_nao_nulas, :]

    linhas_nao_nulas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_nao_nulas, :]    
    linhas_nao_nulas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_nao_nulas, :]

    linhas_nao_nulas = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhas_nao_nulas, :]

    linhas_n_nulas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_n_nulas, :]
    df1 = df1.reset_index(drop=True)

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['City'] = df1['City'].astype(str)

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1] if isinstance(x, str) else x)

    df1['ID'] = df1['ID'].str.strip()

    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    df1['City'] = df1['City'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()

    return df1

def order_metric(df1):
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')

    return fig

def traffic_order_share(df1):
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
              .groupby(['Road_traffic_density'])
              .count()
              .reset_index())
    
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()

    fig = px.pie(df_aux, values = 'entregas_perc', names='Road_traffic_density')
                    
    return fig

def traffic_order_city(df1):
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
            .groupby(['City', 'Road_traffic_density'])
            .count()
            .reset_index())
                
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def order_by_week(df1):
    df1['Week_of_Year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'Week_of_Year']].groupby(['Week_of_Year']).count().reset_index()
    fig = px.line(df_aux, x= 'Week_of_Year', y = 'ID')

    return fig

def order_share_by_week(df1):
        df_aux1 = df1.loc[:, ['ID', 'Week_of_Year']].groupby(['Week_of_Year']).count().reset_index()
        df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'Week_of_Year']]
                   .groupby(['Week_of_Year'])
                   .nunique()
                   .reset_index())
        
        df_aux = pd.merge(df_aux1, df_aux2, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
 
        fig = px.line(df_aux, x='Week_of_Year', y='order_by_deliver')

        return fig

def country_maps(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude'] 
    df_aux = (df1.loc[:, cols]
              .groupby(['City','Road_traffic_density'])
              .median()
              .reset_index())

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
          
    folium_static(map, width=1024 , height=600)

# ------------------------------------------------------ Início da estrutura lógica do código ----------------------------------------------------------
# Importar arquivo
# -----------------------------------
df1 = pd.read_csv('train.csv')
df1 = clean_code(df1)

## VISUAIS

# Visão - Empresa

# -----------------------------------
# Barra Lateral
# -----------------------------------

st.header('Marketplace - Visão Cliente')

#image_path = 'C:\\Users\\Estefany\\Documents\\curso_python\\comunidade_ds\\analisando_dados_com_python\\alvo-de-dardos.png'
image = Image.open('alvo-de-dardos.png')

st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury  Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')


date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='YYYY-MM-DD'
)

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# -----------------------------------
# Layout
# -----------------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width = True)            

        with col2:   
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width = True)


with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)


with tab3:
        st.markdown('# Country Maps')
        country_maps(df1)