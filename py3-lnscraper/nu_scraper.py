#!/usr/bin/env python3
import requests, os, re, json
from lxml import html
from bs4 import BeautifulSoup
from collections import namedtuple
from helpers.str_helper import urlPrefixer, string_sanitizer
from helpers.misc import countdown
from helpers.dir_helper import MkDirP
from browsers.selenium import SeleniumBrowser
from browsers.scraper_lxml import html_scraper

nu_prefix = 'https://www.novelupdates.com/series/'
xpath_nu_navigation = '//a[@class="next_page"]'
xpath_nu_release = '//table[@id="myTable"]/tbody/tr'
xpath_nu_group = '//a[contains(@href, "/group/")]'
xpath_nu_chapter = '//a[contains(@class, "chp-release")]'
xpath_nu_extnu = '//a[contains(@class, "chp-release")]'

def chapter_zfill(chapter_txt, **zargs):
    if chapter_txt is not None:
        vfill = zargs.pop('vfill', 2)
        chfill = zargs.pop('chfill', 3)
        if 'v' in chapter_txt and 'c' in chapter_txt:
            str_vol, str_chp = chapter_txt.split('c', 1)
            num_vol = re.sub(r"\D", "", str_vol)
            num_chp = re.sub(r"\D", "", str_chp)
            chapter_fill = 'v%s-c%s' % (num_vol.zfill(vfill), num_chp.zfill(chfill))
        else:
            num_chp = re.sub(r"\D", "", chapter_txt)
            chapter_fill = 'c%s' % num_chp.zfill(chfill)
        return chapter_fill
    else:
        return None
    
def html2md(text_html, **kargs):
    soup_features = kargs.pop('features', 'lxml')
    soup_html = BeautifulSoup(text_html, features = soup_features)
    # kill all script and style elements
    for soup_script in soup_html(["script", "style"]):
        soup_script.decompose()    # rip it out
    soup_text = re.sub('^\n+', '\n', soup_html.get_text(), re.MULTILINE) # WTF no break!?
    # soup_text = soup_html.get_text()
    return soup_text.replace('\n', '<br/>\n')

def chapter_md(chapter_link, **kargs):
    xpath_article = kargs.pop('article', None)
    wait_seconds = kargs.pop('wait', 11)
    chapter_html = browser_sel.get(chapter_link, read=True, wait=wait_seconds)
    chapter_article = html_scraper(
        chapter_html, refer = chapter_link, tag_content = xpath_article
    )['tag_content']
    # print (chapter_html)
    if len(chapter_article) > 0:
        chapter_text = html2md(chapter_article[0])
    else:
        chapter_text = None
    return chapter_text

def chapter_transit(chapter_landing, **kargs):
    xpath_transit = kargs.pop('transit', None)
    xpath_article = kargs.pop('article', None)
    wait_seconds = kargs.pop('wait', 11)
    if xpath_transit is not None:
        landing_html = browser_sel.get(chapter_landing, read=True, wait=wait_seconds)
        landing_redirect = html_scraper(
            landing_html, 
            refer = chapter_landing, 
            href = xpath_transit
        )['href']
        if len(landing_redirect) > 0:
            landing_text = html_scraper(
                landing_html, refer = chapter_landing, tag_content = xpath_article
            )['tag_content']
            landing_md = html2md(landing_text[0])
            return '%s\n<br/>\n%s' % (
                landing_md, 
                chapter_md(landing_redirect[0], article = xpath_article)
            )
        else:
            return chapter_md(chapter_landing, article = xpath_article)
    else:
        return chapter_md(chapter_landing, article = xpath_article)

def json2dict(json_path):
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r') as jr:
                json_dict = json.load(jr)
        except Exception as excp:
            print (excp)
            json_dict = {}
    else:
        json_dict = {}
    return json_dict

