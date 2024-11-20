import polars as pl
import streamlit as st
import altair as alt



if __name__ == "__main__":
    st.title('Prima prova libreria ALTAIR')
    data_url = "https://www.dei.unipd.it/~ceccarello/data/gapminder.csv"
    
    gapminder = pl.read_csv(data_url).filter(pl.col('year')==2007)
    #st.write(gapminder)

    chart = (
        alt.Chart(gapminder).mark_circle()
        .encode(
            alt.X('gdpPercap').scale(type='log'),
            alt.Y('lifeExp'),
            alt.Color('continent'),
            alt.Size('pop')
        )
    )

    bar_chart = (
        alt.Chart(gapminder)
        .mark_bar()
        .encode(
            alt.X('pop', aggregate='sum'),
            alt.Y('continent', sort='-x')
        )
    )


    st.altair_chart(
        bar_chart,
        use_container_width=True
    )