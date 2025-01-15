import streamlit as st
import polars as pl
from pathlib import Path
import re
import time


def read_data():
    '''
    Funzione che legge i dati del file csv del percorso: DATA/data.csv

    RETURN
        dataframe: dataframe dei dati
    '''
    data_dir = Path('DATA')
    data = pl.read_csv(data_dir/'data.csv')
    return data

def write_data(data):
    '''
    Funzione che scrive nuovi dati sul file csv data.csv

    PARAM
        dataframe: dati da scrivere
    '''
    data_dir = Path('DATA')
    data.write_csv(data_dir/'data.csv', separator=',')

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

    df = pl.DataFrame(coord_list, schema=['lon', 'lat'], orient="row")

    df = (
        df
        .select(
            pl.col('lon').round(4).max().alias('lon_max'),
            pl.col('lon').round(4).min().alias('lon_min'),
            pl.col('lat').round(4).max().alias('lat_max'),
            pl.col('lat').round(4).min().alias('lat_min')
        )
    )
    return df

def sale_main():
    # Tracciamento aggiunta dei dati
    if 'data_was_added' not in st.session_state:
        st.session_state.data_was_added = False

    if 'current_data' not in st.session_state or st.session_state.data_was_added:
        st.session_state.current_data = read_data()
        st.session_state.data_was_added = False  # Reset the flag
    
    data = st.session_state.current_data

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
                <li>Si ricorda che l'autonomia delle auto è espressa in miglia (1 miglio = 1.6 chilometri).</li>
            </ul>
            <h4 style="text-align:center; color: orange">Informazioni su compilazione form</h4>
                <ul>
                    <li>Le contee presenti nelle scelte sono quelle presenti nel dataset d'origine, dunque al di fuori
                        dello stato di Washington</li>
                    <li>Dal punto precedente, potrebbe essere che alcune contee non presentino tutte le città presenti, le città
                        sceglibili sono quelle che sono presenti nel dataset d'origine.</li>
                    <li>Le coordinate hanno il vincolo delle coordinate massime e minime della città scelta,
                        presenti nel dataset d'origine.</li>
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

    if 'new_sale_state' not in st.session_state:
        st.session_state.new_sale_state = ''

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

    if 'new_sale_longitude' not in st.session_state:
        st.session_state.new_sale_longitude = ''
    
    if 'new_sale_latitude' not in st.session_state:
        st.session_state.new_sale_latitude = ''

    #Aggiunta di una nuova vendita
    st.markdown(f'''
                <h3 style='text-align: center;'>
                    Dati della vendita
                </h3'''
                , unsafe_allow_html=True)
    
    c1 = st.container(border=True)

    # Scelta dei dati
    st.session_state.new_sale_county = c1.selectbox(label = 'Seleziona la contea',
                                                    options= sorted(data['County'].unique().to_list()))
    
    st.session_state.new_sale_city = c1.selectbox(label='Seleziona la città',
                                                  options= sorted(data
                                                                  .filter(pl.col('County') == st.session_state.new_sale_county)['City']
                                                                  .unique().to_list()))
    st.session_state.new_sale_state = (data
                                       .filter(pl.col('City') == st.session_state.new_sale_city)['State']
                                       .unique().item())

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
    st.session_state.new_sale_longitude = c1.number_input('Inserisci Longitudine', 
                    min_value=st.session_state.new_sale_check_coord['lon_min'].item(),
                    max_value=st.session_state.new_sale_check_coord['lon_max'].item(),
                    step=0.0001,
                    format="%.4f")

    st.session_state.new_sale_latitude = c1.number_input('Inserisci Latitudine', 
                    min_value=st.session_state.new_sale_check_coord['lat_min'].item(),
                    max_value=st.session_state.new_sale_check_coord['lat_max'].item(),
                    step=0.0001,
                    format="%.4f")


    #Operazioni a seguito del button
    submit_sale = c1.button('Conferma scelte', type="primary")
    if submit_sale:
        new_row = pl.DataFrame([dict(zip(data.columns, [
            st.session_state.new_sale_county,
            st.session_state.new_sale_city,
            st.session_state.new_sale_state,
            st.session_state.new_sale_year_model,
            st.session_state.new_sale_make,
            st.session_state.new_sale_model,
            st.session_state.new_sale_engine_type,
            st.session_state.new_sale_range,
            0,
            f'POINT ({st.session_state.new_sale_longitude} {st.session_state.new_sale_latitude})'
        ]))])

        # Update sessio state
        st.session_state.current_data = pl.concat([st.session_state.current_data, new_row])
        write_data(st.session_state.current_data)

        # Flag aggiunta dati
        st.session_state.data_was_added = True  
        c1.success('Vendita eseguita con successo')
        time.sleep(2)
        st.rerun()

if __name__ == '__main__':
    print('Hello world')