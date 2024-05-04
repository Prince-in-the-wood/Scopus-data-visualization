import utils
import streamlit as st
import pandas as pd
import altair as alt

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
    st.markdown("## Section 2: Region analyze")
    
    writer_in_affiliation(df)
    
continent_colors = {
    'Africa': '#a06af1',
    'Asia': '#6d70f1',
    'Europe': '#d46046',
    'North America': '#6dc99a',
    'Oceania': '#eaa568',
    'South America': '#77d0ef',
    'Cannot Resolve': '#e47092'
}

def condition(df):
    return (df['full_name'].isin(selected_writer)) & \
           (df['publisher'].isin(selected_publisher)) & \
           (df['publication_name'].isin(selected_publication)) & \
           (pd.to_datetime(start_date) <= df['coverDate']) & \
           (df['coverDate'] <= pd.to_datetime(end_date))

def writer_in_affiliation(df):

    st.markdown("### 📌: The number of papers of each affiliation's region")

    df2 = df[condition(df) & (~pd.isna(df['affiliation']))].explode('affiliation')

    if( len(df2) == 0 ):
        st.write("No region data to show")
        return 
    
    split_data = df2['affiliation'].apply(utils.split_affiliation_col).apply(pd.Series)
    split_data.columns = ['affilname', 'affiliation-city', 'affiliation-country']
    df2[['affilname', 'affiliation-city', 'affiliation-country']] = split_data
    
    df2['region'] = df2['affiliation-country'].apply(utils.get_continent)

    coord_df = utils.get_coord_df()
    df2 = pd.merge(df2, coord_df[["affiliation-city", "affiliation-country","latitude", "longitude"]], on=["affiliation-city", "affiliation-country"], how='left')
    
    # count by country
    data = df2.groupby(['affiliation-country', 'region'])['id'].nunique().reset_index() \
        .rename(columns={'id': 'count'}).sort_values(by='count', ascending=False)
    
    # count by region
    data2 = data.groupby(['region'])['count'].sum().reset_index() \
            .rename(columns={'id': 'count'}).sort_values(by='count', ascending=False)
    data2['color'] = data2['region'].apply(lambda x: continent_colors[x])
    
    regions = sorted(df2['region'].unique())

    # count in each city
    data3 = df2[["latitude", "longitude", 'id', 'region']]
    data3['color'] = data3['region'].apply(lambda x: continent_colors[x])

    data4 = df2.groupby(["latitude", "longitude"])['id'].nunique().reset_index() \
            .rename(columns={'id': 'count'}).sort_values(by='count', ascending=False)
    
    st.markdown("#### 🗺️: All country")
    st.markdown("##### Pie chart")
    with st.expander("Click to see the graph"):
        utils.draw_pie_chart(data=data2, category='region', value='count', color='color')

    st.markdown("##### Bar chart")
    with st.expander("Click to see the graph"):
        color = alt.Color('region', scale=alt.Scale(domain=list(continent_colors.keys()), range=list(continent_colors.values())))
        utils.draw_altair_bar(data=data,x='affiliation-country', y='count', color=color)

    st.markdown("##### Scatter map")
    with st.expander("Click to see the graph"):
        utils.draw_scatter_map(data3)

    st.markdown("##### Heat map")
    with st.expander("Click to see the graph"):
        utils.draw_heat_map(data4, "count")

    st.markdown("---")

    st.markdown("#### 🗺️: For each regions")
    utils.draw_table(data=data2[['region','count']])

    for region in regions:
        with st.expander(region):
            if region == "Cannot Resolve":
                continue
                
            utils.draw_altair_bar(data=data[data['region']==region], x='affiliation-country', y='count')
        
    with st.expander("Cannot resolve region"):
        utils.draw_altair_bar(data=data[data['region'] == "Cannot Resolve"], x='affiliation-country', y='count')
