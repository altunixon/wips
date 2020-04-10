#!/usr/bin/env python3
import requests, os, re, json
from lxml import html
from bs4 import BeautifulSoup
from browsers.html_scraper import html_scraper

xpath_nu_navigation = ''
xpath_nu_release = ''
xpath_nu_group = ''
xpath_nu_chapter = ''
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
        series_id = series_nu.strip('/')
        if series_id not in data_watched.keys():
            data_watched[series_id] = {}
        page_next = series_nu
        while page_next is not None and page_next not in procd:
            procd.add(page_next)
            ### CHANGE TO HTML_SCRAPER
            page_html = requests.get(page_next).content
            page_data = html_scraper(
                page_html, 
                pair = xpath_nu_release, 
                text_chapter = xpath_nu_chapter, 
                href_extnu = xpath_nu_extnu, 
                text_group = xpath_nu_group
            )
            if len(page_data['pair']) > 0:
                x = lambda y, z: y[z][0] if len(y[z]) > 0 else None
                for chapter_data in page_data['pair']:
                    chapter_extnu = x(chapter_data, 'href_extnu')
                    chapter_text = x(chapter_data, 'text_chapter')
                    chapter_group = x(chapter_data, 'text_group')
                    if chapter_extnu is not None and chapter_text is not None:
                        if chapter_text not in data_watched[series_id].keys():
                            chapter_req = requests.head(chapter_extnu, allow_redirects = True)
                            chapter_url = chapter_req.url
                            chapter_html = chapter_req.read() ### ?????????
                            print ('[READ] Scraping %s [%s]: %s' % (chapter_group, chapter_text, chapter_url))
                            data_watched[series_id][chapter_text] = chapter_url
                        else:
                            print ('[SKIP] %s' % data_watched[series_id][chapter_text])
                    else:
                        pass
                page_nav = html_scraper(page_html, href = xpath_nu_navigation)
                page_next = page_nav[0] if len(page_nav) > 0 else None
            else:
                page_next = None
