import streamlit as st
import os
import pandas as pd
from streamlit_folium import st_folium
import folium
import matplotlib.pyplot as plt
import numpy as np


directorio_actual = os.path.dirname(__file__)

#cargar csvs
try:
    df_renta = pd.read_csv(os.path.join(directorio_actual, "Resultados", "RentaMedia_Distritos.csv"),index_col=0)
except Exception as e:
    st.error(f"Error al cargar el archivo RentaMedia_Distritos.csv: {e}")
    st.stop()
try:
   df_centros = pd.read_csv(os.path.join(directorio_actual, "Resultados", "lista_centros.csv"),index_col=0)
   df_centros = df_centros.drop_duplicates(subset=['despecific'])
except Exception as e:
    st.error(f"Error al cargar el archivo lista_centros.csv {e}")
    st.stop()
try:
    df_librerias = pd.read_csv(os.path.join(directorio_actual, "Resultados", "listado_con_distritos.csv"),index_col=1)
except:
    st.error(f"Error al cargar el archivo listado_con_distritos.csv: {e}")
    st.stop()
try:
    df_densidad = pd.read_csv(os.path.join(directorio_actual, "Resultados", "Densidad_distrito.csv"),index_col=0)
except:
    st.error(f"Error al cargar el archivo Densidad_distrito.csv: {e}")
    st.stop()
try:
    df_unido = pd.read_csv(os.path.join(directorio_actual, "Resultados", "Locales_unidos.csv"),index_col=0)
except:
    st.error(f"Error al cargar el archivo Locales_unidos.csv: {e}")
    st.stop()
try:
    df_renta_secc = pd.read_csv(os.path.join(directorio_actual, "Resultados", "renta_seccion_2021.csv"),index_col=0)
    df_renta_secc['Secciones'] = df_renta_secc['Secciones'].astype(str)
    df_renta_secc['Secciones'] = df_renta_secc['Secciones'].apply(lambda x: x.zfill(5))
    df_renta_secc['Secciones'] = df_renta_secc['Secciones'].str[:2] + df_renta_secc['Secciones'].str[3:]

except:
    st.error(f"Error al cargar el archivo Densidad_distrito.csv: {e}")
    st.stop()

def borde_geo(feature):
    return {
        'fillColor': '#ff8830',  
        'color': '#ff8830',      
        'weight': 1,           
        'fillOpacity': 0.3    
    }

distritos_valencia = {
    1: "Ciutat Vella",
    2: "Eixample",
    3: "Extramurs",
    4: "Campanar",
    5: "La Saïdia",
    6: "Pla del Real",
    7: "Olivereta",
    8: "Patraix",
    9: "Jesús",
    10: "Quatre Carreres",
    11: "Poblats Marítims",
    12: "Camins al Grau",
    13: "Algirós",
    14: "Benimaclet",
    15: "Rascanya"
}

if "center" not in st.session_state:
    layoutt = "wide"
else:
    layoutt = "centered" if st.session_state.center else "wide"

st.set_page_config(page_title='Librerias en Valencia', 
                   page_icon='📕', 
                   layout=layoutt,)



with st.sidebar:
    st.checkbox(
        "Viendo desde móvil?", key="center", value=st.session_state.get("center", False)
    )
    option = st.selectbox(
        'Selecciona página',
        ('General','Distrito', 'Secciones','Librerias', 'Centros Educativos','Gráficos','Locales'),index=0)


