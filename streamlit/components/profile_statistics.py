import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import altair as alt


def generate_statistic(tab, profile):
    num_published = pd.DataFrame({'Year': profile['published_by_year'].keys(), '# of Publications':profile['published_by_year'].values()})
    num_published['Year'] = num_published['Year'].astype('str')
    num_published = num_published.sort_values(by='Year')
    tab.subheader('# of Publications')
    tab.bar_chart(data=num_published, x='Year', y='# of Publications')


    num_citations = pd.DataFrame(profile['citations_by_year'])
    num_citations['Year'] = num_citations['Year'].astype('str')
    num_citations = num_citations.sort_values(by='Year')
    tab.subheader('# of Citations')
    tab.bar_chart(data=num_citations, x='Year', y='# of Citations')


    years_citations = list(profile['avg_citations_by_publication_year'].keys())
    avg_citations_by_publication_year = [profile['avg_citations_by_publication_year'][x] for x in years_citations]
    avg_citations_by_publication_year = pd.DataFrame({'Publication Year': years_citations, 'Avg Citations':avg_citations_by_publication_year})
    avg_citations_by_publication_year = avg_citations_by_publication_year.sort_values(by='Publication Year')
    avg_citations_by_publication_year['Avg Citations'] = avg_citations_by_publication_year['Avg Citations'].round(2)
    
    tab.subheader('Avg Citations by Publication Year')
    avg_citations_by_publication_year_chart = alt.Chart(avg_citations_by_publication_year).mark_line(
        point=alt.OverlayMarkDef(filled=False, fill='white', size=50)
    ).encode(
        x='Publication Year',
        y='Avg Citations'
    )
    tab.altair_chart(avg_citations_by_publication_year_chart, use_container_width=True)


    #TODO: change processing format
    tab.subheader('h-index by Year')
    years_citations = list(profile['h_index_by_year'].keys())
    h_index_by_year = [profile['h_index_by_year'][x] for x in years_citations]
    h_index_by_year = pd.DataFrame({'Year': years_citations, 'h-index':h_index_by_year})
    tab.bar_chart(data=h_index_by_year, x='Year', y='h-index')

    #TODO: Change processing format
    tab.subheader('h-index by Publication Year')
    years_citations = list(profile['h_index_by_publication_year'].keys())
    h_index_by_publication_year = [profile['h_index_by_publication_year'][x] for x in years_citations]
    h_index_by_publication_year = pd.DataFrame({'Publication Year': years_citations, 'h-index':h_index_by_publication_year})
    tab.bar_chart(data=h_index_by_publication_year, x='Publication Year', y='h-index')


    h_index = profile['h_index_by_years_from_publication_year']
    sorted_index = sorted(range(len(h_index['Publication Year'])), key=lambda index: h_index['Publication Year'][index])
    publication_year = [h_index['Publication Year'][i] for i in sorted_index]
    data__ = [h_index['h-index'][i] for i in sorted_index]

    tab.subheader('h-index by Year grouped by Publication Year')

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


    with tab:
        values = st.slider(
            'Select the range of publication year',
            min_value=publication_year[0], 
            max_value=publication_year[-1], 
            value=(publication_year[-5], publication_year[-1]),
            step=1
        )
        options = generate_graph_options(values[0], values[1])
        st_echarts(options=options, height="400px")

    




    tab.subheader('Publication Position')
    tab.write('First Author, Last Author, Co-Author, Single Author')
