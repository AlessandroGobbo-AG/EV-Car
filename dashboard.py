import streamlit as st
import polars as pl
import altair as alt
import re
import pydeck as pdk
import pandas as pd
from pathlib import Path

'''
Funzione che legge i dati del file csv del percorso: DATA/data.csv

Return:
    dataframe: dataframe dei dati
'''
@st.cache_data
def read_data():
    data_dir = Path('DATA')
    data = pl.read_csv( data_dir/'data.csv')
    return data

'''
Funzione che ritorna un diagramma a barre in cui l'asse delle X rappresenta gli anni, mentre
l'asse delle Y rappresenta il numero di auto vendute. 

-Crea un dataframe in cui sono presenti le colonne 'ANNO' e 'NUMERO VENDITE'
-Creazione del grafico a barre con i dati ricavati in precedenza

Param: 
    dataframe: dataframe dei dati
Return:
    chart: grafico a barre creato con altair
'''
def year_pop_chart(data):
    data_chart = (
        data
        .group_by('Model Year')
        .agg(
            vendite_annuali = pl.col('Model Year').count()
        )
        .sort(pl.col('Model Year'), descending=False)
    )
    
    chart = (
        alt.Chart(
            data_chart,
            title = alt.Title('Vendita annuale di auto elettrico o ibride')
        )
        .mark_bar(
            color='#f17105'
        ) 
        .encode(
            y='vendite_annuali:Q',
            x= 'Model Year:O'
        )
    )
    return(chart)

'''
Testo che spiega il grafico che sarà presente alla sinistra della spiegazione

Param:
    int: numero di auto presenti nel database
Return:
    text: testo della spiegazione
'''
def text_year_pop_chart(number):
    text = f'''Dal grafico si nota come il trend sia in costante crescita
            , presentando un periodo di inversione di trend causata dalla pandemia di
            Covid19.  
            :orange[***Considerazioni***]  
            **1)** Il dataset non presenta tutte le auto BEV/PHEV immatricolato nello stato 
            di Washington, i dati sono stati ricavati dal sito Data.gov, (si guardi documentazione).  
            **2)** Il totale di auto vendute per questa analisi è:  
            :orange-background[**{number}**]  
            **3)** I dati sono stati scaricati in data 10-12-2024, e l'ultimo aggiornamento al dataset
            è stato eseguito in data 22-11-2024
            
            '''
    return(text)


'''
Funzione che dal dataframe generato dal file csv, si vanno a selezionare i dati 
del numero dei veicoli venduti per ogni produttore di auto presente nel dataset

Param: 
    dataframe: dataframe dei dati
Return:
    dataframe: dataframe che contiene PRODUTTORE e NUMERO DI VENDITE
'''
def make_pop_data(data):
    data = (
        data
        .group_by('Make')
        .agg(
            Vendita_per_marca = pl.col('Make').count()
        )
        .sort('Vendita_per_marca', descending = True)
    )
    return(data)

'''
Testo che spiega il grafico che sarà presente alla destra della spiegazione

Return:
    text: testo della spiegazione
'''
def text_make_pop_data(data):
    data_mod = (
        data
        .group_by('Make')
        .agg(
            Vendita = pl.col('Make').count()
        )
        .sort('Vendita', descending = True)
        .select('Make')
    )

    data_list = data_mod.rows()[0:4]
    text = f'''Nella tabella presente di lato si vede quante auto
            sono state vendute da ogni venditore presente nello stato di washington 
            dal 2011 al 2024, inoltre sono presenti i dati delle auto ordinate che 
            verranno consegnate nel 2025.  
            :orange[***Marchi più venduti***]  
            •{
                '\n•'.join( [ element[0] for element in data_list])
            }
            \n:orange[***Considerazioni***]  
            Nelle prossime analisi si vedranno quali sono i modelli più venduti
            e cercheremo di capire i motivi. '''
    return(text)


'''
Funzione che serve a creare una lista in cui sono presenti tutti i produttori di veicoli
elettrici e ibridi presenti nel dataframe

Param: 
    dataframe: dataframe dei dati 
Return:
    list: lista dei produttori
'''
def make_list(data):
    return data['Make'].unique().sort().to_list()

'''
Funzione che ha l'obiettivo di creare un grafico a linee 
in cui in base ai produttore scelti dall'utente si vedranno il numero di auto 
vendute da ogni produttore selezionato per ogni anno. 

Param: 
    dataframe: dataframe dei dati
    list: lista dei produttori selezionati

Return:
    chart: grafico a linee
'''
def make_per_year (data, make):

    data = (
        data
        .group_by('Make', 'Model Year')
        .agg(
            Vendita_per_marca = pl.col('Make').count()
        )
        .filter(pl.col('Make').is_in(make))
    )

    chart = alt.Chart(data).encode( 
        color= alt.Color(
                'Make:N',
                scale=alt.Scale(scheme='darkred')
            )
    ).properties(
        width = 750
    )

    line = chart.mark_line().encode(
        x = 'Model Year:O',
        y = 'Vendita_per_marca:Q'
    )

    label = chart.encode(
        x = 'max(Model Year):O',
        y = alt.Y('Vendita_per_marca:Q').aggregate(argmax='Model Year'),
        text = 'Make'
    )

    text = label.mark_text(align='left', dx = 4)

    circle = label.mark_circle()

    return line + text + circle


