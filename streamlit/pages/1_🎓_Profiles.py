import streamlit as st
import json
import pandas as pd
import datetime
import numpy as np
import math

from components.profile_background import generate_background
from components.profile_research import generate_research
from components.profile_collaboration import generate_collaboration
from components.profile_statistics import generate_statistic

import streamlit.components.v1 as components





@st.cache_data
def get_faculties():
    return pd.read_csv('./data_sources/processed/scse_profile.csv')


def get_profile(id):
    if id is not None:
        with open(f'./data_sources/profile/{id}.json', 'r') as f:
            profile = json.load(f)
        return profile
    return None

st.set_page_config(
    page_title="Profile",
    page_icon="👋",
)




faculties = get_faculties()

name_selected = st.selectbox(
    label='Professor', 
    options=sorted(faculties['full_name']), 
    index=None
)

if name_selected is None:
    st.subheader('Choose a Faculty from the dropdown above to begin!')

if name_selected is not None:
    id = faculties[faculties['full_name']==name_selected]['dr_ntu_id'].values[0]
    profile = get_profile(id)


    row0_photo, row0_info = st.columns(
        (2,5)
    )

    row0_photo.image(f"./data_sources/{profile['image_path'][2:]}")

    row0_info.write(f"""{profile['full_name']}  \n  {profile['designation']}""")


    row0_info.link_button(
        label='Email', 
        url='mailto:'+profile['email'], 
        use_container_width=True
    )

    row0_info.link_button(
        label='DR NTU', 
        url=profile['dr_ntu']if not(isinstance(profile['dr_ntu'], float) and math.isnan(profile['dr_ntu'])) else '', 
        disabled=False if not(isinstance(profile['dr_ntu'], float) and math.isnan(profile['dr_ntu'])) else True,
        use_container_width=True
    )
    row0_info.link_button(
        label='Google Scholar', 
        url=profile['google_scholar']if not(isinstance(profile['google_scholar'], float) and math.isnan(profile['google_scholar'])) else '', 
        disabled=False if not(isinstance(profile['google_scholar'], float) and math.isnan(profile['google_scholar'])) else True,
        use_container_width=True
    )

    row0_info.link_button(
        label='Personal Site', 
        url=profile['other_websites'][0] if not(isinstance(profile['other_websites'], float) and math.isnan(profile['other_websites'])) and len(profile['other_websites'])>0 else '', 
        disabled=False if not(isinstance(profile['other_websites'], float) and math.isnan(profile['other_websites'])) and len(profile['other_websites'])>0 else True,
        use_container_width=True
    )

    # row0_info.write(f"Interests: {', '.join(profile['interests'])}")

    # row0_info.write(f"Grants: {profile['grants']}")

    if isinstance(profile['google_scholar'], float) and math.isnan(profile['google_scholar']):
        st.warning('Google Scholar not available', icon="⚠️")

    else:
        st.write('heare')
        row1= st.columns(3)

        total_publications = sum(profile['published_by_year']['# of Publications'])
        total_citations = sum(profile['citations_by_year']['# of Citations'])

        row1[0].metric(
            label='\# of Publications', 
            value=total_publications,
            delta=f"{profile['published_by_year']['# of Publications'][profile['published_by_year']['Year'].index(str(datetime.datetime.now().year))]} YTD"
        )

        row1[1].metric(
            label='\# of Citations', 
            value=total_citations,
            delta=f"{profile['citations_by_year']['# of Citations'][profile['citations_by_year']['Year'].index(str(datetime.datetime.now().year))]} YTD"
        )

        row1[2].metric(
            label='Avg Citation per Publication', 
            value=round(total_citations / total_publications, 2),
            help='\# of Citations / # of Publications'
        )


        row2 = st.columns(3)

        row2[0].metric(
            label='All Time h-index', 
            value=profile['all_time_h_index']
        )

        row2[1].metric(
            label='All Time i10-index', 
            value=profile['all_time_i10_index']
        )

        row2[2].metric(
            label='All Time i20-index', 
            value=profile['all_time_i20_index']
        )

    

    list_tabs = ['Background', 'Research Focus', 'Collaboration', 'Research Impact']
    whitespace = 1
    tab1, tab2, tab3, tab4 = st.tabs(list_tabs)
    css = '''
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:1.5rem;
        }
    </style>
    '''

    st.markdown(css, unsafe_allow_html=True)

    
    generate_background(tab1, profile)

        
    tab2.info(
        body='Information is sourced from Google Scholar',
        icon='ℹ️'
    )
    if isinstance(profile['google_scholar'], float) and math.isnan(profile['google_scholar']):
        tab2.warning('Google Scholar not available', icon="⚠️")
    else:
        generate_research(tab2, profile)

    tab3.info(
        body='Information is sourced from Google Scholar',
        icon='ℹ️'
    )
    if isinstance(profile['google_scholar'], float) and math.isnan(profile['google_scholar']):
        tab3.warning('Google Scholar not available', icon="⚠️")
    else:
        generate_collaboration(tab3, profile)

    tab4.info(
        body='Information is sourced from Google Scholar',
        icon='ℹ️'
    )
    if isinstance(profile['google_scholar'], float) and math.isnan(profile['google_scholar']):
        tab4.warning('Google Scholar not available', icon="⚠️")
    else:
        generate_statistic(tab4, profile)