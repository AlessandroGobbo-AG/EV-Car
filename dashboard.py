import streamlit as st
import polars as pl
import altair as alt

def read_data():
    data = pl.read_csv('DATA/data.csv')
    return data

def year_pop_chart(data):
    data_chart = (
        data
        .group_by('Model Year')
        .agg(
            tot_per_year = pl.col('Model Year').sum()
        )
        .sort(pl.col('Model Year'), descending=False)
    )
    
    chart = (
        alt.Chart(data_chart)
        .mark_bar() 
        .encode(
            y='tot_per_year',
            x= 'Model Year'
        )
    )
    st.altair_chart(chart)

def dashboard_main():
    data = read_data()
   
    st.title('DASHBOARD')
    st.divider()
    
    st.header('Vendite auto ibride/elettriche stato Washington')
    year_pop_chart(data)

if __name__ == '__main__':
    dashboard_main()