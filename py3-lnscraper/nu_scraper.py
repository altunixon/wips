#!/usr/bin/env python3
import requests, os, re, json
from lxml import html
from bs4 import BeautifulSoup
from browsers.html_scraper import html_scraper

xpath_nu_navigation = ''
xpath_nu_chapter = ''
xpath_nu_group = ''
xpath_nu_number = ''
xpath_nu_extnu = ''

series_watch = {
    'nu_url': {
        'transit_link': None, 
        'article_text': '', 
    }, 
}

if __name__ == '__main__':
    path_base = os.path.dirname(os.path.realpath(__file__))

    import argparse
    parser = argparse.ArgumentParser(description = 'Scraping Arguments.')
    parser.add_argument('-o', '--output', 
        dest = 'path_out', type = str, 
        default = os.path.join(path_base, 'articles'), 
        help = 'Output dir')
    parser.add_argument('-d', '--datastore', 
        dest = 'path_json', type = str, 
        default = os.path.join(path_base, 'watched.json'), 
        help = 'JSON Datastore')
    parser.add_argument('-u', '--update', dest = 'check_ulazy', action = 'store_true')
    parser.set_defaults(check_ulazy = False)
    console_args = parser.parse_args()
    
    # Load/Init JSON
    if os.path.isfile(console_args.path_json):
        with open(console_args.path_json, 'r') as j:
            data_watched = json.load(j)
    else:
        data_watched = {}
    
    # Process series
    procd = set([])
    for series_nu in series_watch.keys():
        page_next = series_nu
        while page_next is not None and page_next not in procd:
            ### CHANGE TO HTML_SCRAPER
            page_html = html.fromstring(requests.get(page_next).content)
            page_chapters = page_html.xpath()
