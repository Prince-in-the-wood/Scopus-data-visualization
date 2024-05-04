import pandas as pd
import numpy as np

import pycountry
import pycountry_convert as pc

import pydeck as pdk
import streamlit as st
import altair as alt
import plotly.express as px

start_date, end_date = (None, None)
selected_writer, selected_publisher, selected_publication = ([], [], [])
full_name = []

def get_selected_list():
    return start_date, end_date, selected_writer, selected_publisher, selected_publication, full_name

def set_start_date(startDate):
    global start_date
    start_date = startDate

def set_end_date(endDate):
    global end_date
    end_date = endDate

def set_full_name(fullName, full_name_list):
    global full_name
    full_name = fullName
    global selected_writer
    selected_writer = fullName if len(fullName) > 0 else full_name_list

def set_publisher(publisher, publisher_list):
    global selected_publisher
    selected_publisher = publisher if len(publisher) > 0 else publisher_list

def set_publication_name(publication_name, publication_name_list):
    global selected_publication
    selected_publication = publication_name if len(publication_name) > 0 else publication_name_list

coord_df = pd.read_csv("src/data/all_city_country/coordinates/coordinates.csv")
coord_df = coord_df.rename(columns={
                "original_affiliation-city": "affiliation-city",
                "original_affiliation-country": "affiliation-country",
                "lat":"latitude",
                "lon": "longitude"
            })

def get_coord_df():
    return coord_df

def get_continent(country_name):
    try:
        country_alpha_2 = pycountry.countries.lookup(country_name).alpha_2
        continent_code = pc.country_alpha2_to_continent_code(country_alpha_2)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        return continent_name
    except LookupError:
        return "Cannot Resolve"

def split_affiliation_col(x):
    if pd.isna(x):
        return np.nan, np.nan, np.nan
    else:
        return x['affilname'], x['affiliation-city'], x['affiliation-country']


# Draw graph
def draw_bar_chart(data, x, y):
    if( data.size > 0 ):
        st.bar_chart(data=data, x=x, y=y)
    else:
        st.write(
            """No data to display"""
        )

def draw_table(data):
    if( data.size > 0 ):
        st.table(data)

def draw_altair_bar(data, x, y, color=alt.value('steelblue')):
    if( data.size > 0 ):
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X(x, sort=None),
            y=y,
            color=color
        ).properties(width='container', height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write(
            """No data to display"""
        )

def draw_pie_chart(data, category, value, color=None):
    if( data.size > 0 ):
        if color == None:
            fig = px.pie(data, values=value, names=category)
        else:
            fig = px.pie(data, values=value, names=category, color=color)
        st.plotly_chart(fig, theme=None)
    else:
        st.write(
            """No data to display"""
        )

def draw_scatter_map(df):
    layer = pdk.Layer(
                "ScatterplotLayer",
                df,
                get_position=["longitude", "latitude"],
                get_fill_color=[255, 140, 0],
                get_radius=500,
                pickable=True
            )

    view_state = pdk.ViewState(
                    longitude=df['longitude'].mean(),
                    latitude=df['latitude'].mean(),
                    zoom=0
                )
    smap = pdk.Deck(layers=[layer], initial_view_state=view_state)
    st.pydeck_chart(smap)

def draw_heat_map(df, weight):
    layer = pdk.Layer(
                "HeatmapLayer",
                df,
                get_position=["longitude", "latitude"],
                get_weight=weight,
                opacity=0.6
            )

    view_state = pdk.ViewState(
                    longitude=df['longitude'].mean(),
                    latitude=df['latitude'].mean(),
                    zoom=0
                )
    smap = pdk.Deck(layers=[layer], initial_view_state=view_state)
    st.pydeck_chart(smap)