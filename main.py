import streamlit as st
import os
import pandas as pd
# from streamlit_folium import st_folium
import folium
import matplotlib.pyplot as plt

directorio_actual = os.path.dirname(__file__)

#cargar csvs
df_renta = pd.read_csv(os.path.join(directorio_actual, "Resultados", "RentaMedia_Distritos.csv"),index_col=0)
df_centros = pd.read_csv(os.path.join(directorio_actual, "Resultados", "lista_centros.csv"),index_col=0)
df_librerias = pd.read_csv(os.path.join(directorio_actual, "Resultados", "listado_con_distritos.csv"),index_col=0)
df_centros = df_centros.drop_duplicates(subset=['despecific'])

def borde_geo(feature):
    return {
        'fillColor': '#ff8830',  
        'color': '#ff8830',      
        'weight': 1,           
        'fillOpacity': 0.3    
    }

st.set_page_config(page_title='Librerias en Valencia', 
                   page_icon='📕', 
                   layout="centered",)

with st.sidebar:
    option = st.selectbox(
        'Selecciona página',
        ('General','Distrito', 'Librerias', 'Centros Educativos','Gráficos'),index=0)
    
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
        marcador = folium.Marker(location=[lat, lon], popup=nombre, icon=folium.Icon(color='beige', icon='graduation-cap', prefix='fa'))
        marcador.add_to(centros_educativos)

    for index, row in df_librerias.iterrows():
        nombre = index
        direccion = row['formatted_address']
        latitud = row['latitud']
        longitud = row['longitud']
        folium.Marker(location=[latitud, longitud], popup=f"{nombre}: {direccion}",icon=folium.Icon( color='orange',icon='book',prefix='fa')).add_to(librerias_grupo)

    centros_educativos.add_to(mapa)
    librerias_grupo.add_to(mapa)
    distritos_grupo.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    mapa_html = mapa._repr_html_()

    st_folium(mapa,width=700)

elif option == 'Distrito':
    st.markdown("<h3 style='text-align: center; color: #ff8830;'>Mapa  por Distritos</h1>", unsafe_allow_html=True)
    with st.sidebar:
        df_renta_dinindex = df_renta.set_index('Distritos')
        anyo = st.selectbox(
        'Selecciona año',
        ('2015','2016','2017','2018','2019','2020','2021'),index=6)
        renta = df_renta_dinindex[anyo]
        st.write('Renta anual por habitante', )
        st.dataframe(renta.sort_values(ascending=False),width=220)

    mapa = folium.Map(location=(39.47405288846648, -0.3768651911255773), zoom_start=12)

    distritos_grupo = folium.FeatureGroup(name='Distritos')

    geojson_file = os.path.join(directorio_actual, "datos", "distritos_vlc.geojson")
    geojson_data = open(geojson_file, 'r', encoding='utf-8-sig').read()

    geojson_distritos = folium.GeoJson(geojson_data, name='distritos',style_function=borde_geo).add_to(distritos_grupo)

    popup = folium.GeoJsonPopup(fields=['nombre'], aliases=['Distrito:&nbsp;'])
    popup.add_to(geojson_distritos)

    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=df_renta,
        columns=['Distritos', anyo],
        key_on='feature.properties.nombre',
        fill_color='Oranges',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Renta anual por habitante'
    ).add_to(mapa)

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
        st.dataframe(librerias.sort_values(ascending=False),width=220)
       
    mapa = folium.Map(location=(39.47405288846648, -0.3768651911255773), zoom_start=12)

    librerias_grupo = folium.FeatureGroup(name='Librerias')
    distritos_grupo = folium.FeatureGroup(name='Distritos')

    geojson_file = os.path.join(directorio_actual, "datos", "distritos_vlc.geojson")
    geojson_data = open(geojson_file, 'r', encoding='utf-8-sig').read()

    geojson_distritos = folium.GeoJson(geojson_data, name='distritos',style_function=borde_geo).add_to(distritos_grupo)

    popup = folium.GeoJsonPopup(fields=['nombre'], aliases=['Distrito:&nbsp;'])
    popup.add_to(geojson_distritos)

    for index, row in df_librerias.iterrows():
        if dist == 'Todos':
            nombre = index
            direccion = row['formatted_address']
            latitud = row['latitud']
            longitud = row['longitud']
            folium.Marker(location=[latitud, longitud], popup=f"{nombre},{direccion}",icon=folium.Icon(icon='book',color='orange', prefix='fa')).add_to(librerias_grupo)
        else:
            if row['distrito'] == dist:
                nombre = index
                direccion = row['formatted_address']
                latitud = row['latitud']
                longitud = row['longitud']
                folium.Marker(location=[latitud, longitud], popup=f"{nombre},{direccion}",icon=folium.Icon(icon='book',color='orange', prefix='fa')).add_to(librerias_grupo)

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
        st.dataframe(df_librerias_sinlatlong.loc[libreria],width=700)
            

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
            st.dataframe(recuento_filtr,width=220)
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

    for index, row in df_centros.iterrows():
        if dist == 'Todos':
            nombre = row['despecific']
            tipo = row['dgenerica_']
            lat, lon = map(float, row['Geo Point'].split(', '))
            marcador = folium.Marker(location=[lat, lon], popup=str(nombre) + ' ' + str(tipo), icon=folium.Icon(color='beige', icon='graduation-cap', prefix='fa'))
            marcador.add_to(centros_educativos)
        else:
            if row['distrito'] == dist:
                nombre = row['despecific']
                tipo = row['dgenerica_']
                lat, lon = map(float, row['Geo Point'].split(', '))
                marcador = folium.Marker(location=[lat, lon], popup=str(nombre) + ' ' + str(tipo), icon=folium.Icon(color='beige', icon='graduation-cap', prefix='fa'))

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
        st.dataframe(df_centros_singeo.loc[df_centros_singeo['despecific']==centro].T,width=700)


elif option == 'Gráficos':  
    st.markdown("<h3 style='text-align: center; color: #33FF86;'>Gráficos</h1>", unsafe_allow_html=True)
    df_renta_grafico = df_renta.set_index('Distritos')
    df_renta_grafico = df_renta_grafico.transpose()
    estilos = ['-', '--', '-.', ':']
    colores = ['b', 'g', 'r', 'c', 'm', 'y', 'k'] 

    plt.figure(figsize=(14, 8))
    for i, distrito in enumerate(df_renta_grafico.columns):
        estilo = estilos[i % len(estilos)]
        color = colores[i % len(colores)]
        plt.plot(df_renta_grafico.index, df_renta_grafico[distrito], label=distrito, linestyle=estilo, color=color)

    plt.title('Evolución de la renta neta media por persona en los distritos de València')
    plt.xlabel('Año')
    plt.ylabel('Renta neta media por persona')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

