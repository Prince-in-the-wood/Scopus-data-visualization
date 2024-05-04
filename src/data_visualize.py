# Import library
import section01 
import section02
import section03

import numpy as np
import pandas as pd

import streamlit as st
import ast


# Before Analyze ##################################################################################################
# Load data
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

# Clean data
@st.cache_data
def concat_name(x):
    if pd.isnull(x['given_name']):
        return x['surname']
    return x['given_name'] + " " +  x['surname']

@st.cache_data
def format_data(df):
    # Affiliation
    condition = (df['affiliation'] == "['affilname', 'affiliation-city', 'affiliation-country']") | \
                (df['affiliation'] == "['affiliation-city', '@id', 'affilname', '@href', 'affiliation-country']" )
    df.loc[condition, 'affiliation'] = np.NaN
    condition = pd.notna(df['affiliation'])
    df.loc[condition, 'affiliation'] = df.loc[condition, 'affiliation'].apply(lambda x: ast.literal_eval(x))

    df['coverDate'] = pd.to_datetime(df['coverDate'])
    df['full_name'] = df.apply(concat_name, axis=1)
    return df

@st.cache_data
def load_and_format():
    given_df = load_data('src/data/dataset/scopusToCSV_FromAjarn.csv')
    scraped_df = load_data('src/data/dataset/scopusToCSV.csv')

    given_df = format_data(given_df)
    scraped_df = format_data(scraped_df)
    all_df = pd.concat([given_df, scraped_df])
    return given_df, scraped_df, all_df

(given_df, scraped_df, all_df) = load_and_format()

# Side bar ##################################################################################################
st.sidebar.header('Sidebar Controls')

# section selector
st.sidebar.subheader('🧭: Section selector')
section = st.sidebar.radio(
    "Go to", 
    ["Home", "Section 1: Report analyze", "Section 2: Region analyze", "Section 3: Writers analyze"]
)

# Data selector
st.sidebar.subheader('💾: Data selector')
selected_data = st.sidebar.radio(
    'Select data',
    ['Given data', 'Scraped data', 'All data']
)

if( selected_data == 'Given data' ):
    df = given_df
elif( selected_data == 'Scraped data'):
    df = scraped_df
else:
    df = all_df

# Select parameter
st.sidebar.subheader('🛠️: Parameter selector')

full_name_list = sorted(df['full_name'].unique())
publication_name_list = sorted(df['publication_name'].unique())
publisher_list = sorted(df[df['publisher'].isnull() == 0]['publisher'].unique())

min_date = df['coverDate'].min()
max_date = df['coverDate'].max()
start_date = st.sidebar.date_input('Select start date', format="YYYY-MM-DD", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input('Select end date', format="YYYY-MM-DD", value=max_date, min_value=start_date, max_value=max_date)

full_name = st.sidebar.multiselect(
    'Select writer full name',
    full_name_list
)

publication_name = st.sidebar.multiselect(
    'Select publication name',
    publication_name_list
)

publisher = st.sidebar.multiselect(
    'Select publisher',
    publisher_list
)

# Main area ##################################################################################################
st.title('🚀Final-project: Scopus data report')
st.markdown("---")


if section == "Home":
    st.markdown("## Welcome to Our project")
    st.markdown("### 📖: How to use")
    st.markdown("""
        - Section selector: Navigate you to different main content\n
        - Data selector: Select flavor data you want to display\n
        - Parameter selector: Filter the data\n
            - Only in section 3, writer full name, publication name or publisher is not used for filtering the data\n
            - Noted that if writer full name, publication name or publisher is not selected, all data in the day range will be selected\n
    """)

    st.markdown("### 🤝: Our team member")
    st.markdown("""
        1. 6431313121 Thamon Nantasen\n
        2. 6431314821 Tittaya Worawongtad\n
        3. 6431341721 Waranont Chaosanguan\n
        4. 6432142321 Matikant Vatrasresth\n
    """)
elif section == "Section 1: Report analyze":
    section01.set_start_date(start_date)
    section01.set_end_date(end_date)
    section01.set_full_name(full_name, full_name_list)
    section01.set_publisher(publisher, publisher_list)
    section01.set_publication_name(publication_name, publication_name_list)

    section01.section(df)
elif section == "Section 2: Region analyze":
    section02.set_start_date(start_date)
    section02.set_end_date(end_date)
    section02.set_full_name(full_name, full_name_list)
    section02.set_publisher(publisher, publisher_list)
    section02.set_publication_name(publication_name, publication_name_list)

    section02.section(df)
elif section == "Section 3: Writers analyze":
    section03.set_start_date(start_date)
    section03.set_end_date(end_date)
    section03.set_full_name(full_name, full_name_list)
    section03.section(df)