import streamlit as st
import polars as pl
import altair as alt


@st.cache_data
def read_data():
    data = pl.read_csv('DATA/data.csv')
    return data

'''
PRIMA RIGA DI GRAFICI
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
    #st.altair_chart(chart)
    return(chart)

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
SECONDA RIGA DI GRAFICI
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
TERZA RIGA DI GRAFICI
'''

def make_list(data):
    return data['Make'].unique().sort().to_list()

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

def model_per_maker(data, make):
    # Prepara i dati aggregati per marca e modello
    data_agg = (
        data
        .group_by('Make', 'Model')
        .agg(
            Vendita_per_modello = pl.col('Model').count()
        )
        .filter(pl.col('Make').is_in(make))
    )

    # Crea il grafico
    chart = alt.Chart(data_agg).mark_arc().encode(
        theta=alt.Theta('Vendita_per_modello:Q'),  # Quantitativo per il calcolo delle dimensioni
        color=alt.Color('Model:N'),  # Colore per ogni modello
        tooltip=['Model', 'Vendita_per_modello']
    ).properties(
        width=200,
        height=200
    ).facet(
        facet='Make:N',  # Crea una torta per ogni marca
        columns=3  # Disponi 3 colonne
    )

    return chart



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

    c4.altair_chart(model_per_maker(data, st.session_state.make_selection))

    
if __name__ == '__main__':
    dashboard_main()
    