import streamlit as st
import polars as pl
import altair as alt
import re
import pydeck as pdk
import pandas as pd
from pathlib import Path


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


def year_pop_chart(data):
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
    data_chart = (
        data
        .group_by('Model Year', 'Electric Vehicle Type')
        .agg(
            vendite_annuali = pl.col('Model Year').count()
        )
        .sort(pl.col('Model Year'), descending=False)
    )
    
    chart = (
        alt.Chart(
            data_chart,
            #title = alt.Title('Vendita annuale di auto elettrico o ibride')
        )
        .mark_bar() 
        .encode(
            y='vendite_annuali:Q',
            x= 'Model Year:O',
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='oranges'))
        )
    )
    return(chart)


def text_year_pop_chart(number):
    '''
    Testo che spiega il grafico che sarà presente alla sinistra della spiegazione

    Param:
        int: numero di auto presenti nel database
    Return:
        text: testo della spiegazione
    '''
    return(f"""
    <div style='border:2px solid orange; padding:20px; border-radius:5px; margin-bottom:30px; margin-right:30px; font-size:16px;'>
        <span style="color: orange; font-weight: bold;">Informazioni</span><br>
        <strong><span style="color: orange;">1)</span></strong> Il dataset presenta le auto BEV/PHEV presenti nel sito Data.gov (si guardi documentazione per il link).<br>
        <strong><span style="color: orange;">2)</span></strong> Il totale di auto vendute per questa analisi è:
        <span style="background-color: orange; color: black; font-weight: bold; padding: 5px; border-radius: 3px;">{number}</span><br>
        <strong><span style="color: orange;">3)</span></strong> I dati sono stati scaricati in data 10-12-2024, e l'ultimo aggiornamento al dataset
        è stato eseguito in data 22-11-2024 <br>
        <strong><span style="color: orange;">4)</span></strong> L'obiettivo dell'analisi è quello di rappresentare e cercare di spiegare le informazioni presenti nel dataset. 
        <br>I dati verranno presentati graficamente e saranno affiancati da etichette/label oppure da spiegazioni o riassunti sui grafici. <br>
        <strong><span style="color: orange;">5)</span></strong> I dati sull'autonomia sono in <strong>Miglia</strong>, mentre i dati sul costo
        a listino delle auto sono in <strong>Dollari</strong>.
    </div>
    """)
    



def make_pop_data(data):
    '''
    Funzione che dal dataframe generato dal file csv, si vanno a selezionare i dati 
    del numero dei veicoli venduti per ogni produttore di auto presente nel dataset

    Param: 
        dataframe: dataframe dei dati
    Return:
        dataframe: dataframe che contiene PRODUTTORE e NUMERO DI VENDITE
    '''
    data = (
        data
        .group_by('Make')
        .agg(
            Vendita_per_marca = pl.col('Make').count()
        )
        .sort('Vendita_per_marca', descending = True)
    )
    return(data)


def text_make_pop_data(data):
    '''
    Testo che spiega il grafico che sarà presente alla destra della spiegazione

    Return:
        text: testo della spiegazione
    '''
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
    text = f"""
    <div style='border:2px solid orange; padding:20px; border-radius:5px; margin-bottom:30px; font-size:16px;'>
        Nella tabella di lato sono presenti i dati di vendita di ogni produttore presente nel dataset. <br>
        I dati sono stati filtrati, mantenendo solo i dati dal 2011 al 2025. <br>
        <span style="color: orange; font-weight: bold;">Marchi più venduti</span>
        <ul>
            {"".join(f'''<span style= "font-weight: bold;"><li>{element[0]}</li></span>''' for element in data_list)}
        </ul>
        <span style="color: orange; font-weight: bold;">Considerazioni</span>
        <ul>
            <li>Sono presenti dati del 2025 a causa degli ordini che non riescono ad essere consegnati nel 2024.</li>
            <li>Gli utenti che hanno permessi i permessi di <strong>Vendita</strong> avranno la possibilità di aggiungere 
            ulteriori dati al dataset così da tener aggiornata la dashboard nel tempo.</li>
        </ul>
        
    </div>
    """
    return(text)



def make_list(data):
    '''
    Funzione che serve a creare una lista in cui sono presenti tutti i produttori di veicoli
    elettrici e ibridi presenti nel dataframe

    Param: 
        dataframe: dataframe dei dati 
    Return:
        list: lista dei produttori
    '''
    return data['Make'].unique().sort().to_list()


def make_per_year (data, make):
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



