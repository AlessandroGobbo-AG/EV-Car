import streamlit as st
import polars as pl
import altair as alt

'''
Funzione che legge i dati del file csv del percorso: DATA/data.csv

Return:
    dataframe: dataframe dei dati
'''
@st.cache_data
def read_data():
    data = pl.read_csv('DATA/data.csv')
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
    text = f'''Dal grafico si nota come anno dopo anno
            la vendita di auto con motore elettrico o ibrido aumenta in modo 
            costante nello stato di Washington.  
            :orange[***Considerazioni***]  
            **1)** Il totale di auto vendute per questa analisi è:  
            :orange-background[**{number}**]  
            **2)** Si nota come tra il 2018 e i due anni successivi: 2019 e 2020, la crescita si sia
            bloccata, passando ad un calo, a causa della pandemia di covid19.
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
def text_make_pop_data():
    text = f'''Nella tabella presente di lato si vede quante auto
            sono state vendute da ogni venditore presente nello stato di washington 
            dal 2011 al 2023 (non fino alla fine).  
            :orange[***Marchi più venduti***]  
            • **TESLA**  
            • **NISSAN**  
            • **CHEVROLET**  
            • **BMW**    
            :orange[***Considerazioni***]  
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
def make_per_year(data, make):
    data = (
        data
        .group_by('Make', 'Model Year')
        .agg(
            Vendita_per_marca = pl.col('Make').count()
        )
        .filter(pl.col('Make').is_in(make))
    )

    chart = (
        alt.Chart(data)
        .mark_line(
            point=alt.OverlayMarkDef()
        )
        .encode(
            x = 'Model Year:O',
            y = 'Vendita_per_marca:Q',
            color= alt.Color(
                'Make:N',
                scale=alt.Scale(range=['#A40E4C','#F49D6E','#F5D6BA'])
            )
        )
        .properties(
            width=500
        )
    )

    return(chart)

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

    data_agg = (
        data
        .group_by('Make', 'Model')
        .agg(
            Vendita_per_modello = pl.col('Model').count()
        )
        .filter(pl.col('Make').is_in(make))
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
            alt.Color('Model:N').legend(None)
        )
    )

    text_pie = (
        alt.Chart(data_agg)
        .mark_text(
            radius = 150,
            size = 15,
            color='cyan'
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
            color='cyan'
        )
        .encode(
            alt.Text("Make:N")
        )
    )

    chart = (
        base_pie+text_pie+text_total
    ).properties(
        height = 30,
        width = 30
    ).facet(
        'Make', columns=3
    )

    '''
    Devo togliere dalla legenda i modelli che hanno poche vendite, altrimenti si sovrappongono, capire come fare
    '''

    return(chart)

'''
Funzione che va a generare la pagina di dashboard
'''
def dashboard_main():

    data = read_data()
   
    st.title(':orange[DASHBOARD]')
    st.divider()
    
    #PRIMO CONTAINER
    st.subheader('Vendita annuale auto BEV/PHEV')
    c1 = st.container(border=False)
    col1c1, col2c1 = c1.columns(2)

    col1c1.altair_chart(year_pop_chart(data), use_container_width=True)
    col2c1.markdown(text_year_pop_chart(data.height))

    #SECONDO CONTAINER
    c2 = st.container(border=False)
    c2.subheader('Analisi per marca')

    col1c2, col2c2 = c2.columns(2)
    col2c2.dataframe(make_pop_data(data))
    col1c2.markdown(text_make_pop_data())

    #TERZO CONTAINER

    c3 = st.container(border=False)
    st.session_state.make_selection = c3.multiselect('Scegli al massimo 3 marchi',make_list(data), max_selections=3, default=['TESLA'])

    c3.altair_chart(make_per_year(data, st.session_state.make_selection))

    #QUARTO CONTAINER
    c4 = st.container(border=False)
    c4.altair_chart(model_per_make(data, st.session_state.make_selection), use_container_width=True)

    
if __name__ == '__main__':
    dashboard_main()
    