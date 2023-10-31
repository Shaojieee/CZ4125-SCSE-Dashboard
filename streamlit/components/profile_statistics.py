import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import altair as alt
import datetime


def generate_statistic(tab, profile):
    num_published = pd.DataFrame(profile['published_by_year'])
    num_published['Year'] = num_published['Year'].astype('str')
    num_published = num_published.sort_values(by='Year')
    tab.subheader('# of Publications')
    tab.bar_chart(data=num_published, x='Year', y='# of Publications')


    num_citations = pd.DataFrame(profile['citations_by_year'])
    num_citations['Year'] = num_citations['Year'].astype('str')
    num_citations = num_citations.sort_values(by='Year')
    tab.subheader('# of Citations')
    tab.bar_chart(data=num_citations, x='Year', y='# of Citations')


    avg_citations_by_publication_year = pd.DataFrame(profile['avg_citations_by_publication_year'])
    
    tab.subheader('Avg Citations per Publication by Publication Year')
    avg_citations_by_publication_year_chart = alt.Chart(avg_citations_by_publication_year).mark_line(
        point=alt.OverlayMarkDef(filled=False, fill='white', size=50)
    ).encode(
        alt.X('Publication Year:N', sort='ascending').title('Publication Year'),
        alt.Y('Avg Citations per Publication').title('Avg Citations per Publication'),
        
        
    )
    tab.altair_chart(avg_citations_by_publication_year_chart, use_container_width=True)
    
    # tab.subheader('KIV')
    # avg_citations_by_publication_year_chart = alt.Chart(avg_citations_by_publication_year).mark_line(
    #     point=alt.OverlayMarkDef(filled=False, fill='white', size=50)
    # ).encode(
    #     x='Publication Year',
    #     y='Avg Citations'
    # )
    # tab.altair_chart(avg_citations_by_publication_year_chart, use_container_width=True)


    tab.subheader('h-index by Year')
    h_index_by_year = pd.DataFrame(profile['h_index_by_year'])
    tab.bar_chart(data=h_index_by_year, x='Year', y='h-index')

    tab.subheader('h-index by Publication Year')
    h_index_by_publication_year = pd.DataFrame(profile['h_index_by_publication_year'])
    tab.bar_chart(data=h_index_by_publication_year, x='Publication Year', y='h-index')


    h_index_by_years_from_publication_year = pd.DataFrame(profile['h_index_by_years_from_publication_year'])
    publication_year = sorted(h_index_by_years_from_publication_year['Publication Year'].unique())
    h_index_by_years_from_publication_year = h_index_by_years_from_publication_year.sort_values(by=['Publication Year', 'Year'])
    h_index_by_years_from_publication_year['h-index'] = h_index_by_years_from_publication_year['h-index'].astype('int') 
    publication_year = [int(x) for x in publication_year]
    h_index = list(h_index_by_years_from_publication_year.groupby(by=['Publication Year'])['h-index'].apply(list).reset_index()['h-index'])
    
    tab.subheader('h-index by Year grouped by Publication Year')

    @st.cache_data
    def generate_graph_options(start, end, name):
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
                "data": publication_year,
                "name": "Year",
                "nameLocation": "middle",
                "nameTextStyle":{
                    "padding": [10,0,0,0],
                    "fontSize": 13,
                    "color": "rgb(250, 250, 250)"
                }
            },
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
                    "name": year,
                    "type": "line",
                    # "stack": "总量",
                    "data": [None]*(len(publication_year)-len(data)) + data
                }
                for year, data in zip(publication_year[start_index: end_index+1], h_index[start_index:end_index+1])
            ]
        }
        return options



    with tab:
        values = st.slider(
            'Select the range of publication year',
            min_value=publication_year[0], 
            max_value=publication_year[-1], 
            value=(publication_year[-5], publication_year[-1]),
            step=1
        )
        options = generate_graph_options(values[0], values[1], name=profile['full_name'])
        
        st_echarts(options=options, height="400px")