def model_per_make(data, make):
    '''
    Funzione che va a generare grafici a torta per ogni produttore scelto dall'utente.
    Per ogni produttore saranno visibili il numero di modelli venduti. 
    Il numero massimo di grafici visibili sarà 3. 
    La creazione dei grafici viene a seguito di una manipolazione dei dati.

    Param:
        dataframe: dataframe dei dati 
        list: lista di produttore selezionati dall'utente
    '''

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

def map_3d(data):
    '''
    Funzione che crea una mappa con visualizzazione 3D in cui si vede
    dove sono state immatricatolate le auto nello stato di Washington 
    andando a creare una specie di scatterplot in cui le barre più elevate
    indicano una zona in cui l'immatricolazione delle auto è maggiore. 

    Param: 
        dataframe: dataframe dei dati 
    '''
    # Ottimizzazione 1: Selezione dati più efficiente
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


def engine_type_per_make (data, make):
    '''
    Funzione che crea grafici a torta in cui si vede come sono distribuite le auto immatricolate
    per marca rispetto alla tipologia di motore. 

    Param: 
        dataset: dataset dei dati
        list: lista delle marche che si desidera analizzare

    Return: 
        chart: grafici che rappresentano la distribuzione dei motori
    '''
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



def maker_list_over_25(data):
    '''
    Funzione che mi crea una lista dei produttore che hanno venduto almeno il 0.25% delle auto presenti
    nel dataset. 

    Param
        dataset: dataset dei dati

    Return
        list: lista contenente i produttori di auto con almneo 0.25% di vendite
    '''
    data = (
        data
        .group_by('Make')
        .agg(
            Vendita_per_marca = (pl.col('Make').count() / len(data)*100).round(3)
        )
        .filter(pl.col('Vendita_per_marca') > .5)
    )

    return data['Make'].unique().sort().to_list()



def maker_small_report(data, maker, model_list): 

    '''
    Funzione che mi crea un piccolo report sul produttore che viene selezionato

    PARAM
        dataset: dataset dei dati
        string: produttore selezionato
        list: lista dei modelli per creare il grafico a linee

    RETURN
        list:
            [0] integer: primo anno di vendita auto elettrico o ibrida
            [1] integer: conteggio auto vendute
            [2] integer: numero di modelli venduti
            [3] chart: grafico a linee che mostra quante auto sono state vendute per modello selezionato
    '''

    data_maker = data.filter(pl.col('Make') == maker)
    # Primo anno in cui il produttore ha venduto un auto nello stato di Washington
    first_year = (
        data_maker
        .select(pl.col('Model Year')).min().item()
    )

    # Numero di auto vendute dal produttore nello stato di Washington
    sell_car_count = (
        data_maker
        .select(pl.col('Make')).count().item()  
    )

    # Numero di modelli venduti dal produttore nello stato di Washington
    total_model_make = (
        data_maker
        .select(pl.col('Model')).unique().count().item()
    )

    # Percentuale di auto elettriche e ibride
    percentage_engine = (
        data_maker
        .group_by('Electric Vehicle Type')
        .agg(
            ((pl.col('Electric Vehicle Type').count())/data_maker.height).round(2).alias('Engine Type Percentage')
        )
        .sort(pl.col('Electric Vehicle Type'))
    )

    # Percentuale 2024 vs 2023


    data_chart = (
        data_maker
        .group_by('Make', 'Model', 'Model Year')
        .agg(
            Total = pl.col('Model').count()
        )
        .filter(pl.col('Model').is_in(model_list))
        .filter(pl.col('Total')>30)
        .sort(pl.col('Model Year'))
    )

    chart = alt.Chart(data_chart).encode( 
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

    return first_year, sell_car_count, total_model_make, compl_chart, percentage_engine



def model_list_by_maker(data, make):

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


def electric_range(data):
    '''
    Funzione che mi genera un grafico con l'autonomia massima e minima per ogni produttore
    PARAM
        dataset: dataset delle auto
    RETURN
        chart: grafico a barre in cui si vede per alcuni marchi il range massimo e il minimo venduto
        dataset: dataset in cui si vede per ogni produttore range massimo e minimo
    '''
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
            y = alt.Y('Make:N', sort = '-x'),
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



def engine_distribution(data):
    '''
    Funzione che ritorna un grafico che mostra la distribuzione di auto vendute in base alla tipologia 
    del motore e l'autonomia del motore elettrico.

    PARAM
        data: dataset delle auto

    RETURN
        chart: grafico in cui si mostra la distribuzione per colore delle auto vendute in base all'autonomia
    '''

    # Organizziamo il dataset per ottenere un dataset utile per creare il grafico
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
        .sort('Electric Range')
    )

    data = data.with_columns(
        pl.col('Electric Vehicle Type').replace({
            'Plug-in Hybrid Electric Vehicle (PHEV)': 'PHEV',
            'Battery Electric Vehicle (BEV)': 'BEV'
        })
    )

    # Convertiamo il dataset in un DataFrame Pandas per Altair
    df = data.to_pandas()

    base = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, opacity=0.8)
        .encode(
            x=alt.X('Electric Range:Q', title='Electric Range(interval of 10)',bin=alt.Bin(step=10)),
            y=alt.Y('Count:Q'),
            color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='purpleorange'), legend=None)
        )
    )

    return base



