import streamlit as st
import os
import json
import pandas as pd
import datetime


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

st.write(profile)


row0_photo, row0_info = st.columns(
    (2,5)
)

row0_photo.title('Photo')

row0_info.write(f"""{profile['full_name']}  \n  {profile['designation']}  \n {profile['email']}""")
row0_info.link_button('Google Scholar', url=profile['google_scholar'])
if profile['orcid']!=None:
    row0_info.link_button('ORCID', url=profile['orcid'])
row0_info.write(f"Interests: {profile['interests']}")

# row0_info.write(f"Grants: {profile['grants']}")


row1= st.columns(2)

row1[0].metric(
    label='\# of Publications', 
    value=sum(profile['num_published'].values()),
    delta=f"{profile['num_published'][str(datetime.datetime.now().year)]} YTD"
)

row1[1].metric(
    label='\# of Citations', 
    value=sum(profile['citation_statistics']['chart'].values()),
    delta=f"{profile['citation_statistics']['chart'][str(datetime.datetime.now().year)]} YTD"
)



row2 = st.columns(4)

row2[0].metric(
    label='All Time h-index', 
    value=profile['citation_statistics']['table']['All'][1]
)

row2[1].metric(
    label='All Time i10-index', 
    value=profile['citation_statistics']['table']['All'][2]
)

row2[2].metric(
    label='Time Weight h-index', 
    value=profile['citation_statistics']['table']['All'][2],
    help='Exponentially Weighted h-index'
)

row2[3].metric(
    label='Individualised h-index', 
    value=profile['citation_statistics']['table']['All'][2],
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


num_published = pd.DataFrame({'Year': profile['num_published'].keys(), '# of Publications':profile['num_published'].values()})
st.subheader('# of Publications')
st.bar_chart(data=num_published, x='Year', y='# of Publications')


years_citations = list(profile['citation_statistics']['chart'].keys())
num_citations = [profile['citation_statistics']['chart'][x] for x in years_citations]
num_citations = pd.DataFrame({'Year': years_citations, '# of Citations':num_citations})
st.subheader('# of Citations')
st.bar_chart(data=num_citations, x='Year', y='# of Citations')

st.subheader('h-index by over time')
years_citations = list(profile['h-index_over_time'].keys())
num_citations = [profile['h-index_over_time'][x] for x in years_citations]
num_citations = pd.DataFrame({'Year': years_citations, 'h-index':num_citations})
st.bar_chart(data=num_citations, x='Year', y='h-index')


st.subheader('h-index by Publication Year')
years_citations = list(profile['h_index_by_publication_year'].keys())
num_citations = [profile['h_index_by_publication_year'][x] for x in years_citations]
num_citations = pd.DataFrame({'Publication Year': years_citations, 'h-index':num_citations})
st.bar_chart(data=num_citations, x='Publication Year', y='h-index')

st.subheader('h-index by years from Publication Year')

st.subheader('Collaboration Network')


st.subheader('Research Focus')

st.subheader('Publication Position')
st.write('First Author, Last Author, Co-Author, Single Author')







