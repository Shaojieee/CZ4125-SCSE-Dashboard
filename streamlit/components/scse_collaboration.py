import streamlit as st
import altair as alt
import pandas as pd
import datetime
from streamlit_d3graph import d3graph
from d3graph import vec2adjmat

def generate_collaboration(tab, profile):
    with tab:
        network_df = pd.DataFrame(profile['Collaboration Network'])
        st.subheader('Collaboration Network within SCSE')

        @st.cache_data
        def build_within_scse_graph():
            temp_df = pd.DataFrame(network_df)
            temp_df = temp_df[temp_df['type'].isin(['NTU'])]
            grouped = temp_df.groupby(by=['source','target']).agg(
                num_collaborations=('type', len)
            ).reset_index()
            source = grouped['source'].to_list()
            target = grouped['target'].to_list()
            weight = grouped['num_collaborations'].to_list()
            adjmat = vec2adjmat(source, target, weight=weight)
            
            return adjmat

        graph = build_within_scse_graph()
        label = graph.index.values
        d3 = d3graph(charge=750)
        d3.graph(graph)
        d3.set_node_properties(label=label, color=label, size='degree')
        # Initialize
        d3.show(
            show_slider=False,
            figsize=(700,500)
        )

        st.subheader('External Collaboration Network')
        filtered_df = pd.DataFrame(network_df[network_df['location']!='Nanyang Technological University'])
        locations = sorted(filtered_df['location'].unique())
        filter_by_location = st.multiselect(
            label='Filter Organisations',
            options=locations
        )

        if len(filter_by_location)>0:
            filtered_df = network_df[network_df['location'].isin(filter_by_location)]

        st.dataframe(
            filtered_df[filtered_df['location']!='Nanyang Technological University'].groupby(by=['location'])['source'].count().reset_index(),
            use_container_width=True,
            hide_index=True,
            height=200,
            column_config={
                'location': 'Collaborator',
                'source': '# of Collaborations',
            }
        )
        # Filter and aggregating to colloborators
        if len(filter_by_location)>0:
            collaboration_by_year = filtered_df.groupby(by=['year','location'])['target'].count().reset_index()
            years = set(collaboration_by_year['year'].to_list())
            has_unknown = []
            if 'Unknown' in years:
                years.remove('Unknown')
                has_unknown = ['Unknown']
            year_df = pd.DataFrame({'year':[x for x in range(min(years), datetime.datetime.now().year+1)]+has_unknown})
            collaboration_by_year = year_df.merge(collaboration_by_year, how='left', on='year')
            collaboration_by_year['target'] = collaboration_by_year['target'].fillna(0)
            collaboration_by_year['location'] = collaboration_by_year['location'].fillna(collaboration_by_year[collaboration_by_year['location'].notna()]['location'].iloc[0])
        else:
            collaboration_by_year = filtered_df.groupby(by=['year','type'])['target'].count().reset_index()
            years = set(collaboration_by_year['year'].to_list())
            has_unknown = []
            if 'Unknown' in years:
                years.remove('Unknown')
                has_unknown = ['Unknown']
            year_df = pd.DataFrame({'year':[x for x in range(int(min(years)), datetime.datetime.now().year+1)]+has_unknown})
            collaboration_by_year = year_df.merge(collaboration_by_year, how='left', on='year')
            collaboration_by_year['target'] = collaboration_by_year['target'].fillna(0)
            collaboration_by_year['type'] = collaboration_by_year['type'].fillna('NTU')
            collaboration_by_year['type'] = collaboration_by_year['type'].replace('Outside SCSE', 'NTU')
            collaboration_by_year['type'] = collaboration_by_year['type'].replace('Outside NTU', 'External')


        chart = alt.Chart(collaboration_by_year).mark_bar().encode(
            alt.X('year:N', sort='ascending').title('Year'),
            alt.Y('sum(target)').title('# of Collaborations'),
            color=alt.Color(
                'type' if len(filter_by_location)==0 else 'location',
                title='Collaboration Type',
                legend=alt.Legend(
                    orient='bottom',
                    direction='horizontal'
                )
            )
        )
        st.altair_chart(chart, use_container_width=True, theme='streamlit')


        def build_external_graph(filter_by_location=[]):
            temp_df = pd.DataFrame(filtered_df)
            grouped = temp_df.groupby(by=['source','location']).agg(
                num_collaborations=('target', len)
            ).reset_index()
            source = grouped['source'].to_list()
            target = grouped['location'].to_list()
            weight = grouped['num_collaborations'].to_list()
            adjmat = vec2adjmat(source, target, weight=weight)
            
            return adjmat

        graph = build_external_graph()
        label = graph.index.values
        d3 = d3graph(charge=750)
        d3.graph(graph)
        d3.set_node_properties(label=label, color=label, size='degree')
        # Initialize
        d3.show(
            show_slider=False,
            figsize=(700,500)
        )

        