def range_label(data):

    '''
    Funzione che mi crea le etichette per aggiungere informazioni su numero auto vendute e autonomia

    PARAM
        dataset: dataset dei dati

    RETURN
        list: lista contenente le informazioni utili per le auto
    '''

    #organizzazione dei dati
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
    # numero di auto 
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
        .sort(pl.col('Electric Vehicle Type'))
    )

    return (car_count, round(data_mean,2),
            data_mean_by_engine.row(0)[1],data_mean_by_engine.row(0)[2],
            data_mean_by_engine.row(1)[1],data_mean_by_engine.row(1)[2])


@st.cache_data
def jitter_strip_plot(_data):

    '''
    Funzione che mi genera un grafico di tipo jitter strip in base alla tipologia del motore

    PARAM: 
        dataset: dataset dei dati 

    RETURN: 
        chart: 
            ASSE Y: tipologia del motore
            ASSE X: autonomia del motore elettrico
'''

    #organizzaione dei dati
    data_strip_plot = (
        _data
        .select('Make', 'Electric Range', 'Electric Vehicle Type')
        .filter(pl.col('Electric Range') > 0 )
        .limit(10000)  
    )
    data_strip_plot = data_strip_plot.with_columns(
        pl.col('Electric Vehicle Type').replace({
            'Plug-in Hybrid Electric Vehicle (PHEV)': 'PHEV',
            'Battery Electric Vehicle (BEV)': 'BEV'
        })
    )

    #creazione del graifco 
    gaussian_jitter = alt.Chart(data_strip_plot).mark_circle(size = 8).encode(
        y = 'Electric Vehicle Type:N',
        x = 'Electric Range:Q',
        yOffset='jitter:Q',
        
        color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='purpleorange')).legend(None)
    ).transform_calculate(
        jitter = "sqrt(-2*log(random()))*cos(2*PI*random())"
    ).properties(
        height= 500,
        width = 500
    )

    return gaussian_jitter.resolve_scale(yOffset='independent')


@st.cache_data
def make_jitter_strip_plot(_data, make): 

    '''
    Grafico che mi genera un jitter strip plot per le auto che fanno parte della lista passata come parametro.
    Inoltre si vedono colori differenti in base alla tipologia del motore. 

    PARAM
        dataset: dataset dei dati
        list: lista delle auto che compongono il grafico

    RETURN
        chart: grafico di tipo jitter strip plot: 
                ASSE Y: produttore di auto
                ASSE X: autonomia del motore elettrico
                COLORE: tipologia del motore
    '''

    # Crea lista vuota per dataframe filtrati
    df_list = []

    # Per ogni marca richiesta:
    # - Filtra per marca specifica
    # - Limita a 1000 record, per motivi di complessità computazionale
    for i in make:
        df_list.append(
            _data
            .select('Make', 'Electric Range', 'Electric Vehicle Type')
            .filter(pl.col('Make') == i)
            .filter(pl.col('Electric Range') > 0)
            .limit(1000)
        )

    # Concatena risultati o crea DataFrame vuoto se nessun dato
    if len(df_list) > 0:
        jitter_plot = pl.concat(df_list)
    else:
        jitter_plot = pl.DataFrame(schema={"Make": pl.Utf8, "Electric Range": pl.Int32, "Electric Vehicle Type": pl.Utf8})

    
    # Creo grafico con Altair
    gaussian_jitter = alt.Chart(jitter_plot).mark_circle(size = 8).encode(
        y = 'Make:N',
        x = 'Electric Range:Q',
        yOffset='jitter:Q',
        color=alt.Color(
            'Electric Vehicle Type:N',
            scale=alt.Scale(
                domain=['BEV', 'PHEV'],  # Categorie fisse
                range=['#9F9DB6', '#CBA575']  # Colori predefiniti per BEV e PHEV
        )
    )
    ).transform_calculate(
        jitter = "sqrt(-2*log(random()))*cos(2*PI*random())"
    ).properties(
        width = 700,
        height= 500
    )

    return (gaussian_jitter).resolve_scale(yOffset='independent')
    

