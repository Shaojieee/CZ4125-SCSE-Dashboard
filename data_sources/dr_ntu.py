from bs4 import BeautifulSoup, NavigableString
import requests
import pandas as pd
import os
import json
from typing import Dict, List, Tuple

class DR_NTU():
    def __init__(self, scse_profiles=None, individual_profiles=None):
        self.base_url = 'https://dr.ntu.edu.sg'

        self.scse_profiles = None
        if scse_profiles is not None:
            self.scse_profiles = pd.read_csv(scse_profiles)

        self.individual_profiles = {}
        if individual_profiles is not None:
            with open(individual_profiles, 'r') as f:
                self.individual_profiles = json.load(f) 

    
    def get_all_scse_profiles(self) -> pd.DataFrame:
        if self.scse_profiles is None:
            self.scrape_all_scse_profiles()
    
        return pd.DataFrame(self.scse_profiles)

    def get_profile_details(self, name: str) -> Dict:
        if name not in self.individual_profiles:
            self.scrape_individual_profile(name)
        
        return self.individual_profiles.get(name, None)

    def scrape_all_scse_profiles(self)->None:
        url = self.base_url+'/simple-search'
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
        self.scse_profiles = []
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
                        'dr_ntu_url': self.base_url + full_name.find('a')['href']
                    }

                    self.scse_profiles.append(profile)
            # Proceed to the next set of results
            params['start'] += params['rpp']
        
        self.scse_profiles = pd.DataFrame(self.scse_profiles)

        self.save_scse_profiles()
        return
    
    # Personal Information
    def scrape_position(self, html: BeautifulSoup)->str:
        div = html.find(name='span', attrs={'class':'namecard-fullname'}).parent
        div = div.find_next_sibling('div')
        id = div.get('id')
        if id==None:
            return div.text.strip()
        else:
            return None
    
    def scrape_name_card(self, html: BeautifulSoup)->str:
        span = html.find(name='span', attrs={'class':'namecard-fullname'})
        if span is None:
            return None
        return span.text.strip()
    
    def scrape_email(self,html: BeautifulSoup)->str:
        div = html.find(name='div', attrs={'id':'emailDiv'})
        if div is None:
            return None
        return div.text.strip()
    
    def scrape_websites(self, html: BeautifulSoup)->Dict[str, str]:
        div = html.find(name='div', attrs={'id':'personalsiteDiv'})
        if div is None:
            return {}
        a_tab = div.find_all(name='a')
        return {a.text.strip():a.get('href') for a in a_tab}

    # Information from `Profile` Section
    def scrape_keywords(self, html: BeautifulSoup)->List[str]:
        keywords_div = html.find(name='div', attrs={'id':'researchkeywords', 'class':'panel'})
        if keywords_div is None:
            return []
        keywords_span = keywords_div.find_all(name='span', attrs={'class':'rkeyword'})

        return [k.text.strip() for k in keywords_span]
        
    def scrape_biography(self, html: BeautifulSoup)->str:
        biography_div = html.find(name='div', attrs={'id':'biographyDiv'})
        return biography_div.text.strip()

    def scrape_research_interest(self, html: BeautifulSoup)->str:
        interest_div = html.find(name='div', attrs={'id':'researchinterestsDiv'})
        if interest_div is None:
            return None
        return interest_div.text.strip()
    
    def scrape_grants(self, html: BeautifulSoup)->str:
        grants_div = html.find(name='div', attrs={'id':'currentgrantsDiv'})
        if grants_div is None:
            return None
        return grants_div.text.strip()

    # Information from `Publication` Section
    def scrape_articles(self, html: BeautifulSoup)->List[str]:
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

    def scrape_books(self, html: BeautifulSoup)->List[str]:
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

    def scrape_book_chapters(self, html: BeautifulSoup)->List[str]:
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

    def scrape_conferences(self, html: BeautifulSoup)->List[str]:
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
    
    def scrape_bibliometrics(self, html: BeautifulSoup)->Dict[str, str]:
        div = html.find(name='div', attrs={'id':'custombiblio'})
        if div is None:
            return {}
        link_divs = div.find_all(name='div', attrs={'class':'dynaField'})
        links = {}

        for link in link_divs:
            a = link.find(name='a')
            links[a.text.strip()] = a.get('href')

        return links

    def scrape_individual_profile(self, name: str)->None:
        if self.scse_profiles is None:
            self.scrape_all_scse_profiles()

        # TODO: Make the scse profile have a unique index
        row = self.scse_profiles.loc[self.scse_profiles['full_name']==name,:].iloc[0]
        if len(row)==0:
            return 
        
        full_name = row['full_name']
        profile_url = row['dr_ntu_url']

        # Getting profile page
        resp = requests.get(
            url=profile_url
        )
        html = BeautifulSoup(resp.text, "html.parser")

        profile = {}

        profile['position'] = self.scrape_position(html)
        profile['name_card'] = self.scrape_name_card(html)
        profile['email'] = self.scrape_email(html)
        profile['websites'] = self.scrape_websites(html)

        # Information from `Profile` Section
        profile['keywords'] = self.scrape_keywords(html)
        profile['biography'] = self.scrape_biography(html)
        profile['interests'] = self.scrape_research_interest(html)
        profile['grants'] = self.scrape_grants(html)

        # Getting publication page
        publication_url = row['dr_ntu_url'] + '/selectedPublications.html'
        resp = requests.get(
            url=publication_url
        )
        html = BeautifulSoup(resp.text, "html.parser")

        # Information from `Publications` Section
        profile['articles'] = self.scrape_articles(html)
        profile['books'] = self.scrape_books(html)
        profile['book_chapters'] = self.scrape_book_chapters(html)
        profile['conferences'] = self.scrape_conferences(html)
        profile['bibliometrics'] = self.scrape_bibliometrics(html)

        self.individual_profiles[full_name] = profile
        return

    def scrape_everyone_profiles(self)->None:
        if self.scse_profiles is None:
            self.scrape_all_scse_profiles()
        
        for name in self.scse_profiles['full_name']:
            self.scrape_individual_profile(name)

    def save_scse_profiles(self, output_dir='./dr_ntu', output_filename='scse_profiles')->None:
        if self.scse_profiles is None:
            print('Run `scrape_all_scse_profiles` before saving')
        else:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, output_filename+'.csv')
            self.scse_profiles.to_csv(output_file, index=False)
            print(f'SCSE Profiles saved at {output_file}')

        return

    def save_individual_profiles(self, output_dir='./dr_ntu', output_filename='individual_profiles')->None:
        if len(self.individual_profiles)==0:
            print('Run `scrape_individual_profiles` before saving')
        else:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, output_filename+'.json')
            with open(output_file, 'w') as f:
                json.dump(self.individual_profiles, f)
            print(f'Individual Profiles saved at {output_file}')
        return