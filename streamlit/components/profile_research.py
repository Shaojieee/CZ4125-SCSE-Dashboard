import streamlit as st
import json
import os
import datetime
import pandas as pd
import math
from streamlit_option_menu import option_menu
import altair as alt

def generate_research(tab, profile):
    
    if 'research_page' not in st.session_state:
        st.session_state['research_page'] = 1
    
    def reset_page():
        st.session_state['research_page'] = 1

    publications = profile['publications']

    publication_df = pd.DataFrame(publications)
    topics = sorted(publication_df['Topic'].unique())


    publication_df['Publication Year'] = publication_df['Publication Year'].fillna('Unknown')
    publication_df['Publication Year'] = publication_df['Publication Year'].astype(str)
    years = publication_df[publication_df['Publication Year']!='Unknown']['Publication Year'].unique()
    years = [int(x) for x in sorted(years)]

    filter_by_year = tab.slider(
        label='Year Filter',
        min_value=years[0],
        max_value=years[-1],
        value=(years[0], years[-1]),
        step=1,
        on_change=reset_page
    )

    filter_by_topic = tab.multiselect(
        label='Topic Filter',
        options=topics,
        default=None,
        on_change=reset_page
    )

    
    filtered_publications = publication_df[((publication_df['Publication Year']>=str(filter_by_year[0]))&(publication_df['Publication Year']<=str(filter_by_year[1])))|(publication_df['Publication Year']=='Unknown')]
    if len(filter_by_topic)>0:
        filtered_publications = publication_df[publication_df['Topic'].isin(filter_by_topic)]



    chart = alt.Chart(filtered_publications).mark_bar().encode(
        alt.X('Publication Year:N', sort='ascending').title('Year'),
        alt.Y('count(Title)').title('# of Publications'),
        color=alt.Color(
            'Topic',
            title='Topic',
            legend=alt.Legend(
                orient='bottom',
                direction='horizontal'
            )
        )
    )

    tab.altair_chart(chart, use_container_width=True, theme='streamlit')



    sort_by = tab.radio(
        label='Sort By',
        options=['Publication Year', '\# of Citations'],
        horizontal=True
    )

    if sort_by=='\# of Citations':
        sort_by='# of Citations'
    elif sort_by=='Publication Year':
        filtered_publications['Publication Year'] = filtered_publications['Publication Year'].replace('Unknown', '0')

        filtered_publications = filtered_publications.sort_values(by=sort_by, ascending=False)
        filtered_publications['Publication Year'] = filtered_publications['Publication Year'].replace('0', 'Unknown')

    num_per_page = 5
    num_pages = math.ceil(len(filtered_publications)/num_per_page)


    start_index = (st.session_state['research_page']-1)*num_per_page
    end_index = min(st.session_state['research_page']*num_per_page, len(filtered_publications))
    
    col = tab.columns((1,1.75))
    with col[0]:
        st.subheader('Title')
        titles = []
        for i,row in filtered_publications.iloc[start_index: end_index,:].iterrows():
            titles.append(row['Title'])
        selected_title = option_menu(
            "", 
            titles, 
            icons=['book']*len(titles),
            default_index=0
        )
        
    
    with col[1]:
        st.subheader('Details')
        row = filtered_publications[filtered_publications['Title']==selected_title].iloc[0,:]
        # st.write(row)
        st.markdown('##### Published Year')
        st.write(f"{row['Publication Year']}")

        st.markdown('##### Topic')
        st.write(f"{row['Topic']}")



        st.markdown('##### # of Citations')
        st.write(f"{str(row['# of Citations'])}")


        st.markdown('##### Description')
        st.write(row['Description'] if row['Description'] is not None else '--No description available--')
    
    
    # Page Control
    def next_page():
        st.session_state['research_page'] += 1

    def previous_page():
        st.session_state['research_page'] -= 1

    def check_previous_page_disabled():
        current_page = st.session_state['research_page']

        return current_page==1

    def check_next_page_disabled():
        current_page = st.session_state['research_page']

        return current_page==num_pages
    
    buttons = col[0].columns(3)
    buttons[0].button('⇦', use_container_width=True, on_click=previous_page, disabled=check_previous_page_disabled())
    buttons[1].markdown(f"<p style='text-align: center;'>{st.session_state['research_page']}/{num_pages}</>", unsafe_allow_html=True)
    
    buttons[2].button('⇨', use_container_width=True, on_click=next_page, disabled=check_next_page_disabled())
    