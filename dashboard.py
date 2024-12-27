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
                scale=alt.Scale(scheme='oranges')
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
                      scale=alt.Scale(scheme='oranges')).legend(None)
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
                      scale=alt.Scale(scheme='oranges')).legend(None),
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
Funzione che mi crea una lista dei produttore che hanno venduto almeno il 0.25% delle auto presenti
nel dataset. 

Param
    dataset: dataset dei dati

Return
    list: lista contenente i produttori di auto con almneo 0.25% di vendite
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
Funzione che mi crea un piccolo report sul produttore che viene selezionato
'''
def maker_small_report(data, maker, model_list): 

    # Primo anno in cui il produttore ha venduto un auto nello stato di Washington
    first_year = (
        data
        .filter(pl.col('Make') == maker)
        .select(pl.col('Model Year')).min().item()
    )

    # Numero di auto vendute dal produttore nello stato di Washington
    sell_car_count = (
        data
        .filter(pl.col('Make')== maker)
        .select(pl.col('Make')).count().item()  
    )

    # Numero di modelli venduti dal produttore nello stato di Washington
    total_model_make = (
        data
        .filter(pl.col('Make') == maker)
        .select(pl.col('Model')).unique().count().item()
    )

    data = (
        data
        .group_by('Make', 'Model', 'Model Year')
        .agg(
            Total = pl.col('Model').count()
        )
        .filter(pl.col('Make')==maker)
        .filter(pl.col('Model').is_in(model_list))
        .filter(pl.col('Total')>15)
        .sort(pl.col('Model Year'))
    )

    chart = alt.Chart(data).encode( 
        color= alt.Color(
                'Model:N',
                scale=alt.Scale(scheme='oranges')
            )
    ).properties(
        width = 750
    )

    line = chart.mark_line().encode(
        x = 'Model Year:O',
        y = 'Total:Q'
    )

    label = chart.encode(
        x = 'max(Model Year):O',
        y = alt.Y('Total:Q').aggregate(argmax='Model Year'),
        text = 'Model'
    )

    text = label.mark_text(align='left', dx = 4)

    circle = label.mark_circle()

    compl_chart = line+text+circle

    #return line + text + circle

    return first_year, sell_car_count, total_model_make, compl_chart


'''
Funzione che in base al produttore che viene passato come parametro
ritorna una lista contenente i modelli delle auto ordinati in base al numero 
di auto vendute per quel modello

Param: 
    dataframe: dataframe dei dati
    string: nome del produttore

Return: 
    list: lista contenente i modelli del produttore
'''
def model_list_by_maker(data, make):

    data = (
        data
        .filter(pl.col('Make') == make)
        .group_by('Make', 'Model')
        .agg(
            Total = pl.col('Model').count()
        )
        .sort('Total', descending = True)
    )


    return data['Model'].to_list()


'''
Funzione che mi genera un grafico con l'autonomia massima e minima per ogni produttore
PARAM
    dataset: dataset delle auto
RETURN
    chart: grafico a barre in cui si vede per alcuni marchi il range massimo e il minimo venduto
    dataset: dataset in cui si vede per ogni produttore range massimo e minimo
