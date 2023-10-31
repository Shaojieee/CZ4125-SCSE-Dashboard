import sys
sys.path.append('../')

from bs4 import BeautifulSoup, NavigableString
import requests
import pandas as pd
import os
import json
from typing import Dict, List, Tuple


BASE_URL = 'https://dr.ntu.edu.sg'

def scrape_all_scse_profiles():
    url = BASE_URL+'/simple-search'
    params = {
        'filterquery': 'ou00030',
        'filtername': 'school',
        'filtertype': 'authority',
        'location': 'researcherprofiles',
        'sort_by': 'bi_sort_4_sort',
        'order': 'ASC',
        'rpp': 50,
        'start': 0
    }
    scse_profiles = []
    while True:
        resp = requests.get(
            url=url,
            params=params
        )
        html = BeautifulSoup(resp.text, "html.parser")

        # Iterate through the results for this page
        table = html.find('table')

        # No more records to be found
        if table is None:
            break
        else:
            rows = table.find_all('tr')
            for row in rows:
                full_name = row.find(name='td', headers='t1')
                email = row.find(name='td', headers='t3')
                
                # Checking if its a header row
                if full_name is None or email is None:
                    continue
                profile = {
                    'full_name': full_name.text,
                    'email': email.text,
                    'dr_ntu': BASE_URL + full_name.find('a')['href']
                }

                scse_profiles.append(profile)
        # Proceed to the next set of results
        params['start'] += params['rpp']
    
    scse_profiles = pd.DataFrame(scse_profiles)

    return scse_profiles

# Personal Information
def scrape_position(html: BeautifulSoup)->str:
    div = html.find(name='span', attrs={'class':'namecard-fullname'}).parent
    div = div.find_next_sibling('div')
    id = div.get('id')
    if id==None:
        return div.text.strip()
    else:
        return None

def scrape_name_card(html: BeautifulSoup)->str:
    span = html.find(name='span', attrs={'class':'namecard-fullname'})
    if span is None:
        return None
    return span.text.strip()

def scrape_email(html: BeautifulSoup)->str:
    div = html.find(name='div', attrs={'id':'emailDiv'})
    if div is None:
        return None
    return div.text.strip()

def scrape_websites(html: BeautifulSoup)->Dict[str, str]:
    div = html.find(name='div', attrs={'id':'personalsiteDiv'})
    if div is None:
        return {}
    a_tab = div.find_all(name='a')

    links = {}

    for a in a_tab:
        link = a.get('href')
        text = a.text
        if link is None or link=='#':
            continue
        if 'scholar.google' in link:
            key = 'google_scholar'
        elif 'orcid.org' in link:
            key = 'orcid'
        elif 'github' in link:
            key = 'github'
        elif 'scopus' in link:
            key = 'scopus'
        elif 'webofscience' in link:
            key = 'web_of_science'
        # TODO: Create better logic to separate personal site
        # elif 'website' in text.lower() or 'homepage' in text.lower() or 'ntu.edu.sg' in link:
        #     key = 'personal_website'
        else:
            key = 'others'
        
        if key=='others':
            links[key] = links.get(key, []) + [link]
        else:
            links[key] = link


    return links

def scrape_profile_picture(html:BeautifulSoup, full_name:str, output_dir='./profile_img')->str:
    img = html.find(name='img', attrs={'id':'picture'})
    img_link = 'https://dr.ntu.edu.sg' + img.get('src')
    resp = requests.get(img_link)

    os.makedirs(output_dir, exist_ok=True)

    with open(f"./profile_img/{full_name.lower().replace(' ', '_')}.jpg", "wb") as f:
        f.write(resp.content)
    return f"./profile_img/{full_name.lower().replace(' ', '_')}.jpg"

# Information from `Profile` Section
#TODO: Check if there are any more sections in `div` with `id=accordian`
def scrape_keywords(html: BeautifulSoup)->List[str]:
    keywords_div = html.find(name='div', attrs={'id':'researchkeywords', 'class':'panel'})
    if keywords_div is None:
        return []
    keywords_span = keywords_div.find_all(name='span', attrs={'class':'rkeyword'})

    return [k.text.strip() for k in keywords_span]
    
def scrape_biography(html: BeautifulSoup)->str:
    biography_div = html.find(name='div', attrs={'id':'biographyDiv'})
    return biography_div.text.strip()

def scrape_research_interest(html: BeautifulSoup)->str:
    interest_div = html.find(name='div', attrs={'id':'researchinterestsDiv'})
    if interest_div is None:
        return None
    return interest_div.text.strip()

def scrape_grants(html: BeautifulSoup)->str:
    grants_div = html.find(name='div', attrs={'id':'currentgrantsDiv'})
    if grants_div is None:
        return None
    return grants_div.text.strip()

#TODO: Scrape from `div` with `id=teaching`
def scrape_course_taught(html: BeautifulSoup)->List[str]:
    return []

# Information from `Publication` Section
def scrape_articles(html: BeautifulSoup)->List[str]:
    div = html.find(name='div', attrs={'id':'facultyjournalDiv'})
    if div is None:
        return []
    title = []

    # Code from google
    # Jump from 1 br to another to extract the string inbetween each br
    for br in div.find_all('br'):
        next_s = br.nextSibling
        if not (next_s and isinstance(next_s,NavigableString)):
            continue
        next2_s = next_s.nextSibling
        cur = str(next_s.text)
        while next2_s and next2_s.name!='br':
            cur = cur + str(next2_s.text)
            next2_s = next2_s.nextSibling
        if cur is not None and not ('highly cited' in cur.lower() or 'recent publication' in cur.lower()):
            title.append(cur.strip())

    return title

