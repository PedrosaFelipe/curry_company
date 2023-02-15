# Libraries

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine


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



# Visao - Empresa

# colunas
cols = ['ID' , 'Order_Date']
# seleção de linhas
df_aux = df.loc[: , cols].groupby('Order_Date').count().reset_index()
# gráfico de linhas
px.bar(df_aux , x='Order_Date' , y='ID')

print(df.head())

