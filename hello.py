import polars as pl
import streamlit as st
import altair as alt



if __name__ == "__main__":
    st.write('Hello')
    data_url = "https://www.dei.unipd.it/~ceccarello/data/gapminder.csv"
    
    gapminder = pl.read_csv(data_url).filter(pl.col('year')==2007)
