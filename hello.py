import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import re
import kagglehub

# Download latest version
path = kagglehub.dataset_download("ratikkakkar/electric-vehicle-population-data")

print("Path to dataset files:", path)

import polars as pl
data = pl.read_csv(path+'/Electric_Vehicle_Population_Data.csv')

data = data.select(pl.exclude(['VIN (1-10)','Postal Code','Base MSRP','Legislative District','DOL Vehicle ID','Electric Utility','2020 Census Tract']))

data = data.select(pl.exclude('Clean Alternative Fuel Vehicle (CAFV) Eligibility'))

coord_list = []

data = (
    data
    .filter(pl.col('Make') == 'TESLA')
    .select(pl.col('Vehicle Location'))
)

for row in data.rows():
    if row[0] is not None:
        numb = re.findall(r'\d+\.\d+|\d+', row[0])
        coord = (float(numb[0]), float(numb[1]))
        coord_list.append(coord)

coord_chart = pd.DataFrame(coord_list, columns=['lat', 'lon'])

st.write(coord_chart)

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=122,
            longitude=47,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=coord_chart,
                get_position="[lon, lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
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