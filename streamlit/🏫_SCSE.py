import streamlit as st
import json
import pandas as pd
import datetime
from streamlit_d3graph import d3graph
from d3graph import vec2adjmat
import numpy as np
import altair as alt
import streamlit.components.v1 as components

from components.scse_research import generate_research
from components.scse_collaboration import generate_collaboration
from components.scse_statistics import generate_statistic





def get_profile():
    with open(f'./data_sources/scse/profile.json', 'r') as f:
        profile = json.load(f)
    return profile

st.set_page_config(
    page_title="SCSE",
    page_icon="👋",
    # layout='wide'
)




st.title('Nanyang Technological University') 
st.subheader('School of Computer Science and Engineering')

profile = get_profile()
df = pd.DataFrame(profile['by_year'])
network_df = pd.DataFrame(profile['Collaboration Network'])

row1 = st.columns(3)

row1[0].metric(
    label='\# of Faculties', 
    value=profile['# of Faculty']
)

row1[1].metric(
    label='\# of Publications', 
    value=sum(df['# of Publications']),
    delta=str(df.loc[df['Year']==datetime.datetime.now().year, '# of Publications'].values[0]) +' YTD'
)

row1[2].metric(
    label='\# of Citations', 
    value=sum(df['# of Citations']),
    delta=str(df.loc[df['Year']==datetime.datetime.now().year, '# of Citations'].values[0]) + ' YTD'
)

row2 = st.columns(3)

row2[0].metric(
    label='\# of External Collaborators',
    value=network_df['location'].nunique(),
    help='\# of Organisations that has published with NTU'
)

avg_external_collaborators = network_df[network_df['location']!='Nanyang Technological University'].groupby(by=['source'])['location'].nunique().mean()

row2[1].metric(
    label='Avg External Collaborator per Faculty',
    value=avg_external_collaborators,
)

row2[2].metric(
    label='\# of External Collaborations',
    value=network_df[network_df['location']!='Nanyang Technological University']['target'].count(),
    help='\# of Publications with External Organisations'
)

list_tabs = ['Collaboration', 'Research Impact', 'Research Focus']
whitespace = 1
tab1, tab2, tab3 = st.tabs(list_tabs)
css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.5rem;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)

generate_collaboration(tab1, profile)

generate_statistic(tab2, profile)

generate_research(tab3, profile)