if option == 'General':
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Mapa general</h1>", unsafe_allow_html=True)
    mapa = folium.Map(location=(39.47405288846648, -0.3768651911255773), zoom_start=12)


    centros_educativos = folium.FeatureGroup(name='Centros Educativos',show=False)
    librerias_grupo = folium.FeatureGroup(name='Librerias',show=False)
    distritos_grupo = folium.FeatureGroup(name='Distritos')

    geojson_file = os.path.join(directorio_actual, "datos", "distritos_vlc.geojson")
    geojson_data = open(geojson_file, 'r', encoding='utf-8-sig').read()

    geojson_distritos = folium.GeoJson(geojson_data, name='distritos', style_function=borde_geo).add_to(distritos_grupo)

    popup = folium.GeoJsonPopup(fields=['nombre'], aliases=['Distrito:&nbsp;'])
    popup.add_to(geojson_distritos)

    objetivo = folium.Marker(location=[39.47218204154307, -0.38856135262490216], popup='Nuestra Libreria!', icon=folium.Icon(color='green', icon='star', prefix='fa'))
    objetivo.add_to(mapa)

    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=df_renta,
        columns=['Distritos', '2021'],
        key_on='feature.properties.nombre',
        fill_color='Oranges',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Renta anual por habitante'
    ).add_to(mapa)

    for index, row in df_centros.iterrows():
        nombre = row['dlibre']
        lat, lon = map(float, row['Geo Point'].split(', '))
        marcador = folium.Marker(location=[lat, lon], popup=nombre, icon=folium.Icon(color='green', icon='graduation-cap', prefix='fa'))
        marcador.add_to(centros_educativos)

    for index, row in df_librerias.iterrows():
        nombre = index
        direccion = row['formatted_address']
        latitud = row['latitud']
        longitud = row['longitud']
        folium.Marker(location=[latitud, longitud], popup=f"{nombre}: {direccion}",icon=folium.Icon( color='red',icon='book',prefix='fa')).add_to(librerias_grupo)

    centros_educativos.add_to(mapa)
    librerias_grupo.add_to(mapa)
    distritos_grupo.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    mapa_html = mapa._repr_html_()

    st_folium(mapa)

