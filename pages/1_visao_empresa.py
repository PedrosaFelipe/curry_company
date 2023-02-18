# Libraries

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

def maps(df):
	df_aux = df.loc[: , ['City','Road_traffic_density' , 'Delivery_location_latitude' , 'Delivery_location_longitude']].groupby(['City' , 'Road_traffic_density']).median().reset_index()
	map_ = folium.Map()
	for index , location_info in df_aux.iterrows():
		folium.Marker([location_info['Delivery_location_latitude'] , 
					location_info['Delivery_location_longitude']],
					popup = location_info[['City' , 'Road_traffic_density']]).add_to(map_)

	folium_static(map_ , width=1024 , height=600)

	return None

def order_share_by_week(df):
	df_aux01 = df.loc[: , ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
	df_aux02 = df.loc[: , ['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()

	df_aux = pd.merge(df_aux01 , df_aux02 , how='inner')
	df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

	fig = px.line(df_aux , x='week_of_year' , y='order_by_deliver')

	return fig

def order_by_week(df):
	# criar coluna de semanas
	df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
	df_aux = df.loc[: , ['ID' , 'week_of_year']].groupby('week_of_year').count().reset_index()

	# gráfico de linhas
	fig = px.line(df_aux , x='week_of_year' , y='ID')	

	return fig

def traffic_order_city(df):
	df_aux = df.loc[: , ['ID' ,'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
	fig = px.scatter(df_aux , x='City' , y='Road_traffic_density' , size = 'ID' ,  color='City')

	return fig

def traffic_order_share(df):
	df_aux = df.loc[: , ['ID' , 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
	df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

	# gráfico de pizza
	fig = px.pie(df_aux , values = 'entregas_perc' , names = 'Road_traffic_density')

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

def order_metric(df):
			
	cols = ['ID' , 'Order_Date']
	# seleção de linhas
	df_aux = df.loc[: , cols].groupby('Order_Date').count().reset_index()
	# gráfico de linhas
	fig = px.bar(df_aux , x='Order_Date' , y='ID')

	return fig 

# ============================
# Extração
# ============================

df = pd.read_csv(r'../data/train.csv',  parse_dates = ['Order_Date'] , dayfirst=True)

# cleaning dataset
df = clean_code(df)

# ============================
# Sidebar
# ============================


st.header('Marketplace - Visão Cliente')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial' , 'Visão Tática' , 'Visão Geográfica'])

with tab1:
	with st.container():
		
		st.markdown('# Orders by day')
		fig = order_metric(df)
		st.plotly_chart(fig, use_container_width=True)

	with st.container():

		cols1 , cols2 = st.columns(2)
		with cols1:
			st.header(' Traffic Order Share')
			fig = traffic_order_share(df)
			st.plotly_chart(fig, use_container_width=True)


		with cols2:
			st.header('Traffic Order City')
			fig = traffic_order_city(df)
			st.plotly_chart(fig, use_container_width=True)

with tab2:   
	with st.container():
		st.markdown('# Order by week')
		fig = order_by_week(df)
		st.plotly_chart(fig, use_container_width=True)

	with st.container():
		# qdade de pedidos por semana / número único de entregadores por semana
		st.markdown('# Order share by week')
		fig = order_share_by_week(df)
		st.plotly_chart(fig, use_container_width=True)

with tab3:
	st.markdown('# Country Maps')
	maps(df)




	