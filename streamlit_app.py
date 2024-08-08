##################################
# Import libraries 
import streamlit as st 
import pandas as pd 
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import altair as alt
import referencing.jsonschema
from folium import Popup
#################################

st.set_page_config(
    page_title='Disponibilidad de medicamentos en establecimientos de salud Peru',
    page_icon="💊",
    layout='wide',
    initial_sidebar_state='expanded'
)

#################################
# Loading data to create the sidebar and filters
filtros = pd.read_excel('data/sidebar.xlsx')

################################
# Sidebar
with st.sidebar:
    st.title('🏥💊 Disponibilidad de Medicamentos - Peru')
    
    year_list = [2019, 2020, 2021, 2022, 2023, 2024]
    
    selected_year = st.selectbox('Selecciona un año', year_list, index=len(year_list)-1)
    
    depart_list = ['AMAZONAS', 'CAJAMARCA', 'AREQUIPA', 'AYACUCHO', 'APURIMAC',
       'ANCASH', 'HUANUCO', 'ICA', 'HUANCAVELICA', 'CUSCO', 'CALLAO',
       'UCAYALI', 'TUMBES', 'SANMARTIN', 'TACNA', 'PUNO', 'PIURA',
       'PASCO', 'LORETO', 'MOQUEGUA', 'MADREDEDIOS', 'LIMA', 'LALIBERTAD',
       'JUNIN', 'LAMBAYEQUE']
    
    selected_depart = st.selectbox('Selecciona el departamento', depart_list)

#################################

# Donut chart
def assign_color(idm_value):
    if idm_value >= 90:
        return ['#27AE60', '#12783D']  # Verde
    elif idm_value >= 70:
        return ['#F39C12', '#875A12']  # Amarillo
    elif idm_value >= 50:
        return ['#E67E22', '#B35418']  # Naranja
    else:
        return ['#E74C3C', '#781F16']  # Rojo