def make_jitter_strip_list(data):
    '''
    Funzione che mi genera la lista per scegliere i produttori in base a dei parametri 
    per creare gli jitter strip plot

    PARAM
        dataset: dataset dei dati

    RETURN
        list: lista dei produttori che rispettano determinati parametri
    '''
    make_jitter_list = []

    data_range_prod = (
        data
        .select('Make', 'Electric Range', 'Electric Vehicle Type')
        .filter(pl.col('Electric Range') > 0 )
    )

    range_data = (
        data_range_prod
        .group_by('Make','Electric Range', )
        .agg(
            Count = pl.col('Electric Range').count()
        )
        .sort('Make')
    )

    make_data = (
        data_range_prod
        .group_by('Make')
        .agg(
            Count = pl.col('Make').count()/data_range_prod.height*100
        )
        .filter(pl.col('Count') > 0.5)
    )

    make_jitter_list = make_data['Make'].unique().sort().to_list()

    filtered_data = (
        range_data
        .group_by("Make")
        .agg([
            pl.col("Electric Range").max().alias("Max Range"),
            pl.col("Electric Range").min().alias("Min Range"),
        ])
        .filter((pl.col("Max Range") - pl.col("Min Range")) < 5)
    )

    filter_list = filtered_data['Make'].unique().sort().to_list()


    return list(set(make_jitter_list) - set(filter_list))



def year_mean_price(data):
    '''
    Funzione che mi genera un grafico a linee in cui si vede 
    l'andamento medio del prezzo delle auto diviso per tipologia del motore.

    PARAM
        dataset: dataset dei dati

    RETURN
        chart: grafico che mostra l'andamento della media dei prezzi negli anni
    '''
    data_mean_price = (
        data
        .filter(pl.col('Base MSRP') > 0)
        .group_by('Model Year')
        .agg(
            Mean = pl.col('Base MSRP').mean(),
            Count = pl.col('Model Year').count()
        )
        .filter(pl.col('Count')>100)
        .sort('Model Year')
    )

    return (
        alt.Chart(data_mean_price).mark_line(point={'color': 'orange', 'size': 30}, color='orange').encode(
            x='Model Year:O',
            y='Mean:Q',
        ).properties(
            width = 500
        )
    )



def range_price_scatter_plot(data):
    '''
    Funzione che mi crea uno scatter plot per vedere come cambia il prezzo delle auto in base
    all'autonomia e alla tipologia del motore

    PARAM
        dataset: dataset dei dati

    RETURN
        chart: scatterplot in cui si vedono autonomia e range di elettrico, con la suddivisione
            per la tipologia di motore
    '''
    data_scatter_plot = (
        data
        .filter(pl.col('Base MSRP') > 0)
        .select('Base MSRP', 'Electric Range', 'Electric Vehicle Type')
        .filter(pl.col('Electric Range') > 0)
        .filter(pl.col('Base MSRP') < 120000)
    )

    scatter_plot = alt.Chart(data_scatter_plot).mark_point().encode(
                        x='Electric Range:Q',
                        y='Base MSRP:Q',
                        color=alt.Color('Electric Vehicle Type:N', scale=alt.Scale(scheme='purpleorange')),
                        size= 'count()'
                    ).properties(
                        width=600
                    )

    return scatter_plot

'''
Funzione che ritorna il testo che spiega la funzionalità della mappa 3d

RETURN
    string: testo esplicativo
'''
def map_3d_text():
    text = f'''
    <div style='border:2px solid orange; padding:20px; border-radius:5px; margin-bottom:30px; font-size:16px;'>
        Mappa 3d interattiva, che ha l'obiettivo di mostrare come sono 
        distribuiti i dati all'interno dello stato di <span style = "color: orange; font-weight: bold;">Washington</span>.  
        Barre più alte, o colori che tendono al rosso, indicano una maggior concentrazione di dati
        in quella zona dello stato.
    </div>
    '''
    
    return text

'''
Funzione che mi calcola la media del prezzo delle auto
PARAM
    dataset: dataset delle auto
RETURN
    list: [prezzo medio delle auto, prezzo medio BEV, prezzo medio PHEV]
'''
def mean_price(data):
    data_mean_price = (
        data
        .filter(pl.col('Base MSRP') > 0)
        .select(pl.col('Base MSRP').mean().round(2))
    )
    data_mean_price_engine = (
        data
        .filter(pl.col('Base MSRP') > 0)
        .group_by('Electric Vehicle Type')
        .agg(
            Mean = pl.col('Base MSRP').mean().round(2)
        )
        .sort(pl.col('Electric Vehicle Type'))
    )
    return(data_mean_price.row(0)[0], 
           data_mean_price_engine.row(0)[1],
           data_mean_price_engine.row(1)[1],
           data.filter(pl.col('Base MSRP') > 0).height)

