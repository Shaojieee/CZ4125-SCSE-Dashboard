from bs4 import BeautifulSoup
from collections import OrderedDict
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import time
import random
import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List



BASE_URL = "https://scholar.google.com"


def scrape_publications(driver:webdriver.Chrome)->Dict:
    try:
        time.sleep(random.uniform(3,7))
        button = driver.find_element(By.ID, "gsc_bpf_more")
        while button.get_attribute('disabled') is None:
            button.click()
            time.sleep(random.uniform(3,8))

        table = driver.find_element(By.ID, "gsc_a_b")
        table = table.get_attribute('outerHTML')
        table = BeautifulSoup(table, 'html.parser')

        rows = table.find_all(name='tr', attrs={'class':'gsc_a_tr'})
        publications = []

        for row in rows:
            result = {}

            publication = row.find(name='td', attrs={'class':'gsc_a_t'})
            title = publication.find(name='a', attrs={'class':'gsc_a_at'})
            result['title_link'] = title.get('href').strip()
            result['title'] = title.text.strip()

            details = publication.find_all(name='div', attrs={'class': 'gs_gray'})

            result['published_by'] = ''
            result['authors'] = []
            for detail in details:
                if detail.find(name='span', attrs={"class":'gs_oph'}):
                    result['published_by'] = detail.text.strip()
                else:
                    result['authors'] = detail.text.strip().split(', ')

            cited_by = row.find(name='td', attrs={'class':'gsc_a_c'})
            cited_by = cited_by.find(name='a', attrs={'class': ['gsc_a_ac', 'gs_ibl']})
            result['cited_by_link'] = cited_by.get('href').strip()
            result['cited_by'] = cited_by.text.strip()

            # if len(result['cited_by'])>0 and not result['cited_by'].isnumeric():
            #     print(f'Citation not number for {result["title"]} at {driver.current_url}')

            year = row.find(name='td', attrs={'class':'gsc_a_y'}).text
            result['year'] = year.strip()

            publications.append(result)
        
        publications = pd.DataFrame(publications)

        publications = publications.replace(r'^\s*$', np.nan, regex=True)

        publications['title_link'] = 'https://scholar.google.com' + publications['title_link']
        publications['cited_by'] = pd.to_numeric(publications['cited_by'], errors='coerce')
        publications['year'] = pd.to_numeric(publications['year'], errors='coerce')
        


        return publications.to_dict('records')
    except Exception as e:
        print(f'Error in scraping publications at {driver.current_url}')
        print(e)

        return None


def scrape_citation_table(table:BeautifulSoup)->Dict:
    table_dup = []
    table_head_row = table.find(name='thead').find_all(name='th')

    for i in range(len(table_head_row)):
        table_dup.append((table_head_row[i].text, []))

    table_body_row = table.find(name='tbody').find_all(name='tr')
    for row in table_body_row:
        cells = row.find_all(name='td')
        for i in range(len(cells)):
            table_dup[i][1].append(cells[i].text)

    return {x[0]: x[1]for x in table_dup}

def scrape_citation_graph(chart:BeautifulSoup)->Dict[int, int]:
    data = {}
    chart = chart.find(name='div', attrs={'class': 'gsc_md_hist_b'})

    years = chart.find_all(name='span', attrs={'class':'gsc_g_t'})
    cited = chart.find_all(name='a', attrs={'class':'gsc_g_a'})

    for i in range(len(years)):
        data[int(years[i].text.strip())] = int(cited[i].text.strip())

    return data

def scrape_citation_statistics(driver: webdriver.Chrome)->Dict:
    try:
        table = driver.find_element(By.ID, 'gsc_rsb_st')
        table = table.get_attribute('outerHTML')
        table = BeautifulSoup(table, 'html.parser')
        table = scrape_citation_table(table)

        open_chart_btn = driver.find_elements(By.ID, 'gsc_hist_opn')
        if len(open_chart_btn)>0:
            open_chart_btn[0].click()
            chart = driver.find_element(By.ID, 'gsc_md_hist_c')
            chart = chart.get_attribute('outerHTML')
            chart = BeautifulSoup(chart, 'html.parser')
            chart = scrape_citation_graph(chart)

            time.sleep(random.uniform(1,3))
            close_chart_btn = driver.find_element(By.ID, 'gsc_md_hist-x')
            close_chart_btn.click()
        else:
            chart = {}

        return {'table': table, 'chart': chart}
    except Exception as e:
        print(f'Error getting citation statistics at {driver.current_url}')
        print(e)
        return {'table':None, 'chart': None}


