import streamlit as st


def generate_background(tab, profile):
    tab.subheader('Education Background')
    row = tab.columns(3)
    row[0].write('Bachelors')
    row[0].write('--Not Available--' if profile['bachelor_degree'] is None else profile['bachelor_degree'])

    row[1].write('Masters')
    row[1].write('--Not Available--' if profile['masters'] is None else profile['masters'])

    row[2].write('PhD')
    row[2].write('--Not Available--' if profile['phd'] is None else profile['phd'])


    tab.subheader('Biography')
    tab.write(profile['biography'])