import sys
sys.path.append('../')

from bs4 import BeautifulSoup, NavigableString
import requests
import pandas as pd
import os
import json
from typing import Dict, List, Tuple



def generate_faculty_db(scse_profile):
    scse_profile['dr_ntu_id'] = scse_profile['dr_ntu'].apply(lambda x: x.split('/')[-1])
    
    return scse_profile[['full_name', 'email', 'dr_ntu', 'dr_ntu_id']]


def get_google_scholar(raw_dr_ntu_profile):
    google_scholar_id = None

    if raw_dr_ntu_profile['google_scholar'] is not None:
        google_scholar_id = raw_dr_ntu_profile['google_scholar'].split('user=')[1].split('&')[0]

    return google_scholar_id, raw_dr_ntu_profile['google_scholar']