'''
Funzione che va a generare grafici a torta per ogni produttore scelto dall'utente.
Per ogni produttore saranno visibili il numero di modelli venduti. 
Il numero massimo di grafici visibili sarà 3. 
La creazione dei grafici viene a seguito di una manipolazione dei dati.

Param:
    dataframe: dataframe dei dati 
    list: lista di produttore selezionati dall'utente
'''
def model_per_make(data, make):

    '''
    Seleziono i dati che sono essenziali per creare il grafico
    '''
    data_agg = (
        data
        .group_by('Make', 'Model')
        .agg(
            Vendita_per_modello = pl.col('Model').count(),         
        )
        .filter(pl.col('Make').is_in(make))
    )

    '''
    A causa di alcuni modelli che hanno poche vendite seleziono il range (<1% del totale delle auto 
    vendute da un venditore) tale per cui tutti i modelli verranno inseriti nella categoria altro.
    '''
    data_agg = data_agg.with_columns(
        pl.col('Vendita_per_modello').sum().over('Make').alias('Totale_Produttore'),
    ).with_columns(
        (pl.col('Vendita_per_modello') < (0.01 * (pl.col('Totale_Produttore')))).alias('OneP')
    ).with_columns(
        pl.when(pl.col('OneP') == True)
        .then(pl.lit('ALTRO'))
        .otherwise(pl.col('Model'))
        .alias('Model')
    )

    '''
    Ritorno al dataset in cui le colonne presenti saranno 'Make' - 'Model' - 'Vendita_per_modello'
    '''
    data_agg = (
        data_agg
        .group_by('Make', 'Model')
        .agg(
            Vendita_per_modello = pl.col('Vendita_per_modello').sum()
        )
    )

    base_pie = (
        alt.Chart(data_agg)
        .mark_arc(
            radius = 80,
            radius2 = 120,
            cornerRadius=20
        )
        .encode(
            alt.Theta('Vendita_per_modello:Q'),
            alt.Color('Model:N',
                      scale=alt.Scale(scheme='darkred')).legend(None)
        ) 
    )  

    text_pie = (
        alt.Chart(data_agg)
        .mark_text(
            radius = 150,
            size = 12,
            color='white'
        )
        .encode(
            alt.Text('Model:N'),
            alt.Theta('Vendita_per_modello:Q', stack=True),
            alt.Order('Model:N')
        )
    )

    text_total = (
        alt.Chart(data_agg)
        .mark_text(
            radius = 0,
            size=30,
            color='cyan',
            baseline='middle'
        )
        .encode(
            alt.Text("Make:N")
        )
    )

    chart = (
        base_pie+text_pie+text_total
    ).properties(
        height = 60,
        width = 60
    ).facet(
        'Make', columns=3
    ).resolve_scale(
        color='independent'
    )

    return(chart)

'''
Funzione che crea una mappa con visualizzazione 3D in cui si vede
dove sono state immatricatolate le auto nello stato di Washington 
andando a creare una specie di scatterplot in cui le barre più elevate
indicano una zona in cui l'immatricolazione delle auto è maggiore. 

Param: 
    dataframe: dataframe dei dati 
'''
def map_3d(data):
    coord_list = []

    #selezione dei dati da usare
    data = (
        data.select(pl.col('Vehicle Location'))
    )

    #manipolazione della colonna della geolocalizzazione
    for row in data.rows():
        if row[0] is not None:
            numb = re.findall(r'-?\d+\.\d+|-?\d+', row[0])
            coord = (float(numb[0]), float(numb[1]))
            coord_list.append(coord)

    #creazione del dataframe utile per la creazione del grafico
    coord_chart = pd.DataFrame(coord_list, columns=['lon', 'lat'])
    coord_chart = coord_chart.sample(n=100)

    #creazione del grafico tramite libreria PyDeck
    return(
        pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=48,
                longitude=-122,
                zoom=7,
                pitch=60,
            ),
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=coord_chart,
                    get_position="[lon, lat]",
                    radius=2000,
                    elevation_scale=50,
                    elevation_range=[100, 1000],
                    pickable=True,
                    extruded=True,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data=coord_chart,
                    get_position="[lon, lat]",
                    get_color="[200, 30, 0, 160]",
                    get_radius=200,
                ),
            ],
        )
    )

