import streamlit as st
import json
import os

def generate_research(tab, profile):
    @st.cache_data
    def get_research_summary(name):
        if os.path.exists(f"./data_sources/research_interest/{name.lower().replace(' ','_')}.json"):
            with open(f"./data_sources/research_interest/{name.lower().replace(' ','_')}.json") as f:
                summary = json.load(f)
            return {year: value['summary'] for year, value in summary.items()}
        else:
            return {}

    tab_0, tab_1 = tab.columns((1,3))
    tab_0.subheader('Year')
    tab_1.subheader('Summary')
    research_summary = get_research_summary(profile['full_name'])
    for year, summary in research_summary.items():
        tab_0, tab_1 = tab.columns((1,3))
        tab_0.write(year)
        tab_1.write(summary)


    