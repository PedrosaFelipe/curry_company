import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

# ============================
# Funções
# ============================

            
def avg_std_time_on_traffic(df):
    df_aux = (df.loc[: , ['City' , 'Time_taken(min)', 'Road_traffic_density']].groupby(
                                                                                        ['City', 'Road_traffic_density']).
                                                                                        agg({"Time_taken(min)":['mean' , 'std']}))
    df_aux.columns = ['avg_time' , 'std_time']

    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux , path=['City' , 'Road_traffic_density'], values='avg_time',
                    color='std_time', color_continuous_scale='RdBu',
                    color_continuous_midpoint= np.average(df_aux['std_time']))

    return fig
    
def avg_std_time_graph(df):
    df_aux = df.loc[: , ['City' , 'Time_taken(min)']].groupby('City').agg({"Time_taken(min)":['mean' , 'std']})
    df_aux.columns = ['avg_time' , 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                    x = df_aux['City'],
                    y = df_aux['avg_time'],
                    error_y=dict(type='data' , array=df_aux['std_time']) ))

    fig.update_layout(barmode = 'group')

    return fig

def avg_std_time_delivery(df , op_fest , op ):

    ''' Esta função calcula o tempo médio e o desvio padrão do tempo de entrega tanto em festival quanto em época fora de festivais
        Parêmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - op_fest: Indica se o calculo irá ser contado em tempo de festivaisç
                    'Yes' : Indica que há festivais
                    'No'  : Indica que nao há festivais
                - op: Tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tmepo médio
                    'std_time': Calcula o desvio padrão do tempo   
            Output:
                -df : Dataframe com 2 colunas e 1 linha
    '''

    cols=[ 'Time_taken(min)', 'Festival']

    df_aux = df.loc[: , cols].groupby(['Festival']).agg({"Time_taken(min)":['mean' , 'std']})
    df_aux.columns = ['avg_time' , 'std_time']
    df_aux = df_aux.reset_index()

    df_aux = np.round(df_aux.loc[df_aux['Festival'] == op_fest , op] , 2)

    return df_aux

def distance (df , fig):
    if fig == False:
        cols = ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['distance'] = df.loc[: , cols].apply(lambda x:
                                                haversine((x['Restaurant_latitude'] , x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1)

        avg_distance =np.round(df['distance'].mean() , 2) 
        return avg_distance

    else:
        cols = ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['distance'] = df.loc[: , cols].apply(lambda x:
                                                haversine((x['Restaurant_latitude'] , x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1)

        avg_distance = df.loc[:,['City' , 'distance']].groupby('City').mean().reset_index()

        # pull is given as a fraction of the pie radius

        fig = go.Figure( data=[ go.Pie (labels=avg_distance['City'], values=avg_distance['distance'],pull= [0,0.1,0] )])

        return fig

def clean_code(df):
    """Esta função tem a responsabilidade de limpar o dataframe

    Tipos de Limpeza:
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo`remoção do texto da variável numérica)
    
    Input: Dataframe
    Output: Dataframe
    """

    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip() 
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()    
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()    
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip() 
    df.loc[:, 'multiple_deliveries'] = df.loc[:, 'multiple_deliveries'].str.strip()    
    df.loc[:, 'Delivery_person_Age'] = df.loc[:, 'Delivery_person_Age'].str.strip()    


    # Excluir as linhas com NaN
    # ( Conceitos de seleção condicional )

    df = df.loc[df['multiple_deliveries'] != 'NaN' , :]
    df = df.loc[df['Delivery_person_Age'] != 'NaN' , :]
    df = df.loc[df['Road_traffic_density'] != 'NaN' , :]
    df = df.loc[df['City'] != 'NaN' , :]
    df = df.loc[df['Festival'] != 'NaN' , :]

    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # Limpando a coluna de time taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    df['week_of_year']  = df['Order_Date'].dt.strftime('%U')

    return df

# ============================
# Extração
# ============================

df = pd.read_csv(r'../data/train.csv',  parse_dates = ['Order_Date'] , dayfirst=True)

# cleaning dataset
df = clean_code(df)

# ============================
# Sidebar
# ============================


st.header('Marketplace - Visão Restaurantes')

image_path = '../data/logo.webp'
image = Image.open(image_path)
st.sidebar.image(image , width = 230)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fast Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual data?',
    value = datetime(2022,4,4),
    min_value = datetime(2022,2,11),
    max_value = datetime(2022,4,6),
    format = 'DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low' , 'Medium' , 'High' , 'Jam'],
    default='Low'
)

clima = st.sidebar.multiselect(
    'Quais as condições climaticas?',
    ['conditions Cloudy' , 'conditions Fog' , 'conditions Sandstorms' , 'conditions Stormy' , 'conditions Sunny' , 'conditions Windy'],
    default='conditions Cloudy'
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Felipe Pedrosa')
st.sidebar.markdown('### Comunidade DS')

# filtro de data
df = df.loc[df['Order_Date'] <= date_slider , :]

# filtro de transito
df = df.loc[df['Road_traffic_density'].isin(traffic_options) , : ]

# filtro de transito
df = df.loc[df['Weatherconditions'].isin(clima) , : ]


# ============================
# Layout Streamlit
# ============================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial' , '-' , '-'])

with tab1:
    with st.container():
        st.title('Overal Metrics')

        col1 , col2, col3, col4, col5, col6 = st.columns(6, gap='large')

        with col1:
            delivery_unique = len(df.loc[: , 'Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos' , delivery_unique)
        with col2:
            
            avg_distance = distance(df, False)
            col2.metric('A dist. média entregas' , avg_distance)

        with col3:
           
            df_aux = avg_std_time_delivery(df , 'Yes' , 'avg_time')
            col3.metric('Avg entrega c/ fest.' , df_aux)

        with col4:

            df_aux = avg_std_time_delivery(df , 'Yes' , 'std_time')
            col3.metric('Std entrega c/ fest.' , df_aux)

        with col5:

            df_aux = avg_std_time_delivery(df , 'No' , 'avg_time')
            col3.metric('Avg entrega s/ fest.' , df_aux)

        with col6:

            df_aux = avg_std_time_delivery(df , 'No' , 'std_time')
            col3.metric('Std entrega s/ fest.' , df_aux)


    with st.container():
        st.markdown("""---""")
        st.subheader('Tempo medio de entrega por cidade')
        col1 , col2 = st.columns(2)

        with col1:
        
            fig  = avg_std_time_graph(df)
            st.plotly_chart(fig)

        with col2:
            st.subheader('Distribuição da distância')


            df_aux = df.loc[: , ['City' , 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({"Time_taken(min)":['mean' , 'std']})
            df_aux.columns = ['avg_time' , 'std_time']

            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)



    with st.container():
        st.markdown("""---""")
        st.subheader('Distribuição do tempo')

        col1 , col2 = st.columns(2)
        
        with col1:

            fig = distance(df , True)
            st.plotly_chart(fig)
            
        with col2:
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart(fig)
            
