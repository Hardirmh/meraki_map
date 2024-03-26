import streamlit  as st
import pandas as pd
import folium
from streamlit import session_state as ss

APP_TITLE = "Monitoreo de POS Oxxo"
APP_SUB_TITLE = "Meraki & AppDynamics"
color_mapping = {
    'Warning': '#FFFF00',
    'Healthy': '#33FF00',
    'Critical': '#FF3300',
}

@st.cache_resource(experimental_allow_widgets=True)
def et():

    data = pd.read_csv('latencyStats.csv')
    data = data.dropna(subset=['lat'])
    data = data.dropna(subset=['Plaza'])
    ##colors = pd.cut(data['best_effort_avg'].to_list(), 4,labels=['hotpink', 'tomato', 'red', 'crimson'])
    #colors = colors.to_list()
    intervals = [0, 35, 75, 100]
    colors = ['#33FF00', '#FFFF00', '#FF3300']
    #AGREGA LA COLUMNA INTERVAL A latencyStats.csv, ASIGNANDOLE UN COLOR SEGUN LOS VALORES DEL INTERVALO
    data['interval'] = pd.cut(data['best_effort_avg'].to_list(), bins=intervals, labels=colors)
    return data

@st.cache_resource(experimental_allow_widgets=True)
def show_map(data):
    m = folium.Map(location=[data["lat"].mean(), data["lon"].mean()], zoom_start=5)

    colors = ['#33FF00', '#FFFF00', '#FF3300']
    features = {}
    for row in colors:
        features[row] = folium.FeatureGroup(name=row)

    for row in data.iterrows():
        folium.Circle(
            location = [row['lat'], row['lon']],
            radius = 10000,
            color=row['interval'],
            fill_color=row['interval'],
            min_opacity=0.3,
        ).add_child(folium.Popup(row['Tienda'])).add_to(m)
 
##AGREGA LSO COLORES AL MAPA
    for row in colors:
        features[row].add_to(m)
        
    folium.LayerControl().add_to(m)

def style_multiselect_widget(color):
    #Color_mapping es una variable global
    # Default to white if not found
    color_code = color_mapping.get(color, '#FFFFFF')  
    css = f"""
        <style>
            .st-dd .st-eb .st-ag .st-de {{
                background-color: {color_code};
                color: white;  /* Set text color to white for better visibility */
            }}
        </style>
    """
    st.write(css, unsafe_allow_html=True)

def main():
    st.set_page_config(APP_TITLE,layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    df = et()
    zonas=df['Zona'].unique().tolist()
    zona = st.sidebar.multiselect("Selecciona zona",zonas)
    color = st.sidebar.multiselect("Selecciona alerta",list(color_mapping.keys()))
    
    cs = []
    for i in range(len(color)):
        cs.append(color_mapping[color[i]])

    if color:
        for c in color:
            style_multiselect_widget(c)
            
    if (zona == []) & (cs == []):
        st.sidebar.write(df)
        show_map(df)
        
    elif zona != []:
        if cs != []:
            st.sidebar.write(df[(df['Zona'].isin(zona)) & (df['interval'].isin(cs))])
            show_map(df[(df['Zona'].isin(zona)) & (df['interval'].isin(cs))])
        else:
            st.sidebar.write(df[df['Zona'].isin(zona)])
            show_map(df[df['Zona'].isin(zona)])
    elif cs != []:
        st.sidebar.write(df[df['interval'].isin(cs)])
        show_map(df[df['interval'].isin(cs)])

if __name__ == "__main__":
    main()