def make_donut(idm_value, departamento):
    chart_color = assign_color(idm_value)
    
    source = pd.DataFrame({
        "Topic": ['', departamento],
        "% value": [100 - idm_value, idm_value]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', departamento],
        "% value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta=alt.Theta("% value", type="quantitative"),
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[departamento, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    text = plot.mark_text(align='center', color=chart_color[0], font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(
        text=alt.value(f'{idm_value} %')
    )
    
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta=alt.Theta("% value", type="quantitative"),
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[departamento, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    return plot_bg + plot + text

# Calculation IDM by year and department

def calculate_idm_by_depart_year(input_df, input_year, input_depart):
    selected_IDM_depart_year = input_df[(input_df['departamento'] == input_depart) & (input_df['año'] == input_year)]['IDM'].round(0).values
    if len(selected_IDM_depart_year) > 0:
        return selected_IDM_depart_year[0]
    else:
        return None
###################################

# Loading all the data

#IDM col 0
idm_anual_data = pd.read_excel('data/IDM_anual.xlsx')
idm_anual_hosp = pd.read_excel('data/IDM_anual_hospitales.xlsx')
idm_anual_cen = pd.read_excel('data/IDM_anual_centros.xlsx')
idm_anual_pue = pd.read_excel('data/IDM_anual_puestos.xlsx')

# map of IDM 
#

#dep = gpd.read_file('data/LIMITE_DEPARTAMENTO/LIMITE_DEP.shp')
geo_idm = pd.read_excel('data/geo_idm_anual.xlsx')
geo_idm['Coordenadas'] = geo_idm.apply(lambda row: (row['latitud'], row['longitud']), axis=1)

#
## Verificar si las columnas latitud y longitud existen y tienen datos válidos
#if 'latitud' not in geo_idm.columns or 'longitud' not in geo_idm.columns:
#    st.error("Las columnas 'latitud' y 'longitud' no existen en el DataFrame.")
#else:
#    if geo_idm[['latitud', 'longitud']].isnull().any().any():
#        st.error("Hay valores nulos en las columnas 'latitud' y 'longitud'.")
#    else:
#        ####################################
#        # Dashboard Main Panel
#        col = st.columns((1.5, 4.5, 2), gap='medium')
#
col = st.columns((1.5, 4.5, 2), gap='medium')

def style_function(feature):
    return {
        'fillOpacity': 0,      # Hacer la capa de relleno transparente
        'color': 'black',      # Color de la línea
        'weight': 1            # Grosor de la línea
    }

if 'latitud' not in geo_idm.columns or 'longitud' not in geo_idm.columns:
    st.error("Las columnas 'latitud' y 'longitud' no existen en el DataFrame.")
else:
    if geo_idm[['latitud', 'longitud']].isnull().any().any():
        st.error("Hay valores nulos en las columnas 'latitud' y 'longitud'.")
    else:
        ####################################
        # Dashboard Main Panel
        col = st.columns((1.5, 4.5, 2), gap='medium')

        with col[0]:
            st.markdown('#### IDM Anual Departamental')
            
            IDM_anual = calculate_idm_by_depart_year(idm_anual_data, selected_year, selected_depart)
            IDM_anual_hosp = calculate_idm_by_depart_year(idm_anual_hosp, selected_year, selected_depart)
            IDM_anual_cen = calculate_idm_by_depart_year(idm_anual_cen, selected_year, selected_depart)
            IDM_anual_pue = calculate_idm_by_depart_year(idm_anual_pue, selected_year, selected_depart)

            idm_donut_total_chart = make_donut(IDM_anual, selected_depart)
            idm_donut_hosp_chart = make_donut(IDM_anual_hosp, selected_depart)
            idm_donut_cen_chart = make_donut(IDM_anual_cen, selected_depart)
            idm_donut_pue_chart = make_donut(IDM_anual_pue, selected_depart)
            
            st.write('IDM Anual Total')
            st.altair_chart(idm_donut_total_chart, use_container_width=True)
            
            st.write('IDM Anual Total - Hospitales')
            st.altair_chart(idm_donut_hosp_chart, use_container_width=True)
            
            st.write('IDM Anual Total - Centros')
            st.altair_chart(idm_donut_cen_chart, use_container_width=True)
            
            st.write('IDM Anual Total - Puestos')
            st.altair_chart(idm_donut_pue_chart, use_container_width=True)

        with col[1]:
            # Filtrar datos según el año y el departamento seleccionados
            filtered_data = geo_idm[(geo_idm['año'] == selected_year) & (geo_idm['departamento'] == selected_depart)]

            # Crear el mapa de Folium
            m = folium.Map(location=[-9.19, -75.0152], tiles='cartodbpositron', zoom_start=7)
            #folium.GeoJson(dep, style_function=style_function).add_to(m)

            # Crear grupos de capas para los diferentes tipos de establecimientos
            hospital_layer = folium.FeatureGroup(name="Hospital")
            centro_layer = folium.FeatureGroup(name="Centro de salud")
            puesto_layer = folium.FeatureGroup(name="Puesto de Salud")
            otro_layer = folium.FeatureGroup(name="Otro")

            for idx, row in filtered_data.iterrows():
                nombre = row['establec']
                tipo_establecimiento = row['tipo']
                disponibilidad = row['dispo']
                lat = row['latitud']
                lon = row['longitud']

                # Crear contenido HTML para el popup
                popup_content = f"""
                <b>Nombre:</b> {nombre}<br>
                <b>Tipo de Establecimiento:</b> {tipo_establecimiento}<br>
                <b>Disponibilidad:</b> {disponibilidad}%
                """
                popup = folium.Popup(popup_content, max_width=300)

                marker = folium.Circle(location=[lat, lon], radius=5, popup=popup, fill=True)

                if tipo_establecimiento == "Hospital":
                    marker.add_to(hospital_layer)
                elif tipo_establecimiento == "Centro de salud":
                    marker.add_to(centro_layer)
                elif tipo_establecimiento == "Puesto de Salud":
                    marker.add_to(puesto_layer)
                else:
                    marker.add_to(otro_layer)

            hospital_layer.add_to(m)
            centro_layer.add_to(m)
            puesto_layer.add_to(m)
            otro_layer.add_to(m)

            folium.LayerControl().add_to(m)

            st.markdown('### Mapa de Disponibilidad de medicinas por establecimiento de salud')
            st_folium(m, width=600)