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
import numpy as np

st.set_page_config(page_title = 'Visão Restaurantes', page_icon='🍕', layout='wide')

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

def distance(df1, fig):
            if fig == False:
                colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
                df1['distance'] = (df1.loc[:, colunas].apply(lambda x:
                                                haversine(
                                                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
                                                axis = 1)) 
                avg_distance = np.round(df1['distance'].mean(), 2)

                return avg_distance
            
            else:
                colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
                df1['distance'] = (df1.loc[:, colunas].apply(lambda x:
                                                haversine(
                                                    (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
                                                    axis = 1))
                avg_distance = (df1.loc[:, ['City', 'distance']]
                                .groupby('City')
                                .mean()
                                .reset_index())
                fig = go.Figure(data = [go.Pie(labels=avg_distance['City'], values = avg_distance['distance'], pull=[0,0.05,0])])

                return fig                

def avg_std_time_delivery(df1, festival, op):
    '''
        A função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - op: Tipo de operação que precisa ser calculado:
                    'avg_time': calcula o tempo médio
                    'std_time': calcula o desvio padrão do tempo
            Output:
                - df: Dataframe com 2 colunas e 1 linha    
    '''
    df_aux = (df1.loc[:, ['Festival', 'Time_taken(min)']]
            .groupby('Festival')
            .agg({'Time_taken(min)': ['mean', 'std']}))
            
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux

def avg_std_time_graph(df1):
    tempo = (df1.loc[:, ['City', 'Time_taken(min)']]
            .groupby('City')
            .agg({'Time_taken(min)': ['mean', 'std']}))
    tempo.columns = ['tempo_medio', 'tempo_std']
    tempo = tempo.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control',
                        x = tempo['City'],
                        y = tempo['tempo_medio'],
                        error_y = dict(type='data', array=tempo['tempo_std'])))                       
    fig.update_layout(barmode='group')

    return fig

def avg_std_time_on_traffic(df1):
    tempo = (df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
            .groupby(['City', 'Road_traffic_density'])
            .agg({'Time_taken(min)': ['mean', 'std']}))
    tempo.columns = ['tempo_medio', 'tempo_std']
    tempo = tempo.reset_index()
    fig = px.sunburst(tempo, path=['City', 'Road_traffic_density'], values='tempo_medio',
                    color='tempo_std', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(tempo['tempo_std']))
    
    return fig


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

st.header('Marketplace - Visão Restaurantes')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            unicos = df1.loc[:, 'Delivery_person_ID'].nunique() 
            col1.metric('Entregadores', unicos)

        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('Distância Avg', avg_distance)

        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Avg Entrega Fest', df_aux)

        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('Std Entrega Fest', df_aux)            

        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Avg Entrega', df_aux)

        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('Std Entrega', df_aux) 

    with st.container():
        st.markdown('''---''')
        st.title('Tempo Médio de Entregas por Cidade')

        fig = distance(df1, fig=True)
        st.plotly_chart(fig)

    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do Tempo')

        col1, col2 = st.columns(2)
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)

        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)

    with st.container():
        st.markdown('''---''')
        st.title('Distribuição da Distância')

        tempo = (df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']]
                .groupby(['City', 'Type_of_order'])
                .agg({'Time_taken(min)': ['mean', 'std']}))
        tempo.columns = ['tempo_medio', 'tempo_std']
        tempo.reset_index()
        st.dataframe(tempo)
