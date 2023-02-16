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


df = pd.read_csv(r'../data/train.csv',  parse_dates = ['Order_Date'] , dayfirst=True)

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
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas , :]

# filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas , :]

# filtro de transito
linhas_selecionadas = df['Weatherconditions'].isin(clima)
df = df.loc[linhas_selecionadas , :]

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
            cols = ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude', 'Delivery_location_longitude']
            df['distance'] = df.loc[: , cols].apply(lambda x:
                                                    haversine((x['Restaurant_latitude'] , x['Restaurant_longitude']),
                                                                (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1)

            avg_distance =np.round(df['distance'].mean() , 2) 
            col2.metric('A dist. média entregas' , avg_distance)


        with col3:
            cols=[ 'Time_taken(min)', 'Festival']

            df_aux = df.loc[: , cols].groupby(['Festival']).agg({"Time_taken(min)":['mean' , 'std']})
            df_aux.columns = ['avg_time' , 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes' , 'avg_time'] , 2)

            col3.metric('Avg entrega c/ fest.' , df_aux)

        with col4:
            cols=[ 'Time_taken(min)', 'Festival']

            df_aux = df.loc[: , cols].groupby(['Festival']).agg({"Time_taken(min)":['mean' , 'std']})
            df_aux.columns = ['avg_time' , 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes' , 'std_time'] , 2)

            col3.metric('Std entrega c/ fest.' , df_aux)

        with col5:
            cols=[ 'Time_taken(min)', 'Festival']

            df_aux = df.loc[: , cols].groupby(['Festival']).agg({"Time_taken(min)":['mean' , 'std']})
            df_aux.columns = ['avg_time' , 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No' , 'avg_time'] , 2)

            col3.metric('Avg entrega s/ fest.' , df_aux)
        with col6:
            cols=[ 'Time_taken(min)', 'Festival']

            df_aux = df.loc[: , cols].groupby(['Festival']).agg({"Time_taken(min)":['mean' , 'std']})
            df_aux.columns = ['avg_time' , 'std_time']
            df_aux = df_aux.reset_index()

            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No' , 'std_time'] , 2)

            col3.metric('Std entrega s/ fest.' , df_aux)



    with st.container():
        st.markdown("""---""")
        st.subheader('Tempo medio de entrega por cidade')
        col1 , col2 = st.columns(2)

        with col1:
            df_aux = df.loc[: , ['City' , 'Time_taken(min)']].groupby('City').agg({"Time_taken(min)":['mean' , 'std']})
            df_aux.columns = ['avg_time' , 'std_time']

            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control',
                            x = df_aux['City'],
                            y = df_aux['avg_time'],
                            error_y=dict(type='data' , array=df_aux['std_time']) ))

            fig.update_layout(barmode = 'group')

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
            cols = ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude', 'Delivery_location_longitude']
            df['distance'] = df.loc[: , cols].apply(lambda x:
                                                    haversine((x['Restaurant_latitude'] , x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1)

            
            avg_distance = df.loc[:,['City' , 'distance']].groupby('City').mean().reset_index()

            # pull is given as a fraction of the pie radius

            fig = go.Figure( data=[ go.Pie (labels=avg_distance['City'], values=avg_distance['distance'],pull= [0,0.1,0] )])
            st.plotly_chart(fig)
            


        with col2:
            
            df_aux = (df.loc[: , ['City' , 'Time_taken(min)', 'Road_traffic_density']].groupby(
                                                                                                ['City', 'Road_traffic_density']).
                                                                                                agg({"Time_taken(min)":['mean' , 'std']}))
            df_aux.columns = ['avg_time' , 'std_time']

            df_aux = df_aux.reset_index()
            fig = px.sunburst(df_aux , path=['City' , 'Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint= np.average(df_aux['std_time']))

            st.plotly_chart(fig)
            
