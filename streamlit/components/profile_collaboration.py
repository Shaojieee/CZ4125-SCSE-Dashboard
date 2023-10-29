import streamlit as st
import pandas as pd
from streamlit_d3graph import d3graph
from d3graph import vec2adjmat
import numpy as np


def generate_collaboration(tab, profile):
    co_authors = list(profile['co_authors'].keys())
    co_authors_df = pd.DataFrame({
        'Authors': co_authors, 
        '# of Collaborations': [profile['co_authors'][name]['# of Collaborations'] for name in co_authors],
        'Google Scholar': [profile['co_authors'][name]['google_scholar'] for name in co_authors],
        'Type': [profile['co_authors'][name]['type'] for name in co_authors],
        'Location': [profile['co_authors'][name]['location'] for name in co_authors],
    })

    @st.cache_data
    def build_graph(type, filter_by_location, name):
        temp_df = pd.DataFrame(co_authors_df)
        if len(filter_by_location)>0:
            temp_df = temp_df[temp_df['Location'].isin(filter_by_location)]

        if type=='Organisation':
            grouped = temp_df.groupby(by=['Location']).agg(
                num_authors=('Authors', lambda x: len(np.unique(x))),
                num_collaborations=('# of Collaborations', np.sum)
            ).reset_index()
            temp_df = grouped
            source = [profile['full_name']]*len(temp_df)
            target = temp_df['Location'].to_list()
            weight = temp_df['num_collaborations'].to_list()
            adjmat = vec2adjmat(source, target, weight=weight)
        elif type=='Individual':
            source = [profile['full_name']]*len(temp_df)
            target = temp_df['Authors'].to_list()
            weight = temp_df['# of Collaborations'].to_list()
            adjmat = vec2adjmat(source, target, weight=weight)
        
        return adjmat

    with tab:
        granularity = st.radio(
            label='Granularity',
            options=['Organisation', 'Individual'],
            index=0,
            horizontal=True
        )

        filter_by_location = st.multiselect(
            label='Filter by Organisations',
            options=sorted(co_authors_df['Location'].unique()),
            default=None,
        )

        graph = build_graph(
            type=granularity,
            filter_by_location=filter_by_location,
            name=profile['full_name']
        )
        tooltip = graph.columns.astype(str) +'\nTotal Publications: ' + graph.loc[profile['full_name']].astype(str)

        tooltip = tooltip.values
        label = graph.index.values

        d3 = d3graph(charge=1000)
        d3.graph(graph)
        d3.set_node_properties(label=label, tooltip=tooltip, color=label, size='degree')
        # Initialize
        d3.show(
            show_slider=False,
            figsize=(700,500)
        )

    tab.subheader('# of Collaborations by Year')
    collaboration_by_year = profile['collaboration_by_year']


    years  = sorted(list(collaboration_by_year.keys()))
    collaboration_by_year = pd.DataFrame({
        'Year': years,
        'External': [collaboration_by_year[year]['External'] for year in years],
        'NTU': [collaboration_by_year[year]['NTU'] for year in years],
        'Unknown': [collaboration_by_year[year]['Unknown'] for year in years],
    })

    tab.bar_chart(collaboration_by_year, x='Year', y=['External', 'NTU', 'Unknown'])