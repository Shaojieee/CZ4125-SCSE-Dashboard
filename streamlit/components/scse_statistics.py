import pandas as pd
import streamlit as st


def generate_statistic(tab, profile):
    with tab:
        st.subheader('\# of Publications')
        df = pd.DataFrame(profile['by_year'])
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