def scrape_books(html: BeautifulSoup)->List[str]:
    div = html.find(name='div', attrs={'id':'facultybooksDiv'})
    if div is None:
        return []
    title = []

    # Code from google
    # Jump from 1 br to another to extract the string inbetween each br
    for br in div.find_all('br'):
        next_s = br.nextSibling
        if not (next_s and isinstance(next_s,NavigableString)):
            continue
        next2_s = next_s.nextSibling
        cur = str(next_s.text)
        while next2_s and next2_s.name!='br':
            cur = cur + str(next2_s.text)
            next2_s = next2_s.nextSibling
        if cur is not None:
            title.append(cur.strip())

    return title

def scrape_book_chapters(html: BeautifulSoup)->List[str]:
    div = html.find(name='div', attrs={'id':'facultybookchaptersDiv'})
    if div is None:
        return []
    title = []

    # Code from google
    # Jump from 1 br to another to extract the string inbetween each br
    for br in div.find_all('br'):
        next_s = br.nextSibling
        if not (next_s and isinstance(next_s,NavigableString)):
            continue
        next2_s = next_s.nextSibling
        cur = str(next_s.text)
        while next2_s and next2_s.name!='br':
            cur = cur + str(next2_s.text)
            next2_s = next2_s.nextSibling
        if cur is not None:
            title.append(cur.strip())

    return title

def scrape_conferences(html: BeautifulSoup)->List[str]:
    div = html.find(name='div', attrs={'id':'facultyconfDiv'})
    if div is None:
        return []
    title = []

    # Code from google
    # Jump from 1 br to another to extract the string inbetween each br
    for br in div.find_all('br'):
        next_s = br.nextSibling
        if not (next_s and isinstance(next_s,NavigableString)):
            continue
        next2_s = next_s.nextSibling
        cur = str(next_s.text)
        while next2_s and next2_s.name!='br':
            cur = cur + str(next2_s.text)
            next2_s = next2_s.nextSibling
        if cur is not None and not ('highly cited' in cur.lower() or 'recent publication' in cur.lower()):
            title.append(cur.strip())

    return title

def scrape_bibliometrics(html: BeautifulSoup)->Dict[str, str]:
    div = html.find(name='div', attrs={'id':'custombiblio'})
    if div is None:
        return {}
    link_divs = div.find_all(name='div', attrs={'class':'dynaField'})
    links = {}

    for link_div in link_divs:
        a = link_div.find(name='a')
        link = a.get('href')
        if link is None:
            continue
        if 'scholar.google' in link:
            key = 'google_scholar'
        elif 'scopus' in link:
            key = 'scopus'
        elif 'webofscience' in link:
            key = 'web_of_science'
        else:
            key = 'others'
        
        if key=='others':
            links[key] = links.get(key, []) + [link]
        else:
            links[key] = link

    return links

def scrape_individual_profile(url:str, full_name:str)->Dict:

    # Getting profile page
    resp = requests.get(
        url=url
    )
    html = BeautifulSoup(resp.text, "html.parser")

    profile = {}
    profile['full_name'] = full_name
    profile['designation'] = scrape_position(html)
    profile['name_card'] = scrape_name_card(html)
    profile['email'] = scrape_email(html)
    profile['websites'] = scrape_websites(html)
    profile['image_path'] = scrape_profile_picture(html, full_name)

    # Information from `Profile` Section
    profile['keywords'] = scrape_keywords(html)
    profile['biography'] = scrape_biography(html)
    profile['interests'] = scrape_research_interest(html)
    profile['grants'] = scrape_grants(html)

    # Getting publication page
    publication_url = url + '/selectedPublications.html'
    resp = requests.get(
        url=publication_url
    )
    html = BeautifulSoup(resp.text, "html.parser")

    # Information from `Publications` Section
    profile['articles'] = scrape_articles(html)
    profile['books'] = scrape_books(html)
    profile['book_chapters'] = scrape_book_chapters(html)
    profile['conferences'] = scrape_conferences(html)
    profile['bibliometrics'] = scrape_bibliometrics(html)

    # Merging `bibliometrics` into `websites`. Taking the value of `bibliometrics` if there are overlapping keys
    for k, v in profile['bibliometrics'].items():
        if k=='others':
            profile['websites']['others'] = list(set(profile['websites'].get('others', []) + profile['bibliometrics']['others']))
        else:
            profile['websites'][k] = profile['bibliometrics'][k]
    
    # Break down websites into individual components
    profile['google_scholar'] = profile['websites'].get('google_scholar', None)
    profile['orcid'] = profile['websites'].get('orcid', None)
    profile['github'] = profile['websites'].get('github', None)
    profile['scopus'] = profile['websites'].get('scopus', None)
    profile['web_of_science'] = profile['websites'].get('web_of_science', None)
    profile['dr_ntu'] = url
    profile['other_websites'] = profile['websites'].get('others', [])
    del profile['websites']

    return profile


def save_individual_profile(profile, output_filename, output_dir='./raw_dr_ntu'):
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, output_filename+'.json')
    with open(output_file, 'w') as f:
        json.dump(profile, f)
    return