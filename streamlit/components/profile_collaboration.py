import streamlit as st
import pandas as pd
from streamlit_d3graph import d3graph
from d3graph import vec2adjmat
import numpy as np
import datetime
import altair as alt
from streamlit_extras.card import card

def generate_collaboration(tab, profile):
    
    co_authors_df = pd.DataFrame(profile['collaboration_network'])

    if len(co_authors_df)==0:
        tab.write('No co-authors found in Google Scholar')
        return
    

    co_authors_df = co_authors_df.groupby(by=['target_id', 'target']).agg(
        type=('type', max),
        location=('location', max),
        num_collaborations=('location', len)
    ).reset_index()

    @st.cache_data
    def build_graph(type, filter_by_location, name):
        temp_df = pd.DataFrame(co_authors_df)
        if len(filter_by_location)>0:
            temp_df = temp_df[temp_df['location'].isin(filter_by_location)]

        if type=='Organisation':
            grouped = temp_df.groupby(by=['location']).agg(
                num_authors=('target_id', lambda x: len(np.unique(x))),
                num_collaborations=('num_collaborations', np.sum)
            ).reset_index()
            temp_df = grouped
            source = [profile['full_name']]*len(temp_df)
            target = temp_df['location'].to_list()
            weight = temp_df['num_collaborations'].to_list()
            adjmat = vec2adjmat(source, target, weight=weight)
        elif type=='Individual':
            source = [profile['full_name']]*len(temp_df)
            target = temp_df['target'].to_list()
            weight = temp_df['num_collaborations'].to_list()
            adjmat = vec2adjmat(source, target, weight=weight)
        
        return adjmat

    granularity = tab.radio(
        label='Granularity',
        options=['Organisation', 'Individual'],
        index=0,
        horizontal=True
    )

    filter_by_location = tab.multiselect(
        label='Filter by Organisation',
        options=sorted(co_authors_df['location'].unique()),
        default=None,
    )

    with tab:
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
        d3.show(
            show_slider=False,
            figsize=(700,500)
        )

    co_authors_df = pd.DataFrame(profile['collaboration_network'])
    groupby_col = 'type'
    if len(filter_by_location)>0:
        groupby_col = 'location'
        co_authors_df = co_authors_df[co_authors_df['location'].isin(filter_by_location)]
    co_authors_df['source'] = profile['full_name']

    co_authors_df['type'] = co_authors_df['type'].replace('Outside SCSE', 'NTU')
    co_authors_df['type'] = co_authors_df['type'].replace('Outside NTU', 'External')
    collaboration_by_year = co_authors_df.groupby(by=['year',groupby_col])['target'].count().reset_index()
    years = set(collaboration_by_year['year'].to_list())
    has_unknown = []
    if 'unknown' in years:
        years.remove('unknown')
        has_unknown = ['unknown']

    year_df = pd.DataFrame({'year':[x for x in range(min(years), datetime.datetime.now().year+1)]+has_unknown})
    collaboration_by_year = year_df.merge(collaboration_by_year, how='left', on='year')
    collaboration_by_year['target'] = collaboration_by_year['target'].fillna(0)
    collaboration_by_year[groupby_col] = collaboration_by_year[groupby_col].fillna(collaboration_by_year[groupby_col].unique()[0])

    chart = alt.Chart(collaboration_by_year).mark_bar().encode(
        alt.X('year:N', sort='ascending').title('Year'),
        alt.Y('sum(target)').title('# of Collaborators'),
        color=alt.Color(
            'type' if len(filter_by_location)==0 else 'location',
            title='Collaboration Type',
            legend=alt.Legend(
                orient='bottom',
                direction='horizontal'
            )
        )
    )

    tab.altair_chart(chart, use_container_width=True, theme='streamlit')


    for location in filter_by_location:
        section = tab.expander(label=location)
        location_df = co_authors_df[co_authors_df['location']==location]
        with section:
            entries = []
            newline = '\n'
            # location_df = location_df.sort_values(by=['year'], ascending=False)
            for i, row in location_df.iterrows():
                entry = f"1. [{row['title']}]({row['link']}) - {row['year']}"

                entries.append(entry)
            st.markdown(newline.join(entries))
