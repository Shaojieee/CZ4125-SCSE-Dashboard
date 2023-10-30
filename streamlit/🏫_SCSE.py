import streamlit as st
import json
import pandas as pd
import datetime
from streamlit_d3graph import d3graph
from d3graph import vec2adjmat
import numpy as np


def get_profile():
    with open(f'./data_sources/scse/profile.json', 'r') as f:
        profile = json.load(f)
    return profile

st.set_page_config(
    page_title="SCSE",
    page_icon="👋",
)

st.title('Nanyang Technological University') 
st.subheader('School of Computer Science and Engineering')

profile = get_profile()
df = pd.DataFrame(profile['by_year'])

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

st.subheader('\# of Publications')
st.bar_chart(data=df, x='Year', y='# of Publications')

st.subheader('\# of Citations')
st.bar_chart(data=df, x='Year', y='# of Citations')


st.subheader('Faculty Statistics')
top_faculty_df = pd.DataFrame(profile['Top Faculty'])
top_faculty_df['Avg Citations per Publication'] = top_faculty_df['Avg Citations per Publication'].round(2)
top_faculty_df = top_faculty_df.sort_values(by=['# of Publications', '# of Citations', 'Avg Citations per Publication', 'h-index'], ascending=False)


st.dataframe(
    data=top_faculty_df,
    use_container_width=True,
    hide_index=True
)

st.subheader('Collaboration Network within NTU')

network_df = pd.DataFrame(profile['Collaboration Network'])

def build_graph(type, filter_by_location):
    temp_df = pd.DataFrame(network_df)
    temp_df = temp_df[temp_df['type']=='NTU']
    
    if len(filter_by_location)>0:
        temp_df = temp_df[temp_df['location'].isin(filter_by_location)]

    if type=='Organisation':
        grouped = temp_df.groupby(by=['type']).agg(
            num_authors=('target', lambda x: len(np.unique(x))),
            num_collaborations=('# of Collaboration', np.sum)
        ).reset_index()
        temp_df = grouped
        source = ['NTU']*len(temp_df)
        target = temp_df['type'].to_list()
        weight = temp_df['num_collaborations'].to_list()
        adjmat = vec2adjmat(source, target, weight=weight)
    if type=='Individual':
        source = temp_df['source'].to_list()
        target = temp_df['target'].to_list()
        weight = temp_df['# of Collaboration'].to_list()
        adjmat = vec2adjmat(source, target, weight=weight)
    
    return adjmat
granularity = st.radio(
    label='Granularity',
    options=['Organisation', 'Individual'],
    index=0,
    horizontal=True
)
graph = build_graph(type=granularity, filter_by_location=[])

d3 = d3graph(charge=500)
d3.graph(graph)
# d3.set_node_properties(label=label, tooltip=tooltip, color=label, size='degree')
# Initialize
d3.show(
    # show_slider=False,
    figsize=(700,500)
)