'''
Funzione che crea grafici a torta in cui si vede come sono distribuite le auto immatricolate
per marca rispetto alla tipologia di motore. 

Param: 
    dataset: dataset dei dati
    list: lista delle marche che si desidera analizzare

Return: 
    chart: grafici che rappresentano la distribuzione dei motori
'''
def engine_type_per_make (data, make):

    data_type_engine = (
        data
        .group_by('Make', 'Electric Vehicle Type')
        .agg(
            Engine = pl.col('Electric Vehicle Type').count()
        )
        .filter(
            pl.col('Make').is_in(make)
        )
    )

    data_type_engine = data_type_engine.with_columns(
        pl.col('Electric Vehicle Type').replace({
            'Plug-in Hybrid Electric Vehicle (PHEV)': 'PHEV',
            'Battery Electric Vehicle (BEV)': 'BEV'
        })
    )

    base_pie = (
        alt.Chart(data_type_engine)
        .mark_arc(
            radius = 80,
            radius2 = 120,
            cornerRadius=20
        )
        .encode(
            alt.Color('Electric Vehicle Type:N',
                      scale=alt.Scale(scheme='darkred')).legend(None),
            alt.Theta('Engine:Q')
        )
    )

    text_pie = (
        alt.Chart(data_type_engine)
        .mark_text(
            radius = 150,
            size = 15,
            color='cyan'
        )
        .encode(
            alt.Text('Electric Vehicle Type:N'),
            alt.Theta('Engine:Q', stack=True),
            alt.Order('Electric Vehicle Type:N')
        )
    )

    text_total = (
        alt.Chart(data_type_engine)
        .mark_text(
            radius = 0,
            size=30,
            color='cyan',
            baseline='middle'
        )
        .encode(
            alt.Text("Make:N")
        )
    )

    chart = (
        base_pie+text_pie+text_total
    ).properties(
        height = 45,
        width = 45
    ).facet(
        'Make', columns=3
    ).resolve_scale(
        color='independent'
    )


    return chart


'''
Funzione che mi crea una lista dei produttore che hanno venduto almeno il 0.5% delle auto presenti
nel dataset. 

Param
    dataset: dataset dei dati

Return
    list: lista contenente i produttori di auto con almneo 0.5% di vendite
'''
def maker_list_over_25(data):

    data = (
        data
        
        .group_by('Make')
        .agg(
            Vendita_per_marca = (pl.col('Make').count() / len(data)*100).round(3)
        )
        .filter(pl.col('Vendita_per_marca') > .5)
    )

    return data['Make'].unique().sort().to_list()

'''
Funzione che va a generare la pagina di dashboard
'''
def dashboard_main():

    data = read_data()
   
    st.title(':orange[DASHBOARD]')
    st.divider()
    
    #PRIMO CONTAINER
    st.title('Vendita auto BEV/PHEV')
    c1 = st.container(border=False)

    col1c1, col2c1 = c1.columns(2)

    col1c1.altair_chart(year_pop_chart(data), use_container_width=True)
    col2c1.markdown(text_year_pop_chart(data.height))

    #SECONDO CONTAINER
    c2 = st.container(border=False)
    c2.subheader('Totale Vendite')

    col1c2, col2c2 = c2.columns(2)
    col2c2.dataframe(make_pop_data(data))
    col1c2.markdown(text_make_pop_data(data))
    
    
    #TERZO CONTAINE
    c3 = st.container(border=False)
    c3.title('Distribuzione vendite stato Washington')
    c3.pydeck_chart(map_3d(data))

    st.divider()
    
    #QUARTO CONTAINER

    c4 = st.container(border=False)
    c4.title('Analisi vendita per produttore')

    #make_selection è una lista di al massimo 3 marchi
    st.session_state.make_selection = c4.multiselect('''E' possibile scegliere al massimo 3 marchi''',
                                                     make_list(data), max_selections=3, default=['TESLA'])
    
    c4.altair_chart(make_per_year(data, st.session_state.make_selection))

    #QUINTO CONTAINER
    c5 = st.container(border=False)
    c5.subheader('Analisi vendita per modello')
    c5.altair_chart(model_per_make(data, st.session_state.make_selection), use_container_width=True)

    #SESTO CONTAINER
    c6 = st.container(border=False)
    c6.subheader('Analisi vendita per tipologia di motore')
    c6.altair_chart(engine_type_per_make(data, st.session_state.make_selection))

    #SETTIMO CONTAINER
    c7 = st.container(border = True)
    c7.subheader('Analisi per produttore')

    c7.write('''In questa parte del programma, la lista di produttori è minore rispetto 
             all'originale, questo perchè per creare dei report più soddisfacenti è stata fatta una scelta,
             a seguito di un'analisi, di eliminare i produttore di auto che hanno venduto meno dello 0.5% delle
             auto presenti nel dataset.''')

    #è una stringa di al massimo un marchio
    st.session_state.prod_selection = c7.selectbox('''E' possibile scegliere al massimo UN marchio''',
                                                     maker_list_over_25(data))
    
    #c7.write(maker_list_over_25(data))
    
if __name__ == '__main__':
    dashboard_main()
    