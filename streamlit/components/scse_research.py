import streamlit as st
import pandas as pd
import altair as alt

def generate_research(tab, profile):
    with tab:
        st.subheader('Research Topics')
        publications = pd.DataFrame(profile['All Publications'])
        publications = publications.sort_values(by='total_citations', ascending=False)
        publications = publications[['name', 'title', 'topic', 'total_citations', 'publication_year', 'link']]
        topics_df = publications.groupby(by=['topic']).agg(
            num_publications=('title', len),
            total_citations=('total_citations', sum)
        ).reset_index()

        st.dataframe(
            topics_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'topic': 'Topic',
                'num_publications': '# of Publications',
                'total_citations': '# of Citations',
            }
        )

        topics = sorted(publications['topic'].unique())

        years = publications[publications['publication_year']!='Unknown']['publication_year'].unique()
        years = [int(x) for x in sorted(years)]

        st.subheader('Research Topics by Year')
        filter_by_year = tab.slider(
            label='Year Filter',
            min_value=years[0],
            max_value=years[-1],
            value=(years[0], years[-1]),
            step=1
        )

        filter_by_topic = tab.multiselect(
            label='Topic Filter',
            options=topics,
            default=None
        )
        filtered_publications = publications[((publications['publication_year']>=str(filter_by_year[0]))&(publications['publication_year']<=str(filter_by_year[1])))|((publications['publication_year']=='Unknown'))]
        if len(filter_by_topic)>0:
            filtered_publications = publications[publications['topic'].isin(filter_by_topic)]

        chart = alt.Chart(filtered_publications).mark_bar().encode(
            alt.X('publication_year:N', sort='ascending').title('Year'),
            alt.Y('count(title)').title('# of Publications'),
            color=alt.Color(
                'topic',
                title='Topic',
                legend=alt.Legend(
                    # orient='bottom',
                    # direction='horizontal'
                )
            )
        )

        st.altair_chart(chart, use_container_width=True, theme='streamlit')

        filtered_publications = filtered_publications.groupby(by=['name','topic']).agg(
            num_publications=('title', len),
            total_citations=('total_citations', sum)
        ).reset_index()

        st.dataframe(
            filtered_publications,
            use_container_width=True,
            hide_index=True,
            column_config={
                'name': 'Name',
                'topic': 'Topic',
                'num_publications': '# of Publications',
                'total_citations': '# of Citations',
            }
        )