elif option == 'Distrito':
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Mapa  por Distritos</h1>", unsafe_allow_html=True)
    with st.sidebar:
        
        opcion_mapa = st.selectbox(
        'Selecciona tipo de mapa',
        ('Renta', 'Población'),index=0)

        if opcion_mapa == 'Renta':
            df_renta_dinindex = df_renta.set_index('Distritos')
            anyo = st.selectbox(
            'Selecciona año',
            ('2015','2016','2017','2018','2019','2020','2021'),index=6)
            renta = df_renta_dinindex[anyo]
            st.write('Renta anual por habitante', )
            st.dataframe(renta.sort_values(ascending=False),use_container_width =True)

        elif opcion_mapa == 'Población':
            anyo = st.selectbox(
            'Selecciona año',
            ('1991','1996','2001','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023'),index=13)
            st.write('Población por distrito', )
            df_densidad_filtr = df_densidad[anyo]
            st.dataframe(df_densidad_filtr.sort_values(ascending=False),use_container_width =True)

    mapa = folium.Map(location=(39.47405288846648, -0.3768651911255773), zoom_start=12)

    distritos_grupo = folium.FeatureGroup(name='Distritos')
    centros_educativos = folium.FeatureGroup(name='Centros Educativos',show=False)
    librerias_grupo = folium.FeatureGroup(name='Librerias',show=False)

    geojson_file = os.path.join(directorio_actual, "datos", "distritos_vlc.geojson")
    geojson_data = open(geojson_file, 'r', encoding='utf-8-sig').read()

    geojson_distritos = folium.GeoJson(geojson_data, name='distritos',style_function=borde_geo).add_to(distritos_grupo)

    popup = folium.GeoJsonPopup(fields=['nombre'], aliases=['Distrito:&nbsp;'])
    popup.add_to(geojson_distritos)

    objetivo = folium.Marker(location=[39.47218204154307, -0.38856135262490216], popup='Nuestra Libreria!', icon=folium.Icon(color='green', icon='star', prefix='fa'))
    objetivo.add_to(mapa)

    if opcion_mapa == 'Renta':
        folium.Choropleth(
            geo_data=geojson_data,
            name='choropleth',
            data=df_renta,
            columns=['Distritos', anyo],
            key_on='feature.properties.nombre',
            fill_color='Oranges',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Renta anual por habitante').add_to(mapa)
    elif opcion_mapa == 'Población':
        folium.Choropleth(
            geo_data=geojson_data,
            name='choropleth',
            data=df_densidad,
            columns=['Distritos', anyo],
            key_on='feature.properties.nombre',
            fill_color='Oranges',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Población por distrito',).add_to(mapa)

    for index, row in df_centros.iterrows():
        nombre = row['dlibre']
        lat, lon = map(float, row['Geo Point'].split(', '))
        marcador = folium.Marker(location=[lat, lon], popup=nombre, icon=folium.Icon(color='green', icon='graduation-cap', prefix='fa'))
        marcador.add_to(centros_educativos)

    for index, row in df_librerias.iterrows():
        nombre = index
        direccion = row['formatted_address']
        latitud = row['latitud']
        longitud = row['longitud']
        folium.Marker(location=[latitud, longitud], popup=f"{nombre}: {direccion}",icon=folium.Icon( color='red',icon='book',prefix='fa')).add_to(librerias_grupo)

    centros_educativos.add_to(mapa)
    librerias_grupo.add_to(mapa)
    distritos_grupo.add_to(mapa)

    folium.LayerControl().add_to(mapa)

    mapa_html = mapa._repr_html_()

    st_folium(mapa,width=700)

elif option == 'Secciones':
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Mapa  por Secciones</h1>", unsafe_allow_html=True)
    with st.sidebar:
        df_renta_secc2 = df_renta_secc
        df_renta_secc2['Distritos'] = df_renta_secc2['Distritos'].map(distritos_valencia)
        df_renta_secc_distrito = df_renta_secc2.set_index('Distritos')
        st.write('Renta anual por habitante', )
        st.dataframe(df_renta_secc_distrito[['Secciones','Total']].sort_values(by='Total',ascending=False),use_container_width =True)
    min_value = df_renta_secc['Total'].min()
    max_value = df_renta_secc['Total'].max()
    bins = np.linspace(min_value, max_value, num=6).tolist()
    mapa = folium.Map(location=(39.47405288846648, -0.3768651911255773), zoom_start=12)

    distritos_grupo = folium.FeatureGroup(name='Distritos')
    centros_educativos = folium.FeatureGroup(name='Centros Educativos',show=False)
    librerias_grupo = folium.FeatureGroup(name='Librerias',show=False)

    geojson_file = os.path.join(directorio_actual, "datos", "seccions-censals-secciones-censales.geojson")

    geojson_data = open(geojson_file, 'r', encoding='utf-8-sig').read()
    filtered_geojson_data = {
        'type': 'FeatureCollection',
        'features': [feature for feature in folium.GeoJson(geojson_data).data['features'] if int(feature['properties']['coddistrit']) <= 15]
    }

    for feature in filtered_geojson_data['features']:
        cod_dist_secc = feature['properties'].get('coddistsecc')
        feature['properties']['codsecc'] = cod_dist_secc if cod_dist_secc is not None else 0
    geojson_distritos = folium.GeoJson(filtered_geojson_data, name='distritos',style_function=borde_geo).add_to(distritos_grupo)
    popup = folium.GeoJsonPopup(fields=['coddistrit','codsecc'], aliases=['Distrito:&nbsp;','Seccion:&nbsp;'])
    popup.add_to(geojson_distritos)
    folium.Choropleth(
        geo_data=filtered_geojson_data,
        name='choropleth',
        data=df_renta_secc,
        columns=['Secciones', 'Total'],
        key_on='feature.properties.codsecc',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Renta neta por habitante 2021',
    ).add_to(mapa)

    objetivo = folium.Marker(location=[39.47218204154307, -0.38856135262490216], popup='Nuestra Libreria!', icon=folium.Icon(color='green', icon='star', prefix='fa'))
    objetivo.add_to(mapa)

    for index, row in df_centros.iterrows():
        nombre = row['dlibre']
        lat, lon = map(float, row['Geo Point'].split(', '))
        marcador = folium.Marker(location=[lat, lon], popup=nombre, icon=folium.Icon(color='green', icon='graduation-cap', prefix='fa'))
        marcador.add_to(centros_educativos)

    for index, row in df_librerias.iterrows():
        nombre = index
        direccion = row['formatted_address']
        latitud = row['latitud']
        longitud = row['longitud']
        folium.Marker(location=[latitud, longitud], popup=f"{nombre}: {direccion}",icon=folium.Icon( color='red',icon='book',prefix='fa')).add_to(librerias_grupo)

    centros_educativos.add_to(mapa)
    librerias_grupo.add_to(mapa)
    distritos_grupo.add_to(mapa)

    folium.LayerControl().add_to(mapa)

    mapa_html = mapa._repr_html_()

    st_folium(mapa,width=700)


elif option == 'Librerias':
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Mapa de Librerias </h1>", unsafe_allow_html=True)
    with st.sidebar:
        distrito = list(df_librerias['distrito'].unique())
        distrito.insert(0,'Todos')
        dist = st.selectbox(
        'Selecciona Distrito',
        (distrito),index=0)
        if dist == 'Todos':
            librerias = df_librerias['rating']
            recuento = df_librerias['distrito'].count()
            st.write('Recuento de librerias por distrito: ', recuento)
        else:
            librerias = df_librerias[df_librerias['distrito'] == dist]['rating']
            recuento = df_librerias[df_librerias['distrito'] == dist]['distrito'].value_counts()
            st.write('Recuento de librerias por distrito: ', recuento[0])
        st.dataframe(librerias.sort_values(ascending=False),use_container_width =True)
       
    mapa = folium.Map(location=(39.47405288846648, -0.3768651911255773), zoom_start=12)

    librerias_grupo = folium.FeatureGroup(name='Librerias')
    distritos_grupo = folium.FeatureGroup(name='Distritos')

    geojson_file = os.path.join(directorio_actual, "datos", "distritos_vlc.geojson")
    geojson_data = open(geojson_file, 'r', encoding='utf-8-sig').read()

    geojson_distritos = folium.GeoJson(geojson_data, name='distritos',style_function=borde_geo).add_to(distritos_grupo)

    popup = folium.GeoJsonPopup(fields=['nombre'], aliases=['Distrito:&nbsp;'])
    popup.add_to(geojson_distritos)

    objetivo = folium.Marker(location=[39.47218204154307, -0.38856135262490216], popup='Nuestra Libreria!', icon=folium.Icon(color='green', icon='star', prefix='fa'))
    objetivo.add_to(mapa)

    for index, row in df_librerias.iterrows():
        if dist == 'Todos':
            nombre = index
            direccion = row['formatted_address']
            latitud = row['latitud']
            longitud = row['longitud']
            folium.Marker(location=[latitud, longitud], popup=f"{nombre}",icon=folium.Icon(icon='book',color='red', prefix='fa')).add_to(librerias_grupo)
        else:
            if row['distrito'] == dist:
                nombre = index
                direccion = row['formatted_address']
                latitud = row['latitud']
                longitud = row['longitud']
                folium.Marker(location=[latitud, longitud], popup=f"{nombre}",icon=folium.Icon(icon='book',color='red', prefix='fa')).add_to(librerias_grupo)

    librerias_grupo.add_to(mapa)
    distritos_grupo.add_to(mapa)

    folium.LayerControl().add_to(mapa)

    mapa_html = mapa._repr_html_()

    st_folium(mapa,width=700)

    with st.expander('Saber más por Libreria'):
        df_librerias_sinlatlong = df_librerias.drop(['latitud','longitud'],axis=1)
        if dist == 'Todos':
            libreria_lista = list(df_librerias['distrito'].index.unique())
            libreria = st.selectbox(
            'Selecciona Libreria',
            (libreria_lista),index=0)
        else:
            libreria_lista = list(df_librerias[df_librerias['distrito'] == dist].index.unique())
            libreria = st.selectbox(
            'Selecciona Libreria',
            (libreria_lista),index=0)
        st.dataframe(df_librerias_sinlatlong.loc[libreria],use_container_width =True)
            

elif option == 'Centros Educativos':
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Mapa de Centros Educativos</h1>", unsafe_allow_html=True)

    with st.sidebar:
        distrito = list(df_centros['distrito'].unique())
        distrito.insert(0,'Todos')
        dist = st.selectbox(
        'Selecciona Distrito',
        (distrito),index=0)
        if dist == 'Todos':
            librerias = df_centros['telef']
            recuento = df_centros['distrito'].count()
            recuento_filtr = df_centros['distrito'].value_counts()
            st.write('Recuento de centros por distrito: ', recuento)
            st.dataframe(recuento_filtr,use_container_width =True)
        else:
            librerias = df_centros[df_centros['distrito'] == dist]['telef']
            recuento_filtr = df_centros[df_centros['distrito'] == dist]['distrito'].value_counts()

            st.write('Recuento de centros por distrito: ', recuento_filtr[0])

    
    mapa = folium.Map(location=(39.47405288846648, -0.3768651911255773), zoom_start=12)
    centros_educativos = folium.FeatureGroup(name='Centros Educativos',show=True)

    distritos_grupo = folium.FeatureGroup(name='Distritos')
    geojson_file = os.path.join(directorio_actual, "datos", "distritos_vlc.geojson")
    geojson_data = open(geojson_file, 'r', encoding='utf-8-sig').read()

    geojson_distritos = folium.GeoJson(geojson_data, name='distritos',style_function=borde_geo).add_to(distritos_grupo)

    popup = folium.GeoJsonPopup(fields=['nombre'], aliases=['Distrito:&nbsp;'])
    popup.add_to(geojson_distritos)

    objetivo = folium.Marker(location=[39.47218204154307, -0.38856135262490216], popup='Nuestra Libreria!', icon=folium.Icon(color='green', icon='star', prefix='fa'))
    objetivo.add_to(mapa)

    for index, row in df_centros.iterrows():
        if dist == 'Todos':
            nombre = row['despecific']
            tipo = row['dgenerica_']
            lat, lon = map(float, row['Geo Point'].split(', '))
            marcador = folium.Marker(location=[lat, lon], popup=str(nombre) + ' ' + str(tipo), icon=folium.Icon(color='lightgray', icon='graduation-cap', prefix='fa'))
            marcador.add_to(centros_educativos)
        else:
            if row['distrito'] == dist:
                nombre = row['despecific']
                tipo = row['dgenerica_']
                lat, lon = map(float, row['Geo Point'].split(', '))
                marcador = folium.Marker(location=[lat, lon], popup=str(nombre) + ' ' + str(tipo), icon=folium.Icon(color='lightgray', icon='graduation-cap', prefix='fa'))

                marcador.add_to(centros_educativos)    

    centros_educativos.add_to(mapa)
    distritos_grupo.add_to(mapa)

    folium.LayerControl().add_to(mapa)

    mapa_html = mapa._repr_html_()

    st_folium(mapa,width=700)

    with st.expander('Saber más por Centro'):
        datos_filtrados = df_centros[(df_centros['distrito'] == dist)]
        datos_filtrados.dropna(inplace=True)  
        lista_cent = list(datos_filtrados['despecific'].unique())
        centro = st.selectbox(
            'Selecciona Centro',
            (lista_cent),index=0)
        df_centros_singeo = df_centros.drop(['Geo Point', 'Geo Shape','dlibre'], axis=1)
        st.dataframe(df_centros_singeo.loc[df_centros_singeo['despecific']==centro].T,use_container_width =True)


elif option == 'Gráficos':  
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Gráficos de Renta y Población</h3>", unsafe_allow_html=True)
    df_renta_grafico = df_renta.set_index('Distritos')

    min_year = int(df_renta_grafico.columns.min())
    max_year = int(df_renta_grafico.columns.max())

    num_distritos = st.sidebar.slider("Distritos para renta", min_value=1, max_value=len(df_renta_grafico), value=5)

    selected_years = st.sidebar.slider("Años para renta", min_value=min_year, max_value=max_year, value=(min_year, max_year))
    selected_years_str = list(map(str, range(selected_years[0], selected_years[1]+1)))

    df_renta_grafico = df_renta_grafico.sort_values(by='2021', ascending=False).head(num_distritos)
    df_renta_grafico = df_renta_grafico[selected_years_str]
    df_renta_grafico = df_renta_grafico.transpose()

    estilos = ['-', '--', '-.', ':']
    colores = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    plt.rcParams.update({'font.size': 14})
    plt.figure(figsize=(14, 8))
    for i, distrito in enumerate(df_renta_grafico.columns):
        estilo = estilos[i % len(estilos)]
        color = colores[i % len(colores)]
        plt.plot(df_renta_grafico.index, df_renta_grafico[distrito], label=distrito, linestyle=estilo, color=color)

    plt.title('Evolución Anual de la Renta por Distrito')
    plt.xlabel('Año')
    plt.ylabel('Renta neta media por persona')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

    df_densidad_grafico = df_densidad.set_index('Distritos')

    min_year = int(df_densidad_grafico.columns.min())
    max_year = int(df_densidad_grafico.columns.max())

    df_densidad_grafico.columns = df_densidad_grafico.columns.astype(int)

    num_distritos = st.sidebar.slider("Distritos para población", key="num_distritos", min_value=1, max_value=len(df_densidad_grafico), value=5)

    selected_years = st.sidebar.slider("Años para población", key="selected_years", min_value=min_year, max_value=max_year, value=(min_year, max_year))

    df_densidad_grafico = df_densidad_grafico.sort_values(by=max_year, ascending=False).head(num_distritos)
    df_densidad_grafico = df_densidad_grafico.loc[:, selected_years[0]:selected_years[1]]


    plt.figure(figsize=(12, 8))
    for distrito in df_densidad_grafico.index:
        plt.plot(df_densidad_grafico.columns, df_densidad_grafico.loc[distrito], label=distrito)

    plt.title('Evolución Anual de la Población por Distrito')
    plt.xlabel('Año')
    plt.ylabel('Población')
    plt.legend(title='Distrito', loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.tight_layout()

    st.pyplot(plt)

elif option == 'Locales':
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Locales</h3>", unsafe_allow_html=True)
    df_unido_graficos = df_unido
    df_unido_graficos['precio'] = df_unido_graficos['precio'].str.replace('/mes', '').str.replace('.','').str.replace('[\€,]', '', regex=True).astype(int)
    df_unido_graficos['metros'] = df_unido_graficos['metros'].str.replace('m²', '').str.replace('.','').astype(int)
    locales_por_distrito = df_unido_graficos['distrito'].value_counts()

    num_distritos = st.sidebar.slider("Selecciona la cantidad de distritos a mostrar", min_value=1, max_value=len(locales_por_distrito), value=5)

    metros_min = st.sidebar.slider("Selecciona el mínimo de metros cuadrados", min_value=0, max_value=500, value=100)
    precio_max = st.sidebar.slider("Selecciona el máximo de precio", min_value=100, max_value=3000, value=1000)
    top_distritos = locales_por_distrito.head(num_distritos)

    df_filtrado = df_unido_graficos.loc[(df_unido_graficos['metros'] >= metros_min) & (df_unido_graficos['precio'] <= precio_max)]

    locales_por_distrito_filtrado = df_filtrado['distrito'].value_counts().head(num_distritos)
    plt.figure(figsize=(10, 6))
    locales_por_distrito_filtrado.plot(kind='bar', color='orange')
    plt.title('Cantidad de Locales por Distrito')
    plt.xlabel('Distrito')
    plt.ylabel('Cantidad de Locales')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)

    with st.expander('Ver Locales'):
        distrito = list(df_unido['distrito'].unique())
        distrito.insert(0,'Todos')
        dist = st.selectbox(
        'Selecciona Distrito',
        (distrito),index=0)
        if dist == 'Todos':
            df_filtrado = df_unido.loc[(df_unido['metros'] >= metros_min) & (df_unido['precio'] <= precio_max)]
            st.dataframe(df_filtrado,use_container_width =True)
        else:
            df_filtrado = df_unido.loc[(df_unido['metros'] >= metros_min) & (df_unido['precio'] <= precio_max) & (df_unido['distrito'] == dist)]
            st.dataframe(df_filtrado,use_container_width =True)
