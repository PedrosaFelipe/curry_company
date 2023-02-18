import streamlit as  st
from PIL import  Image  

st.set_page_config(
    page_title="Home",
)

image_path =  'data/logo.png'
image = Image.open(image_path)
st.sidebar.image(image , width = 230)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fast Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Felipe Pedrosa')
st.sidebar.markdown('### Comunidade DS')

st.write('# Curry Company Growth Dashboard')

st.markdown(
"""
Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
### Como utilizar esse Growth Dashboard?
- Visão Empresa:
    - Visão Gerencial : Métricas gerais de comportamento diário.
    - Visão Tática : Indicadores semanais de crescimento.
    - Visão Geográfica : Insights de geocalização.
 - Visão Entregador:
    - Visão Gerencial : Acompanhamento dos indicadores semanais de crescimento dos entregadores.
- Visão Restauantes:
    - Visão Gerencial : Acompanhamento dos indicadores semanais de crescimento dos restaurantes.
### Ask fo Help
- Time de Data Science no Discord
    -@felipe pedrosa

"""
)