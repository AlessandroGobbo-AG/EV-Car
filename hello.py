import polars as pl
import streamlit as st
import altair as alt



if __name__ == "__main__":
    st.title('Prima prova libreria ALTAIR')
    data_url = "https://www.dei.unipd.it/~ceccarello/data/gapminder.csv"
    
    gapminder = pl.read_csv(data_url).filter(pl.col('year')==2007)
    #st.write(gapminder)

    st.write(gapminder)


    base_pie = (
        alt.Chart(gapminder)
        .mark_arc(
            radius=120
        )
        .transform_aggregate(
            pop = 'sum(pop)',
            groupby=['continent']
        )
        .encode(
            alt.Theta('pop'),
            alt.Color('continent')
        )
    )

    text_pie = (
        base_pie
        .mark_text(
            radius=150,
            size=15
        )
        .transform_calculate(
            label = "round(datum.pop/1000000)+ 'M'"
        )
        .encode(
            alt.Text('label:N'),
            alt.Theta('pop', stack=True),
            alt.Order('continent')
        )
    )

    st.title('Grafico della popolazione per continente')
    st.altair_chart(
        base_pie+text_pie, 
        use_container_width=True
    )