def scrape_co_authors(driver: webdriver.Chrome)->List[Dict]:
    try:
        co_authors_element = driver.find_elements(By.ID, 'gsc_rsb_co')
        if len(co_authors_element)==0:
            return []
        else:
            co_authors_element = co_authors_element[0]

        co_authors_element = co_authors_element.get_attribute('outerHTML')
        co_authors_div = BeautifulSoup(co_authors_element, 'html.parser')
        co_authors_li = co_authors_div.find_all(name='li')

        co_authors = []
        for author in co_authors_li:
            desc = author.find(name='span', attrs={'class':'gsc_rsb_a_desc'})
            a = desc.find(name='a')

            name = a.text
            link = a.get('href')

            ext = desc.find(name='span', attrs={'class':'gsc_rsb_a_ext'}).text

            co_authors.append(
                {
                    'link': BASE_URL + link,
                    'name': name,
                    'ext': ext
                }
            )
        return co_authors
    except:
        print(f'Error getting co authors at {driver.current_url}')
        return None


def scrape_google_scholar_profile(url: str):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(
            options=options
        )
        stealth(driver,
                # user_agent=agent,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        driver.get(url)
        time.sleep(random.uniform(3,5))
        citation_statistics = scrape_citation_statistics(driver)

        time.sleep(random.uniform(1,2))
        co_authors = scrape_co_authors(driver)

        # time.sleep(random.uniform(1,2))
        publications = scrape_publications(driver)

        driver.quit()

        return {'publications': publications, 'citation_statistics': citation_statistics, 'co_authors': co_authors}
    except:
        print(f'Error Scraping Google Scholar for {url}')
        return None

def save_google_scholar_profile(profile: Dict, output_filename, output_dir='./data'):
    os.makedirs(output_dir, exist_ok=True)
    output_filename = output_dir + '/' + output_filename

    with open(output_filename, 'w') as f:
        json.dump(profile, f)

# TODO: Need to take into account for the missing year citation number
def scrape_publication_details(url: str, driver: webdriver.Chrome):
    try:
        
        title = driver.find_element(By.ID, "gsc_oci_title")
        title = title.get_attribute('outerHTML')
        title = BeautifulSoup(title, 'html.parser')

        table = driver.find_element(By.ID, "gsc_oci_table")
        table = table.get_attribute('outerHTML')
        table = BeautifulSoup(table, 'html.parser')


        details = {}

        title_external_link = title.find(name='a', attrs={'class': 'gsc_oci_title_link'})
        if title_external_link.get('href')=='':
            details['external_link'] = None
        else: 
            details['external_link'] = title_external_link.get('href')

        rows = table.find_all(name='div', attrs={'class':'gs_scl'})
        for row in rows:
            field = row.find(name='div', attrs={'class':'gsc_oci_field'})
            value = row.find(name='div', attrs={'class':'gsc_oci_value'})

            field = field.text.strip().lower().replace(' ', '_')
            if field=='authors':
                value = value.text.strip().split(', ')

            elif field=='scholar_articles':
                continue
            elif field=='total_citations':
                years = value.find_all(name='span', attrs={'class': 'gsc_oci_g_t'})
                cited = value.find_all(name='a', attrs={'class': 'gsc_oci_g_a'})
                value = {int(year.text):0 for year in years}
                
                for cite in cited:
                    year = int(cite.get('href')[-4:])
                    value[year] = int(cite.text)

            else:
                value = value.text.strip()
            
            details[field] = value
        
        return details
    except:
        print(f'Error in scraping publication details at {url}')

        return {}

def save_publications_details(details, output_filename, output_dir='./data'):
    os.makedirs(output_dir, exist_ok=True)
    output_filename = output_dir + '/' + output_filename
    
    if os.path.isfile(output_filename):
        with open(output_filename, 'r') as f:
            updated = json.load(f)
        updated.update(details)
    else:
        updated = details
    
    with open(output_filename, 'w') as f:
        json.dump(updated, f)
