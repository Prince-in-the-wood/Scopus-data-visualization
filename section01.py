# Import library
import numpy as np
import pandas as pd
import streamlit as st
import utils

start_date, end_date = (None, None)
selected_writer, selected_publisher, selected_publication = (None, None, None)
full_name = None

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

def section(df):
    st.markdown("## Section 1: Reports analyze")
    report_in_day(df)
    st.markdown("---")
    cited_by_reports_count(df)
    st.markdown("---")
    report_each_publisher(df)
    st.markdown("---")
    report_each_publication(df)
    st.markdown("---")
    report_type(df)

def condition(df):
    return (df['full_name'].isin(selected_writer)) & \
           (df['publisher'].isin(selected_publisher)) & \
           (df['publication_name'].isin(selected_publication)) & \
           (pd.to_datetime(start_date) <= df['coverDate']) & \
           (df['coverDate'] <= pd.to_datetime(end_date))

# Count by date
def report_in_day(df):
    st.markdown("### 📌: The number of report in each day")

    data = df[condition(df)] \
            .groupby('coverDate')['id'].count().reset_index()
    with st.expander("Click to see the graph"):
        utils.draw_bar_chart(data=data, x='coverDate', y='id')

def cited_by_reports_count(df):
    st.markdown("### 📌: The number of cited-by in reports")

    data = df[condition(df)] \
            .groupby('cited_by_cnt')['id'].count().reset_index().rename(columns={"id": "count"})
    with st.expander("Click to see the graph"):
        utils.draw_bar_chart(data=data, x='cited_by_cnt', y='count')
        utils.draw_table(data[0:min(5, len(data))])

def report_each_publisher(df):
    st.markdown("### 📌: The number of report of each publisher")

    data = df[condition(df)] \
            .groupby('publisher')['id'].count().reset_index().rename(columns={'id': 'count'}).sort_values(by='count', ascending=False)
    with st.expander("Click to see the graph"):
        utils.draw_altair_bar(data=data, x='publisher', y='count')
        utils.draw_table(data[0:min(5, len(data))])

# Show number of report of each publication name
def report_each_publication(df):
    st.markdown("### 📌: The number of report of each publication name")
    st.write("i.e. which book or journal in which papers are published")

    data = df[condition(df)] \
            .groupby('publication_name')['id'].count().reset_index() \
            .rename(columns={'id': 'count'}).sort_values(by='count', ascending=False)
    with st.expander("Click to see the graph"):
        utils.draw_altair_bar(data=data,x='publication_name', y='count')
        utils.draw_table(data[0:min(5, len(data))])

def report_type(df):
    st.markdown("### 📌: The ratio of report in each publication type")
    st.write("Publication type: Conference Proceeding, book, journal, etc.")

    st.markdown("#### Overview")
    data = df[condition(df)].groupby(['aggregation_type'])['id'].count().reset_index() \
           .rename(columns={"id":"count"}).sort_values(by='count', ascending=False)
    rtype = data["aggregation_type"].unique()

    with st.expander("Click to see the graph"):
        utils.draw_pie_chart(data=data, category="aggregation_type", value="count")
        utils.draw_table(data)

    st.markdown("#### Each type")

    for t in rtype:
        with st.expander(t):
            data = df[condition(df) & (df["aggregation_type"] == t)].groupby(['subtype'])['id'].count() \
                    .reset_index().rename(columns={"id":"count"}).sort_values(by='count', ascending=False)
            utils.draw_altair_bar(data=data,x='subtype', y='count')
            utils.draw_table(data)
        
    
