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

def section(df):
    st.markdown("## Section 3: Writers analyze")
    affiliation_of_writer(df)
    st.markdown("---")
    cited_by_writer(df)
    st.markdown("---")
    papers_of_writer(df)

def affiliation_of_writer(df):
    st.markdown("### 📌: The affiliation of writers")
    st.write("If writers is not selected, all writers will be shown")

    df2 = df[(df['full_name'].isin(selected_writer)) & (~pd.isna(df['affiliation']))].explode('affiliation')

    if( len(df2) == 0 ):
        st.write("No region data to show")
    else:
        split_data = df2['affiliation'].apply(utils.split_affiliation_col).apply(pd.Series)
        split_data.columns = ['affilname', 'affiliation-city', 'affiliation-country']
        df2[['affilname', 'affiliation-city', 'affiliation-country']] = split_data
            
        coord_df = utils.get_coord_df()
        df2 = pd.merge(df2, coord_df[["affiliation-city", "affiliation-country","latitude", "longitude"]], on=["affiliation-city", "affiliation-country"], how='left')
            
        # count by country
        data = df2[["latitude", "longitude", 'full_name']].drop_duplicates()
        
        utils.draw_scatter_map(data)

def cited_by_writer(df):
    st.markdown("### 📌: The number of cited-by of the writers' report")

    data = df[(df['full_name'].isin(selected_writer)) & (pd.to_datetime(start_date) <= df['coverDate']) & (df['coverDate'] <= pd.to_datetime(end_date))] \
            .groupby('full_name')['cited_by_cnt'].sum().reset_index().sort_values('cited_by_cnt', ascending=False)
    data = data[data['cited_by_cnt'] > 0]
    data = pd.concat([data, pd.DataFrame({'full_name': 'others','cited_by_cnt': 0}, index=[0])], ignore_index=True)

    with st.expander("Click to see the graph"):
        utils.draw_altair_bar(data=data, x='full_name', y='cited_by_cnt')
        utils.draw_table(data.loc[0:min(5, len(data))])


def papers_of_writer(df):
    st.markdown("### 📌: The papers written by writer")
    st.write("In range" + str(start_date) + " - " + str(end_date))

    with st.expander("Click to see the list of papers"):
        for idx, name in enumerate(full_name):
            st.subheader(str(idx) + ": " + name)
            data = df[(df['full_name'] == name) & (pd.to_datetime(start_date) <= df['coverDate']) & (df['coverDate'] <= pd.to_datetime(end_date))] \
                    [['id', 'title']].sort_values(by='id')
            utils.draw_table(data)
        
        if( len(full_name) == 0 ):
            st.write("Please select writer to see data")