'''
Funzione che va a generare la pagina di dashboard
'''
def dashboard_main():

    data = read_data()
   
    st.title(':orange[DASHBOARD]')
    st.divider()
    
    #----------------------------------------------------------------------------------------------------
    #PRIMO CONTAINER

    '''
    Container in cui verranno presentate le vendite annuali di auto suddivise per tipologia di motore.
    Inoltre sono presenti informazioni sui dati utilizzati per creare il report
    '''

    st.title('Vendita auto BEV/PHEV')
    c1 = st.container(border=False)
    c1.subheader('Vendita annuale di auto BEV e PHEV')

    col1c1, col2c1 = c1.columns(2)

    col1c1.altair_chart(year_pop_chart(data), use_container_width=True)
    col2c1.markdown(text_year_pop_chart(data.height), unsafe_allow_html=True)
  
    #----------------------------------------------------------------------------------------------------
    #SECONDO CONTAINER

    '''
    Container in cui verranno presentate le vendite totali eseguite da ogni produttore presente nel dataset.
    Inoltre verranno presentate delle considerazioni sui dati presenti
    '''

    c2 = st.container(border=False)
    c2.subheader('Totale vendite per produttore')

    col1c2, mid,col2c2 = c2.columns([3,1,2])
    
    
    col2c2.dataframe(make_pop_data(data))
    
    col1c2.markdown(text_make_pop_data(data), unsafe_allow_html=True)
    
    st.divider()
    #----------------------------------------------------------------------------------------------------
    #TERZO CONTAINER

    '''
    Container in cui sarà presente una mappa 3d interattiva in cui si vede la distribuzione delle vendite 
    di auto sulla mappa dello stato di Washington.
    '''

    c3 = st.container(border=False)
    c3.title('Distribuzione vendite stato Washington')
    c3.markdown(map_3d_text(), unsafe_allow_html=True)
    c3.pydeck_chart(map_3d(data))

    st.divider()
    
    #----------------------------------------------------------------------------------------------------
    #QUARTO CONTAINER
    
    '''
    Container in cui è presente una grafico a linee che indica il numero di vendite annuali di al massimo
    3 produttori selezionati a tramite una multiselect
    '''
    st.title('Analisi vendita per produttore')
    st.markdown("""
        <div style='border:2px solid orange; padding:20px; border-radius:5px;margin-bottom:50px;font-size:16px;'>
            In questa sezione della dashboard, l'obiettivo è quello di analizzare i <span style="color: orange; font-weight: bold">dati dei vari produttori</span>.<br>
            Si vuole fare questo in modo interattivo, mostrando approffondimenti sugli argomenti: 
            <ul>
                <li>Vendita annuale per produttore</li>
                <li>Proporzione vendita dei vari modelli</li>
                <li>Proporzione vendita per tipologia del motore</li>
                <li>Report su un solo produttore scelto</li>
            </ul>
            <span style="color: orange; font-weight: bold">Informazioni</span>
            <ul>
                <li>Sull'analisi delle proporzione di vendita per modello, i modelli di auto che hanno una percentuale totale
                inferiore all' 1%, sono stati raggruppati in una categoria: <span style="font-weight: bold">Altro</span>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    c4 = st.container(border=False)
    #make_selection è una lista di al massimo 3 marchi
    st.session_state.make_selection = c4.multiselect('''E' possibile scegliere al massimo 3 marchi''',
                                                     make_list(data), max_selections=3, default=['CHEVROLET'])
    
    c4.altair_chart(make_per_year(data, st.session_state.make_selection))

    #----------------------------------------------------------------------------------------------------
    #QUINTO CONTAINER

    '''
    Container in cui sono presenti da 1 a 3 grafici a torta, dipende dal numero di produttori selezionati
    nel multiselect presente nel container 4. 
    I grafici a torta indicano la proporzioni di modelli venduti per ogni produttore selezionato. 
    Durante la fase di analisi si è scelto un range pari a 0%-1% tale per cui i modelli che appartengono
    a questo intervallo verranno inseriti in una categoria definita 'ALTRO'.
    '''

    c5 = st.container(border=False)
    c5.subheader('Analisi vendita per modello')
    c5.altair_chart(model_per_make(data, st.session_state.make_selection), use_container_width=True)

    #----------------------------------------------------------------------------------------------------
    #SESTO CONTAINER

    '''
    Container in cui sono presenti da 1 a 3 grafici a torta, dipende dal numero di produttori selezionati
    nel multiselect presente nel container 4. 
    I grafici a torta indicano la proporzioni di tipologia di motore per ogni produttore selezionato. 
    '''
    
    c6 = st.container(border=False)
    c6.subheader('Analisi vendita per tipologia di motore')
    c6.altair_chart(engine_type_per_make(data, st.session_state.make_selection))

    #----------------------------------------------------------------------------------------------------
    #SETTIMO CONTAINER

    '''
    Container in cui è stato creato un breve report su un produttore scelto tramite una selectbox. 
    Per il produttore scelto si vedranno delle label: 
    -Primo anno di vendita
    -Totale auto vendute
    -Percentuale auto BEV
    -Percentuale auto PHEV
    -Numero di modelli venduti

    Inoltre è presente un grafico a linee in cui si vedono, di al massimo 2 modelli scelti tramite multiselect, 
    le vendite annuali dei modelli scelti. 
    '''
    
    c7 = st.container(border = True)
    
    c7.subheader('Analisi per produttore')

    c7.write('''In questa parte del programma, la lista di produttori è minore rispetto 
             all'originale, questo perchè per creare dei report più soddisfacenti è stata fatta una scelta,
             a seguito di un'analisi, di eliminare i produttore di auto che hanno venduto meno dello 0.25% delle
             auto presenti nel dataset.''')
    
    c7.write(''':orange[**Scegliere un produttore di auto per ottenere un breve report con delle informazioni sulla vendita
             di auto**.]''')

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

    if 'BEV' in st.session_state.report[4]['Electric Vehicle Type']:
        phev_value = st.session_state.report[4].filter(pl.col('Electric Vehicle Type') == 'BEV')['Engine Type Percentage'][0]
        col1c7.metric(label = "**Percentuale Auto BEV**", value = f"{phev_value*100:.0f}%")
    if 'PHEV' in st.session_state.report[4]['Electric Vehicle Type']:
        phev_value = st.session_state.report[4].filter(pl.col('Electric Vehicle Type') == 'PHEV')['Engine Type Percentage'][0]
        col1c7.metric(label="**Percentuale Auto PHEV**", value=f"{phev_value*100:.0f}%")

    col1c7.metric(label="**Numero di modelli venduti**", value = st.session_state.report[2])
    col2c7.altair_chart(st.session_state.report[3], use_container_width=True)

    st.divider()

    st.title('Analisi tecnica delle auto')

    #----------------------------------------------------------------------------------------------------
    #OTTAVO CONTAINER

    '''
    Container in cui è presente un grafico a barre con l'obiettivo di mostrare la distribuzione di auto
    in base all'autonomia del motore elettrico, con suddivisione della tipologia di colore tramite i colori. 

    Inoltre sono presenti delle label con delle informazioni aggiuntive sulle auto in base alla tipologia del motore
    - Numero totale di auto
    - Numero totale di auto BEV
    - Numero totale di auto PHEV
    - Media autonomia 
    - Media autonomia auto BEV
    - Media autonomia auto PHEV
    '''
    
    c8 = st.container()

    c8.subheader('Distribuzioni autonomia delle auto')

    c8.markdown("""
        <div style='border:2px solid orange; padding:20px; border-radius:5px;margin-bottom:50px;font-size:16px;'>
            In questa parte della dashboard, si vuole effettuare un'analisi sull'autonomia delle auto presenti nel dataset.
            La prima cosa che si nota è che la <strong>dimensione del dataset è diminuita</strong>, questo perchè nel dataset origininale
            non tutti i record hanno valorizzato il valore del campo dell'autonomia del motore elettrico in dotazione.<br> <br>
            In seguito, quando si farà riferimento al dataset in questa parte di analisi, il dataset preso in considerazione
            sarà quello con i dati che <span style="color: orange;"><strong>dispongono del campo Electric Range</strong></span>.
            Sulla destra, sotto l'etichetta: <strong>Numero Totale Auto</strong>,  si vede su quanti record è stata eseguita l'analisi.
        </div>
        """, unsafe_allow_html=True)

    col1c8, col2c8 = c8.columns(spec=[.6,.4])

    col1c8.altair_chart(engine_distribution(data), use_container_width=True)
    st.session_state.range_label = range_label(data)

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

    #----------------------------------------------------------------------------------------------------
    #NONO CONTAINER

    '''
    Container in cui si vuole mostrare, per produttore, l'autonomia massima e la minima presente nel dataset.
    Questo avviene tramite un dataframe e un grafico. 
    Nel grafico, per motivi di visualizzazione, vengono presentati i produttori con una differenza tra  range massimo
    e range minimo 'siginificativo'.
    '''

    c9 = st.container()
    c9.subheader('Analisi su autonomia massima e minima')
    c9.write('')

    electric_range_result = electric_range(data)
    col1c9, col2c9, col3c9 = c9.columns(3)
    col3c9.altair_chart(electric_range_result[0])
    col2c9.write(electric_range_result[1])
    
    col1c9.markdown("""
        <div style='border:2px solid orange; padding:20px; border-radius:5px;margin-right:40px; font-size:16px;'>
            <span style='color:orange; font-weight: bold'>Nota Bene</span> <br>
            La scelta di mostrare sia il dataframe che il grafico è per motivi di visualizzazione. 
            Se fossero stati inseriti tutti i produttori all'interno del grafico, il risultato sarebbe
            stato un grafico molto lungo in cui molti produttori avrebbero avuto una 
            <strong>riga verticale molto fina</strong>, perdendo l'<strong>efficacia</strong> del grafico.
            Per questo motivo è stato inserito il dataframe.   <br> <br>        
            <span style='color:orange; margin-top:20px; font-weight: bold'>Considerazione</span> <br>
            Potrebbe essere interessante vedere come sono distribuite le vendite all'interno del range
            di autonomia dei vari produttori.
        </div>
        """, unsafe_allow_html=True)
    
    
    #----------------------------------------------------------------------------------------------------
    #DECIMO CONTAINER

    '''
    Container in cui sarà presente un jitter strip plot con l'obiettivo di vedere come sono distribuiti 
    i dati rispetto ad autonomia in elettrico e tipologia di motore.
    '''
    
    st.divider()
    c10 = st.container()
    c10.subheader('''Distribuzione dell'autonomia delle auto per tipologia motore''')
    c10.write('')

    col1c10, col2c10 = c10.columns(spec=[0.6, 0.4])
    col1c10.altair_chart(jitter_strip_plot(data))
    col2c10.markdown("""
        <div style='border:2px solid orange; padding:10px; border-radius:5px;margin-bottom:15px;font-size:16px;'>
            <span style="color: orange; font-weight: bold">Obiettivo del grafico</span>
            <br>
            Con questo grafico si vuole analizzare, in base alla tipologia del motore, come sono distribuiti 
            i dati dell'autonomia del motore elettrico presente nelle auto. <br>      
            <br>
            <span style="color: orange; font-weight: bold">Consigli su interpretazione</span> <br>
            Un punto indica che è presente un dato di un determinato valore di autonomia dell'auto. Quindi per non
            sovrapporre i punti è stato aggiunto un valore casuale sull'asse verticale. Più una linea verticale è piena,
            più sono i dati presenti con la stessa autonomia. <br><br>
            <span style="color: orange; font-weight: bold">Esempio</span> <br> 
            Consideriamo il range 140-160, si vede come le auto BEV abbiano delle linee molto fitte, mentre le auto 
            PHEV presentino solo 2 punti isolati, quindi indica come siano molto più frequenti i motori di auto 
            BEV rispetto alle auto PHEV con questo range di autonomia. <br><br>
            <span style="color: orange; font-weight: bold">Informazioni</span> <br>
            Per motivi di visualizzazione e di complessità di calcolo, quindi aumento di tempo per la visualizzazione
            del grafico, i dati sono stati limitati a 10000.
        </div>
        """, unsafe_allow_html=True)
    #----------------------------------------------------------------------------------------------------
    #UNDICESIMO CONTAINER

    '''
    Container in cui sarà presente un jitter strip plot in cui si vedrà come sono distribuite le autonomie 
    delle auto dei produttori scelti a seguito di un multiselect. 
    Inoltre, per ogni produttore, si vedrà la distribuzione per la tipologia del motore, tramite l'uso dei colori.
    '''

    st.divider()
    
    c11 = st.container()
    c11.subheader('Distribuzione autonomia delle auto per produttore')
    c11.write('')

    col1c11, col2c11 = c11.columns(spec=[0.4, 0.6])

    col1c11.markdown("""
        <div style='border:2px solid orange; padding:10px; border-radius:5px;margin-bottom:15px;font-size:16px;margin-top:25px;'>
            <span style="color: orange; font-weight: bold">Obiettivo del grafico</span>
            <br>
            Con questo grafico si vuole analizzare come sono distribuiti 
            i dati dell'autonomia del motore elettrico presente nelle auto. Inoltro per ogni produttore
            viene visualizzata la tipologia del motore tramite l'utilizzo dei colori. <br>      
            <br>
            <span style="color: orange; font-weight: bold">Consigli su interpretazione</span> <br>
            Un punto indica che è presente un dato di un determinato valore di autonomia dell'auto. Quindi per non
            sovrapporre i punti è stato aggiunto un valore casuale sull'asse verticale. Più una linea verticale è piena,
            più sono i dati presenti con la stessa autonomia. <br><br>
            <span style="color: orange; font-weight: bold">Informazioni</span> <br>
            Per motivi di visualizzazione e di complessità di calcolo, quindi aumento di tempo per la visualizzazione
            del grafico, i dati sono stati limitati a 1000 per ogni produttore, questa quantità permette una visualizzazione
            soddisfaciente delle informazioni.
        </div>
        """, unsafe_allow_html=True)
    
    st.session_state.jitter_make_list = make_jitter_strip_list(data)

    st.session_state.jitter_make_selection = col2c11.multiselect('''E' possibile scegliere al massimo 3 modelli''', 
                        st.session_state.jitter_make_list, 
                        st.session_state.jitter_make_list[0])
    
    col2c11.altair_chart(make_jitter_strip_plot(data, 
                                                st.session_state.jitter_make_selection))
    

    #----------------------------------------------------------------------------------------------------
    st.divider()

    # Parte dell'analisi sui prezzi.

    '''
    Parte della dashboard in cui si prova a fare una breve analisi dei prezzi. 
    Questa parte risulta meno esaustiva a causa dei pochi dati rispetto alla dimensione del dataset.
    Il problema principale è che il dato sui prezzi non viene più aggiunto dal 2019.
    '''

    st.header('Analisi sui prezzi')
    st.write('')

    #DODICESIMO CONTAINER

    '''
    Container in cui sarà presente un grafico sull'andamento medio dei prezzi delle auto.
    Per eseguire ciò viene usato un grafico a linee. 
    Inoltre è affiancato da etichette che presentano il prezzo medio delle auto, e il prezzo medio delle auto 
    BEV e PHEV.
    '''
    
    c12 = st.container()
    c12.subheader('Andamento annuale del prezzo medio delle auto')

    #dati sui prezzi
    st.session_state.mean_price = mean_price(data)

    col1c12, col2c12 = c12.columns(spec=[0.5, 0.5])

    col1c12.altair_chart(year_mean_price(data))

    col2c12.markdown(f"""
        <div style='border:2px solid orange; padding:10px; border-radius:5px;margin-bottom:15px;font-size:16px;'>
            <span style="color: orange; font-weight: bold">Informazioni sull'analisi</span> <br>
            <ul>
                <li>Il numero di record usati in questa fase di analisi è di <span style="color: orange; font-weight: bold">{st.session_state.mean_price[3]}</span>, 
                    molto inferiori al 
                    numero di record del dataset originale.</li>
                <li>I dati di di questa fase di analisi si fermano all'anno 2019.</li>
                <li>Per i motivi specificato sopra, l'analisi sui prezzi non è esaustiva e affronterà solo 
                    le fasi di analisi del prezzo medio e la distribuzione delle vendite rispetto a prezzo e autonomia.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    #Creo una piccola visuale per i prezzi medi delle auto
    
    cc1c12, cc2c12, cc3c12 = col2c12.columns(3)
    cc1c12.metric('Prezzo medio Auto', value = st.session_state.mean_price[0])
    cc2c12.metric('Prezzo medio Auto BEV', value = st.session_state.mean_price[1])
    cc3c12.metric('Prezzo medio Auto PHEV', value = st.session_state.mean_price[2])
    #----------------------------------------------------------------------------------------------------
    #TREDICESIMO CONTAINER

    '''
    Container in cui sarà presente uno scatter plot in cui si vuole vedere la distribuzione del prezzo 
    rispetto all'autonomia delle auto. 
    E' presente una differenziazione della tipologia dei motori tramite l'uso dei colori. 
    '''

    st.divider()
    c13 = st.container()
    c13.subheader('Distribuzione delle vendite per prezzo e autonomia')
    c13.write('')
    col1c13, col2c13 = c13.columns(spec=[.5, .5])

    col2c13.altair_chart(range_price_scatter_plot(data))
    col1c13.markdown("""
        <div style='border:2px solid orange; padding:10px; border-radius:5px;margin-bottom:15px;font-size:16px;'>
            <span style="color: orange; font-weight: bold">Informazioni sull'analisi</span> <br>
            <ul>
                <li>I dati che avevano un prezzo di listino di base superiore ai <span style='font-weight: bold'>120000</span> dollari sono 
                     stati esclusi dai grafici per motivi di visualizzazione. Questo è stato possibili farlo
                     a causa della dimensione ridotta.</li>
                <li>I cerchi di dimensioni maggiori indicano un maggiore numero di dati che presenta la stessa
                     autonomia allo stesso prezzo.</li>    
            </ul>
            <span style="color: orange; font-weight: bold">Breve Analisi</span> <br>
            Le auto PHEV presentano una maggiore distribuzione sul prezzo rispetto alle auto BEV, sicuramente questo 
            è influenzato dal fatto che i dati che presentano il campo del prezzo base sono estremamente inferiori rispetto
            al dataset di origine. <br>
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    dashboard_main()
    