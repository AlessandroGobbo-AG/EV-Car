import streamlit as st
import polars as pl
from pathlib import Path
import re

@st.cache_data
def read_data():
    '''
    Funzione che legge i dati del file csv del percorso: DATA/data.csv

    Returns:
        dataframe: dataframe dei dati
    '''
    data_dir = Path('DATA')
    data = pl.read_csv( data_dir/'data.csv')
    return data


def max_min_coord(data, city):
    '''
    Funzione che mi ritorna le coordinate possibili in base alle scelte fatte
    '''
    
    #creazione lista coordinate
    coord_list = []

    #selezione dei dati
    data = (
        data
        .filter(pl.col('City') == city)
        .select(pl.col('Vehicle Location'))
    )

    #riempimento lista delle coordinate
    for row in data.rows():
        if row[0] is not None:
            numb = re.findall(r'-?\d+\.\d+|-?\d+', row[0])
            coord = (float(numb[0]), float(numb[1]))
            coord_list.append(coord)

    df = pl.DataFrame(coord_list, schema=['lon', 'lat'])

    df = (
        df
        .select(
            pl.col('lon').max().alias('lon_max'),
            pl.col('lon').min().alias('lon_min'),
            pl.col('lat').max().alias('lat_max'),
            pl.col('lat').min().alias('lat_min')
        )
    )
    return df

'''
Funzione che crea Main del file
'''
def sale_main():

    #Importazione dei dati
    data = read_data()
    
    #Titolo della pagina
    st.markdown(f'''
                <h1 style='text-align: center; color: orange'>
                    Sezione Vendita
                </h1'''
                , unsafe_allow_html=True)
    
    #Spiazione della pagina
    st.markdown(f'''
        <div style='border:2px solid orange; padding:20px; border-radius:8px; margin-bottom:30px; font-size:16px;'>
            <p>Sezione dedicata all'aggiunta di una nuova vendita di un auto BEV o PHEV degli abitanti dello stato di Washington.</p> 
            <ul>  
                <li>L'inserimento avverrà un campo alla volta. Per gli inserimenti di campi di testi, l'ordine sarà ordine <b>alfabetico</b>.</li>
                <li>Mentre per i campi numerici ci saranno dei <b>controlli</b>, ad esempio nell'autonomia e nella localizzazione della vendita.</li>
                <li>Si ricorda che l'autonomia delle auto è espressa in miglia (1 miglio = 1.6 chilometri).
            </ul>
        </div>
        ''', unsafe_allow_html=True
    )

    st.divider()
    #-------------------------------------------------------------------------------------

    #Creazione sessioni di stato per aggiunta vendita
    if 'new_sale_county' not in st.session_state:
        st.session_state.new_sale_county = ''

    if 'new_sale_city' not in st.session_state:
        st.session_state.new_sale_city = ''

    if 'new_sale_make' not in st.session_state:
        st.session_state.new_sale_make = ''

    if 'new_sale_model' not in st.session_state:
        st.session_state.new_sale_model = ''

    if 'new_sale_year_model' not in st.session_state:
        st.session_state.new_sale_year_model = 2025

    if 'new_sale_engine_type' not in st.session_state:
        st.session_state.new_sale_engine_type = ''

    if 'new_sale_range' not in st.session_state:
        st.session_state.new_sale_range = 0

    if 'new_sale_coordinates' not in st.session_state:
        st.session_state.new_sale_coordinates = []

    if 'new_sale_check_lon' not in st.session_state:
        st.session_state.new_sale_check_lon = ''
    
    if 'new_sale_check_lat' not in st.session_state:
        st.session_state.new_sale_check_lat = ''

    #Aggiunta di una nuova vendita
    st.markdown(f'''
                <h3 style='text-align: center;'>
                    Dati della vendita
                </h3'''
                , unsafe_allow_html=True)
    
    c1 = st.container(border=True)

    st.session_state.new_sale_county = c1.selectbox(label = 'Seleziona la contea',
                                                    options= sorted(data['County'].unique().to_list()))
    
    st.session_state.new_sale_city = c1.selectbox(label='Seleziona la città',
                                                  options= sorted(data
                                                                  .filter(pl.col('County') == st.session_state.new_sale_county)['City']
                                                                  .unique().to_list()))
    
    st.session_state.new_sale_make = c1.selectbox(label='''Seleziona il produttore dell'auto''',
                                                  options = sorted(data['Make'].unique().to_list()))
    
    st.session_state.new_sale_model = c1.selectbox(label = '''Seleziona il modello dell'auto''',
                                                   options = sorted(data
                                                                    .filter(pl.col('Make') == st.session_state.new_sale_make)['Model']
                                                                    .unique().to_list()))
    
    st.session_state.new_sale_year_model = c1.select_slider(label='Seleziona anno immattricolazione auto',
                                                            options= sorted(data['Model Year']
                                                                            .unique().to_list()))
    
    st.session_state.new_sale_engine_type = c1.selectbox(label = 'Seleziona la tipologia del motore', 
                                                         options= (data
                                                                   .filter(pl.col('Model') == st.session_state.new_sale_model)['Electric Vehicle Type']
                                                                   .unique().to_list()))
    
    st.session_state.new_sale_range = c1.slider(label='Inserire autonomia motore elettrico', 
                                                max_value=(data
                                                           .filter(pl.col('Electric Vehicle Type') == st.session_state.new_sale_engine_type)['Electric Range'].max()))

    st.session_state.new_sale_check_coord = max_min_coord(data, st.session_state.new_sale_city)
    c1.write(f'''Coordinate limite per {st.session_state.new_sale_city}''')
    c1.write(st.session_state.new_sale_check_coord)

    c1.write('Inserisci le coordinate della vendita')
    c1.number_input('Inserisci Longitudine', 
                    min_value=st.session_state.new_sale_check_coord['lon_min'].item(),
                    max_value=st.session_state.new_sale_check_coord['lon_max'].item(),
                    step=0.0001,
                    format="%.4f")

    c1.number_input('Inserisci Latitudine', 
                    min_value=st.session_state.new_sale_check_coord['lat_min'].item(),
                    max_value=st.session_state.new_sale_check_coord['lat_max'].item(),
                    step=0.0001,
                    format="%.4f")


if __name__ == '__main__':
    print('Hello world')