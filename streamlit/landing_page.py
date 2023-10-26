import streamlit as st
import os
import json
import pandas as pd
import datetime
from streamlit_echarts import st_echarts


@st.cache_data
def get_names():
    return pd.read_csv('./data_sources/raw_data/scse_profiles.csv')['full_name']

@st.cache_data
def get_profile(name):
    if name is not None:
        with open(f'./data_sources/processed_data/{name.lower().replace(" ", "_")}.json', 'r') as f:
            profile = json.load(f)
        return profile
    return None

st.set_page_config(
    page_title="Profile",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Profile View")

name_selected = st.selectbox(
    label='Professors', 
    options=get_names(), 
    index=None
)

profile = get_profile(name_selected)

# st.write(profile)



row0_photo, row0_info = st.columns(
    (2,5)
)

row0_photo.image(f"./data_sources/{profile['image_path'][2:]}")

row0_info.write(f"""{profile['full_name']}  \n  {profile['designation']}  \n {profile['email']}""")
row0_info.link_button('Google Scholar', url=profile['google_scholar'])
if profile['orcid']!=None:
    row0_info.link_button('ORCID', url=profile['orcid'])
row0_info.write(f"Interests: {profile['interests']}")

# row0_info.write(f"Grants: {profile['grants']}")


row1= st.columns(2)

total_publications = sum(profile['published_by_year'].values())
total_citations = sum(profile['citations_by_year']['# of Citations'])

row1[0].metric(
    label='\# of Publications', 
    value=sum(profile['published_by_year'].values()),
    delta=f"{profile['published_by_year'][str(datetime.datetime.now().year)]} YTD"
)

row1[1].metric(
    label='\# of Citations', 
    value=total_citations,
    delta=f"{profile['citations_by_year']['# of Citations'][profile['citations_by_year']['Year'].index(datetime.datetime.now().year)]} YTD"
)


row2 = st.columns(4)

row2[0].metric(
    label='All Time h-index', 
    value=profile['all_time_h_index']
)

row2[1].metric(
    label='All Time i10-index', 
    value=profile['all_time_i10_index']
)

row2[2].metric(
    label='Avg Citation per publication', 
    value=round(total_citations / total_publications, 2),
    help='\# of Citations / # of Publications'
)

row2[3].metric(
    label='Individualised h-index', 
    value='NA',
    help='h-index among all SCSE Faculty'
)


st.subheader('Education Background')
row3 = st.columns(3)

row3[0].write('Bachelors')
row3[0].write('--Not Available--' if profile['bachelor_degree'] is None else profile['bachelor_degree'])

row3[1].write('Masters')
row3[1].write('--Not Available--' if profile['masters'] is None else profile['masters'])

row3[2].write('PhD')
row3[2].write('--Not Available--' if profile['phd'] is None else profile['phd'])


num_published = pd.DataFrame({'Year': profile['published_by_year'].keys(), '# of Publications':profile['published_by_year'].values()})
st.subheader('# of Publications')
st.bar_chart(data=num_published, x='Year', y='# of Publications')


num_citations = pd.DataFrame(profile['citations_by_year'])
st.subheader('# of Citations')
st.bar_chart(data=num_citations, x='Year', y='# of Citations')

#TODO: change processing format
st.subheader('h-index by Year')
years_citations = list(profile['h_index_by_year'].keys())
num_citations = [profile['h_index_by_year'][x] for x in years_citations]
num_citations = pd.DataFrame({'Year': years_citations, 'h-index':num_citations})
st.bar_chart(data=num_citations, x='Year', y='h-index')

#TODO: Change processing format
st.subheader('h-index by Publication Year')
years_citations = list(profile['h_index_by_publication_year'].keys())
num_citations = [profile['h_index_by_publication_year'][x] for x in years_citations]
num_citations = pd.DataFrame({'Publication Year': years_citations, 'h-index':num_citations})
st.bar_chart(data=num_citations, x='Publication Year', y='h-index')


h_index = profile['h_index_by_years_from_publication_year']
sorted_index = sorted(range(len(h_index['Publication Year'])), key=lambda index: h_index['Publication Year'][index])
publication_year = [h_index['Publication Year'][i] for i in sorted_index]
data__ = [h_index['h-index'][i] for i in sorted_index]

st.subheader('h-index by Year grouped by Publication Year')

@st.cache_data
def generate_graph_options(start, end):
    start_index, end_index = publication_year.index(start), publication_year.index(end)
    options = {
        "tooltip": {"trigger": "axis"},
        "legend": {
            "data": publication_year[start_index: end_index+1],
            "selectedMode": False
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "5%", "containLabel": True},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": h_index['Year'],
            "name": "Year",
            "nameLocation": "middle",
            "nameTextStyle":{
                "padding": [10,0,0,0],
                "fontSize": 13,
                "color": "rgb(250, 250, 250)"
            }
        },
        # TODO: Change style
        "yAxis": {
            "type": "value", 
            "name": 'h-index',
            "nameLocation": "middle",
            "nameTextStyle":{
                "padding": [0,0,10,0],
                "fontSize": 13,
                "color": "rgb(250, 250, 250)"
            },
            "splitLine": {
                "lineStyle": {
                    "color": "rgb(250,250,250)"
                }
            }
        },
        "series": [
            {
                "name": publication_year,
                "type": "line",
                # "stack": "总量",
                "data": data
            }
            for publication_year, data in zip(publication_year[start_index: end_index+1], data__[start_index: end_index+1])
        ]
    }
    return options


values = st.slider(
    'Select the range of h-index to view',
    min_value=publication_year[0], 
    max_value=publication_year[-1], 
    value=(publication_year[-5], publication_year[-1]),
    step=1
)

options = generate_graph_options(values[0], values[1])
st_echarts(options=options, height="400px")





st.subheader('Collaboration Network')

st.subheader('Research Focus')

st.subheader('Publication Position')
st.write('First Author, Last Author, Co-Author, Single Author')