'''
def electric_range(data):
    data_range_prod = (
        data
        .select('Make', 'Electric Range', 'Electric Vehicle Type')
        .filter(pl.col('Electric Range') > 0 )
    )
    data_range_prod = data_range_prod.with_columns(
        pl.col('Electric Vehicle Type').replace({
            'Plug-in Hybrid Electric Vehicle (PHEV)': 'PHEV',
            'Battery Electric Vehicle (BEV)': 'BEV'
        })
    )

    range_graph = (
        data_range_prod
        .group_by('Make','Electric Range', )
        .agg(
            Count = pl.col('Electric Range').count()
        )
        .sort('Make')
    )

    make_list = (
        data_range_prod
        .group_by('Make')
        .agg(
            Count = pl.col('Make').count()/data_range_prod.height*100
        )
        .filter(pl.col('Count') > 0.5)
    )

    make_list = make_list['Make'].unique().sort().to_list()
    
    filtered_data = (
        range_graph
        .group_by("Make")
        .agg([
            pl.col("Electric Range").max().alias("Max Range"),
            pl.col("Electric Range").min().alias("Min Range"),
        ])
        #.filter((pl.col("max_Electric_Range") - pl.col("min_Electric_Range")) < 5)
    )

    tot_electric_range = filtered_data

    filtered_data = (
        filtered_data
        .filter((pl.col("Max Range") - pl.col("Min Range")) < 5)
    )

    filter_list = filtered_data['Make'].unique().sort().to_list()
    
    range_graph_filt = (
        range_graph
        .filter(pl.col('Make').is_in(list(set(make_list) - set(filter_list))))
    )
    bar = (
        alt.Chart(range_graph_filt)
        .mark_bar(cornerRadius=10, height=10)
        .encode(
            x = alt.X('min(Electric Range):Q').scale(domain=[-15, 350]).title('Electric Range'),
            x2 = 'max(Electric Range):Q',
            y = alt.Y('Make:N', sort = '-x').title(None),
            color=alt.value('orange')
        )
    )

    text_min = (
        alt.Chart(range_graph_filt)
        .mark_text(align='right', dx = -5, color='white')
        .encode(
            x = 'min(Electric Range):Q',
            y = alt.Y('Make:N'),
            text = 'min(Electric Range):Q'
        )
    )

    text_max = (
        alt.Chart(range_graph_filt)
        .mark_text(align='left', dx = 5, color='whitesmoke')
        .encode(
            x = 'max(Electric Range):Q',
            y = alt.Y('Make:N'),
            text = 'max(Electric Range):Q'
        )
    )

    (bar + text_min + text_max).properties(
        title = alt.Title(text = 'Electric Range')
    )
    return (bar + text_min + text_max).properties(
        title = alt.Title(text = 'Electric Range')
    ), tot_electric_range

'''
Funzione che ritorna un grafico che mostra la distribuzione di auto vendute in base alla tipologia 
del motore e l'autonomia del motore elettrico.

PARAM
    dataset: dataset delle auto

RETURN
    chart: grafico in cui si mostra la distribuzione per colore delle auto vendute in base all'autonomia
