##################################
# Import libraries 
import openpyxl
import streamlit as st 
import pandas as pd 
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
#################################

st.set_page_config(
    page_title='Disponibilidad de medicamentos en establecimientos de salud Peru',
    page_icon="💊",
    layout='wide',
    initial_sidebar_state='expanded'
)

#################################
# Cache the loading of data to improve performance
@st.cache_data
def load_data(file_path, columns=None):
    return pd.read_excel(file_path, usecols=columns)

# Load data
filtros = load_data('data/sidebar.xlsx')
idm_anual_data = load_data('data/IDM_anual.xlsx')
idm_anual_hosp = load_data('data/IDM_anual_hospitales.xlsx')
idm_anual_cen = load_data('data/IDM_anual_centros.xlsx')
idm_anual_pue = load_data('data/IDM_anual_puestos.xlsx')
geo_idm = load_data('data/geo_idm_anual.xlsx')
idm_hospitales = load_data('data/data_lineplot_hosp.xlsx')
idm_centros = load_data('data/data_lineplot_centros.xlsx')
idm_puestos = load_data('data/data_lineplot_puestos.xlsx')
ranking = load_data('data/ranking_medicamentos_desabastecidos.xlsx', columns=['departamento', 'año', 'nombre_med_grupo'])

################################
# Sidebar
with st.sidebar:
    st.title('🏥💊 Disponibilidad de Medicamentos - Peru')
    with st.expander('¿Qué es el IDM?', expanded=True):
        st.write('''
            El **Índice de Disponibilidad de Medicamentos (IDM)** es un indicador que mide la disponibilidad de medicamentos esenciales en un sistema de salud.
        ''')
        st.latex(r'''
        IDM = \frac{\text{N\degree de medicamentos disponibles}}{\text{N\degree total de medicamentos requeridos}} \times 100
        ''')
    year_list = [2019, 2020, 2021, 2022, 2023, 2024]
    
    selected_year = st.selectbox('Selecciona un año', year_list, index=len(year_list)-1)
    
    depart_list = sorted([
        'AMAZONAS', 'CAJAMARCA', 'AREQUIPA', 'AYACUCHO', 'APURIMAC',
        'ANCASH', 'HUANUCO', 'ICA', 'HUANCAVELICA', 'CUSCO', 'CALLAO',
        'UCAYALI', 'TUMBES', 'SANMARTIN', 'TACNA', 'PUNO', 'PIURA',
        'PASCO', 'LORETO', 'MOQUEGUA', 'MADREDEDIOS', 'LIMA', 'LALIBERTAD',
        'JUNIN', 'LAMBAYEQUE'
    ])
    
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
@st.cache_data
def calculate_idm_by_depart_year(input_df, input_year, input_depart):
    selected_IDM_depart_year = input_df[(input_df['departamento'] == input_depart) & (input_df['año'] == input_year)]['IDM'].round(0).values
    if len(selected_IDM_depart_year) > 0:
        return selected_IDM_depart_year[0]
    else:
        return None
###################################

col = st.columns((1.5, 4, 2.5), gap='medium')

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
            
            st.write('IDM Anual')
            st.altair_chart(idm_donut_total_chart, use_container_width=True)
            
            st.write('IDM Anual - Hospitales')
            st.altair_chart(idm_donut_hosp_chart, use_container_width=True)
            
            st.write('IDM Anual - Centros de Salud')
            st.altair_chart(idm_donut_cen_chart, use_container_width=True)
            
            st.write('IDM Anual - Puestos de Salud')
            st.altair_chart(idm_donut_pue_chart, use_container_width=True)

        with col[1]:
            # Filtrar datos según el año y el departamento seleccionados
            filtered_data = geo_idm[(geo_idm['año'] == selected_year) & (geo_idm['departamento'] == selected_depart)]
        
            # Verificar si hay datos para el departamento seleccionado
            if not filtered_data.empty:
                # Obtener la primera coordenada del dataframe filtrado
                initial_lat = filtered_data.iloc[0]['latitud']
                initial_lon = filtered_data.iloc[0]['longitud']
        
                # Crear el mapa de Plotly
                fig = go.Figure()
        
                for tipo in ['Hospital', 'Centro de salud', 'Puesto de Salud', 'Otro']:
                    df_tipo = filtered_data[filtered_data['tipo'] == tipo]
                    fig.add_trace(go.Scattermapbox(
                        lat=df_tipo['latitud'],
                        lon=df_tipo['longitud'],
                        mode='markers',
                        marker=go.scattermapbox.Marker(size=9),
                        text=df_tipo.apply(lambda row: f"Nombre: {row['establec']}<br>IDM: {row['dispo']}%<br>Tipo: {row['tipo']}", axis=1),  # Popup content
                        hoverinfo='text',
                        name=tipo
                    ))
        
                fig.update_layout(
                    mapbox_style="carto-positron",
                    mapbox=dict(
                        center=go.layout.mapbox.Center(
                            lat=initial_lat,
                            lon=initial_lon
                        ),
                        zoom=6.5
                    ),
                    margin={"r":0,"t":0,"l":0,"b":0},
                    legend_title_text='Tipo de Establecimiento',
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,  # Ajusta la posición vertical de la leyenda
                xanchor="center",
                x=0.2
                ))
        
                st.markdown('### Mapa de Disponibilidad de medicinas por establecimiento de salud')
                st.plotly_chart(fig, use_container_width=True)
                
        ########## LINEPLOT
                st.markdown('### Evolución del IDM por tipo de establecimiento')
                df_lineplot = pd.concat([
                    idm_hospitales[idm_hospitales['departamento'] == selected_depart].assign(tipo='Hospitales'),
                    idm_centros[idm_centros['departamento'] == selected_depart].assign(tipo='Centros de Salud'),
                    idm_puestos[idm_puestos['departamento'] == selected_depart].assign(tipo='Puestos de Salud')
                ])
                
                # Crear el line plot usando plotly
                fig = px.line(
                    df_lineplot,
                    x="date", y="idm",
                    color="tipo",
                    labels={"idm": "IDM", "date": "Fecha"}
                )
        
                # Añadir las líneas horizontales de colores
                fig.add_hrect(y0=90, y1=100, line_width=0, fillcolor="green", opacity=0.2, annotation_text="Bien", annotation_position="top left")
                fig.add_hrect(y0=70, y1=90, line_width=0, fillcolor="yellow", opacity=0.2, annotation_text="Regular", annotation_position="top left")
                fig.add_hrect(y0=50, y1=70, line_width=0, fillcolor="orange", opacity=0.2, annotation_text="Mal", annotation_position="top left")
                fig.add_hrect(y0=35, y1=50, line_width=0, fillcolor="red", opacity=0.2, annotation_text="Muy mal", annotation_position="top left")
        
                # Mover la leyenda a la parte inferior
                fig.update_layout(
                    legend_title_text='Tipo de Establecimiento',
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,  # Ajusta la posición vertical de la leyenda
                        xanchor="center",
                        x=0.5
                    )
                )
        
                st.plotly_chart(fig, use_container_width=True)

#######################################

ranking = ranking[(ranking['departamento'] == selected_depart) & (ranking['año'] == selected_year)][['nombre_med_grupo']].head(15)

with col[2]:
    st.markdown('### Top Medicamentos desabastecidos')
    
    st.dataframe(ranking,
                 hide_index=True,
                 width=None,
                 column_config={
                     'nombre_med_grupo': st.column_config.TextColumn('nombre_med_grupo')
                 })