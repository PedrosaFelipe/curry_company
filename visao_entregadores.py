import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static


# ============================
# Funções
# ============================

def top_delivers(df , top_asc):

    df_aux = (df.loc[: , ['Delivery_person_ID' , 'City' ,'Time_taken(min)']].
                groupby(['Delivery_person_ID' , 'City']).mean().
                sort_values([ 'City' ,'Time_taken(min)'] , ascending = top_asc)).reset_index()


    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)


    df2 = pd.concat([df_aux01 , df_aux02 , df_aux03]).reset_index(drop = True)


    return df2

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


st.header('Marketplace - Visão Entregadores')

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
df = df.loc[df['Order_Date'] < date_slider , :]

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

        col1 , col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df.loc[: , 'Delivery_person_Age'].max()
            col1.metric('Maior idade' , maior_idade)
        with col2:
            menor_idade = df.loc[: , 'Delivery_person_Age'].min()
            col2.metric('Melhor condição' , menor_idade)

        with col3:
            cd_ve_max = df.loc[: , 'Vehicle_condition'].max()
            col3.metric('Pior condição' , cd_ve_max)

        with col4:
            cd_ve_min = df.loc[: , 'Vehicle_condition'].min()
            col4.metric('Menor idade' , cd_ve_min)

    with st.container():
        st.markdown("""---""")
        st.subheader('Avaliações')

        col1 , col2= st.columns(2)
        
        with col1:
            st.markdown("##### Avaliação média por entregas")

            df_avg_rating_per_deliver = (df.loc[: , ['Delivery_person_ID' , 'Delivery_person_Ratings']]
                                                .groupby('Delivery_person_ID').mean().reset_index())
        
            st.dataframe(df_avg_rating_per_deliver)
        with col2:
            st.markdown("##### Avaliação média por tráfego")

            df_avg_std__rating_by_traffic = (df.loc[: , ['Delivery_person_Ratings' , 'Road_traffic_density']]
                                                        .groupby('Road_traffic_density')
                                                        .agg({'Delivery_person_Ratings': ['mean' , 'std']}))
                                                                                                                              
            # mundança de nome das colunas
            df_avg_std__rating_by_traffic.columns = ['delivery_mean' , 'delivery_std']

            # reset do index
            df_avg_std__rating_by_traffic = df_avg_std__rating_by_traffic.reset_index()

            st.dataframe(df_avg_std__rating_by_traffic)

            st.markdown("##### Avaliação média por clima")
                  

            df_avg_std__rating_by_Weather = (df.loc[: , ['Delivery_person_Ratings' , 'Weatherconditions']]
                                                        .groupby('Weatherconditions')
                                                        .agg({'Delivery_person_Ratings': ['mean' , 'std']}))
                                                                                                                                            
            # mundança de nome das colunas
            df_avg_std__rating_by_Weather.columns = ['delivery_mean' , 'delivery_std']

            # reset do index
            df_avg_std__rating_by_Weather = df_avg_std__rating_by_Weather.reset_index()
            st.dataframe(df_avg_std__rating_by_Weather)
            
    with st.container():
        st.markdown("""---""")
        st.subheader('Velcidade de entrega')

        col1 , col2= st.columns(2)
        
        with col1:
            st.markdown("##### Top entregadores mais rápidos")
            df2 = top_delivers(df , top_asc= True)
            st.dataframe(df2)

        with col2:
            st.markdown("##### Top entregadores mais lentos")
            df2 = top_delivers(df , top_asc= False)
            st.dataframe(df2)