'''

def engine_distribution(data):

    #Organizziamo il dataset per ottenere un dataset utile per creare il grafico
    data = (
        data
        .select('Electric Vehicle Type', 'Electric Range')
        .filter(pl.col('Electric Range') > 0)
    )

    data = (
        data
        .group_by('Electric Vehicle Type', 'Electric Range')
        .agg(
            Count = pl.col('Electric Range').count()
        )
        .sort(pl.col('Electric Range'))
    )

    data = data.with_columns(
        pl.col('Electric Vehicle Type').replace({
            'Plug-in Hybrid Electric Vehicle (PHEV)': 'PHEV',
            'Battery Electric Vehicle (BEV)': 'BEV'
        })
    )

    base = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, opacity=0.8)
        .encode(
            x = ('Electric Range:Q'),
            y = alt.Y('Count:Q'),
            color= alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='purpleorange'))
        )
        .properties(width=800)  
        
    )

    return base


'''
Funzione che mi crea le etichette per aggiungere informazioni
'''

def range_label(data):
    data_label = (
    data
    .select('Electric Vehicle Type', 'Electric Range')
    .filter(pl.col('Electric Range') > 0)
    )

    data_label = data_label.with_columns(
        pl.col('Electric Vehicle Type').replace({
            'Plug-in Hybrid Electric Vehicle (PHEV)': 'PHEV',
            'Battery Electric Vehicle (BEV)': 'BEV'
        })
    )

    #numero record con cui si esegue l'analisi
    car_count = data_label.height

    #media dell'autonomia delle auto
    data_mean = (
        data_label
        .mean()
        .select('Electric Range').item()
    )
    
    #calcoliamo il numero di auto e la media in base al motore
    data_mean_by_engine = (
        data_label
        .group_by('Electric Vehicle Type')
        .agg(
            Count = pl.col('Electric Range').count(),
            Mean = pl.col('Electric Range').mean()
        )
        .with_columns(
            pl.col('Mean').round(2).alias('Mean')  
        )
    )

    return (car_count, round(data_mean,2),
            data_mean_by_engine.row(0)[1],data_mean_by_engine.row(0)[2],
            data_mean_by_engine.row(1)[1],data_mean_by_engine.row(1)[2])


@st.cache_data
def strip_plot(_data):

    data_strip_plot = (
        _data
        .select('Make', 'Electric Range', 'Electric Vehicle Type')
        .filter(pl.col('Electric Range') > 0 )
    )
    data_strip_plot = data_strip_plot.with_columns(
        pl.col('Electric Vehicle Type').replace({
            'Plug-in Hybrid Electric Vehicle (PHEV)': 'PHEV',
            'Battery Electric Vehicle (BEV)': 'BEV'
        })
    )

    gaussian_jitter = alt.Chart(data_strip_plot).mark_circle(size = 8).encode(
        y = 'Electric Vehicle Type:N',
        x = 'Electric Range:Q',
        yOffset='jitter:Q',
        
        color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='oranges')).legend(None)
    ).transform_calculate(
        jitter = "sqrt(-2*log(random()))*cos(2*PI*random())"
    ).properties(
        height= 500,
        width = 650
    )

    return gaussian_jitter.resolve_scale(yOffset='independent')



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
             a seguito di un'analisi, di eliminare i produttore di auto che hanno venduto meno dello 0.25% delle
             auto presenti nel dataset.''')

    #è una stringa di al massimo un marchio
    st.session_state.prod_selection = c7.selectbox('''E' possibile scegliere al massimo UN marchio''',
                                                     maker_list_over_25(data))
    
    st.session_state.model_list = model_list_by_maker(data, st.session_state.prod_selection)
    
    c7.divider()

    c7.markdown(f'''<h2 style='text-align: center;'>
                Report del produttore: 
                <span style='color: orange; font-weight: bold;'>{st.session_state.prod_selection}</span>
                </h2>''', 
                unsafe_allow_html=True)

    col1c7, col2c7 = c7.columns(spec=[.2,.8])
    
    st.session_state.model_selection = col2c7.multiselect("E' possibile scegliere al massimo 2 modelli",
                                                      st.session_state.model_list,
                                                      max_selections=2, default=st.session_state.model_list[0])

    st.session_state.report = maker_small_report(data,
                                               st.session_state.prod_selection,
                                               st.session_state.model_selection)
    
    
    
    col1c7.metric(label="**Primo anno di vendita**", value=st.session_state.report[0])
    col1c7.metric(label="**Totale auto vendute**", value=st.session_state.report[1])
    col1c7.metric(label="**Numero di modelli venduti**", value = st.session_state.report[2])

    col2c7.altair_chart(st.session_state.report[3], use_container_width=True)

    st.divider()

    st.title('Analisi tecnica delle auto')

    
    #OTTAVO CONTAINER
    c8 = st.container()

    c8.subheader('Distribuzioni autonomia delle auto')

    col1c8, col2c8 = c8.columns(spec=[.6,.4])

    col1c8.altair_chart(engine_distribution(data), use_container_width=True)
    st.session_state.range_label = range_label(data)
    '''col2c8.metric(label = '**Numero totale EV**', value = st.session_state.range_label[2])
    col2c8.metric(label = '**Media autonomia EV**', value = st.session_state.range_label[3])
    col2c8.metric(label = '**Numero totale PHEV**', value = st.session_state.range_label[4])
    col2c8.metric(label = '**Media autonomia PHEV**', value = st.session_state.range_label[5])'''

    a,b = col2c8.columns(2)
    a.metric(label = '**Numero totale auto**', value = st.session_state.range_label[0])
    b.metric(label = '**Media autonomia**', value = st.session_state.range_label[1])
    a.divider()
    b.divider()
    a.metric(label = '**Numero totale EV**', value = st.session_state.range_label[2])
    b.metric(label = '**Media autonomia EV**', value = st.session_state.range_label[3])
    a.divider()
    b.divider()
    a.metric(label = '**Numero totale PHEV**', value = st.session_state.range_label[4])
    b.metric(label = '**Media autonomia PHEV**', value = st.session_state.range_label[5])


    st.divider()


    #NONO CONTAINER
    c9 = st.container()
    electric_range_result = electric_range(data)
    col1c9, col2c9, col3c9 = c9.columns(3)
    col3c9.altair_chart(electric_range_result[0])
    col2c9.write(electric_range_result[1])
    col1c9.subheader('Spiegazione')
    
    #DECIMO CONTAINER
    st.divider()
    c10 = st.container()

    col1c10, col2c10 = c10.columns(spec=[0.8, 0.2])
    col1c10.altair_chart(strip_plot(data))
    col2c10.subheader('Spiegazione')

    #UNDICESIMO CONTAINER
    st.divider()
    
    c11 = st.container()

    col1c11, col2c11 = c11.columns(spec=[0.2, 0.8])

    col1c11.subheader('Spiegazione')

if __name__ == '__main__':
    dashboard_main()
    