if __name__ == '__main__':
    path_base = os.path.dirname(os.path.realpath(__file__))
    path_conf = os.path.join(path_base, 'list.json')
    browser_sel = SeleniumBrowser(
        capability='chrome@localhost:4445', 
        driver_bin='/usr/bin/chromedriver'
    )
    browser_sel.get(nu_prefix, wait=11)

    import argparse
    parser = argparse.ArgumentParser(description = 'Scraping Arguments.')
    #parser.add_argument(
    #    dest = 'list_url', nargs = '*', 
    #    default = [],
    #    help='URL(s) for the accumulator')
    parser.add_argument('-o', '--output', 
        dest = 'path_out', type = str, 
        default = os.path.join(path_base, 'articles'), 
        help = 'Output dir')
    parser.add_argument('-d', '--datastore', 
        dest = 'path_json', type = str, 
        default = os.path.join(path_base, 'watched.json'), 
        help = 'JSON Datastore')
    parser.add_argument('-w', '--wait', 
        dest = 'time_wait', type = int, 
        default = 3, 
        help = 'Wait time in-between curls')
    parser.add_argument('-u', '--update', dest = 'check_ulazy', action = 'store_true')
    parser.set_defaults(check_ulazy = False)
    console_args = parser.parse_args()
    
    # Set various wait times
    wait_boiler = namedtuple('WaitTime', ['low', 'medium', 'high'])
    if console_args.time_wait < 10:
        wait_time = wait_boiler(
            console_args.time_wait, round(console_args.time_wait * 1.5), round(console_args.time_wait * 2.5))
    else:
        wait_time = wait_boiler(
            round(console_args.time_wait * 0.75), console_args.time_wait, round(console_args.time_wait * 1.5))
    # Load/Init JSON
    conf_list = json2dict(path_conf)
    # Config format: { "template1": {"redirect", "article"}, "template2": {"redirect", "article"}, "list": {"name": {"redirect", "article"}, } }
    series_watch = {}
    if os.path.isfile(path_conf):
        for k, v in conf_list["list"].items():
            if isinstance(v, str):
                if v in conf_list.keys():
                    series_watch[k] = conf_list[v]
                else:
                    print ('[SKIP] Conf Template NotFound: "%s" = %s' % (k, v))
            elif isinstance(v, dict):
                if 'article' in v.keys() and len(v['article']) > 0:
                    series_watch[k] = v
                else:
                    print ('[SKIP] Conf XPath Missing: "%s" = %s' % (k, v))
            else:
                print ('[SKIP] Conf Invalid: "%s" = %s' % (k, v))
    else:
        pass
    data_watched = json2dict(console_args.path_json)
    
    # Process series
    page_done = set([])
    for series_nu in series_watch.keys():
        series_saveto = os.path.join(console_args.path_out, string_sanitizer(series_nu))
        MkDirP(series_saveto, meltdown = True)
        series_url = urlPrefixer(series_nu.strip('/'), nu_prefix)
        if series_url not in data_watched.keys():
            data_watched[series_url] = {}
        page_next = series_url
        while page_next is not None and page_next not in page_done:
            page_done.add(page_next)
            ### CHANGE TO HTML_SCRAPER
            browser_sel.get(page_next, read=False, wait=wait_time.high)
            if browser_sel.driver.current_url != page_next:
                browser_sel.get(page_next, read=False, wait=(wait_time.high + wait_time.medium))
            else:
                pass
            # print (html_scraper(page_html, tag_content = '//table[@id="myTable"]')['tag_content'])
            page_data = html_scraper(
                browser_sel.read(), 
                refer = page_next,
                pair = xpath_nu_release, 
                text_chapter = xpath_nu_chapter, 
                href_extnu = xpath_nu_extnu, 
                text_group = xpath_nu_group
            )
            if len(page_data['pair']) > 0:
                x = lambda y, z: y[z][0] if len(y[z]) > 0 else None
                for chapter_data in page_data['pair']:
                    chapter_extnu = urlPrefixer(x(chapter_data, 'href_extnu'), nu_prefix)
                    chapter_name = x(chapter_data, 'text_chapter')
                    # chapter_name = chapter_zfill(x(chapter_data, 'text_chapter'))
                    chapter_group = x(chapter_data, 'text_group')
                    if chapter_extnu is not None and chapter_name is not None:
                        if chapter_name not in data_watched[series_url].keys():
                            if 'transit' not in series_watch[series_nu].keys() \
                            or series_watch[series_nu]['transit'] is None:
                                chapter_out = chapter_md(
                                    chapter_extnu, 
                                    article = series_watch[series_nu]['article']
                                    wait = wait_time.medium
                                )
                            else:
                                chapter_out = chapter_transit(
                                    chapter_extnu, 
                                    transit = series_watch[series_nu]['transit'], 
                                    article = series_watch[series_nu]['article']
                                    wait_time = wait_time.medium
                                )
                            chapter_url = browser_sel.driver.current_url
                            print ('[READ] Scraping %s [%s %s]: %s' % (
                                    chapter_group, series_nu, chapter_name, chapter_url))
                            if chapter_out is not None:
                                chapter_saveas = os.path.join(series_saveto, 
                                    '%s.md' % string_sanitizer(chapter_name)
                                )
                                data_watched[series_url][chapter_name] = chapter_url
                            else:
                                print ('[#404] %s %s: "%s" > "%s"' % (series_nu, chapter_name, chapter_extnu, chapter_url))
                                chapter_saveas = os.path.join(series_saveto, 
                                    '%s-BLANK.md' % string_sanitizer(chapter_name)
                                )
                                chapter_out = 'Indx: "%s" <br/>\n#404: %s [%s] <br/>\nJump: "%s" <br/>\nDest: "%s"' % (
                                    page_next, 
                                    series_nu, 
                                    chapter_name, 
                                    chapter_extnu, 
                                    chapter_url
                                )
                            if not os.path.isfile(chapter_saveas):
                                with open(chapter_saveas, 'w') as sf:
                                    sf.write(chapter_out)
                            else:
                                print ('[SKIP] File "%s" Exists.' % chapter_saveas)
                            countdown(wait_time.low, txt = '%s: done next chapter in' % chapter_name)
                        else:
                            print ('[SKIP] Json "%s"' % data_watched[series_url][chapter_name])
                    else:
                        pass
                if not console_args.check_ulazy:
                    page_nav = html_scraper(page_html, refer = page_next, href = xpath_nu_navigation)['href']
                    page_next = '%s/%s' % (series_url.strip('/'), page_nav[0].replace('./', '')) \
                        if len(page_nav) > 0 \
                        else None
                    # print (page_next)
                else:
                    page_next = None
            else:
                page_next = None
            # countdown(3, txt = 'Next page "%s" in' % page_next)
        # Update watched.json after processing each serie
        with open(console_args.path_json, 'w', encoding='utf-8') as j:
            json.dump(data_watched, j, ensure_ascii=False, indent=4, sort_keys=True)
