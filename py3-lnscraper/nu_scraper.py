#!/usr/bin/env python3
import requests, os, re, json
from lxml import html
from bs4 import BeautifulSoup
from helpers.str_helper import urlPrefixer, string_sanitizer
from helpers.misc import countdown
from helpers.dir_helper import MkDirP
from browsers.scraper_lxml import html_scraper

nu_prefix = 'https://www.novelupdates.com/series/'
xpath_nu_navigation = '//a[@class="next_page"]'
xpath_nu_release = '//table[@id="myTable"]/tbody/tr'
xpath_nu_group = '//a[contains(@href, "/group/")]'
xpath_nu_chapter = '//a[@class="chp-release"]'
xpath_nu_extnu = '//a[@class="chp-release"]'

template_wordpress = {
    'transit_link': None, 
    'article_text': '//div[contains(@class, "entry-content")]', 
}

series_watch = {
    # 'a-demon-lords-tale-dungeons-monster-girls-and-heartwarming-bliss': {
    #     'transit_link': '/a[contains(@href, "jingai-musume-")]', 
    #     'article_text': '//div[class="reading-content"]'
    # }, 
    'sevens-ln': template_wordpress, 
    'isekai-tensei-soudouki': template_wordpress, 
    'the-strange-adventure-of-a-broke-mercenary': template_wordpress, 
    'okami-wa-nemuranai': template_wordpress, 
    'manuke-fps': template_wordpress, 
    'death-march-kara-hajimaru-isekai-kyusoukyoku': template_wordpress, 
    'the-death-mage-who-doesnt-want-a-fourth-time': {
        'transit_link': None,
        'article_text': '//div[@class="reading-content"]'
    }, 
    'i-became-the-strongest-with-the-failure-frame【abnormal-state-skill】as-i-devastated-everything': {
        'transit_link': None,
        'article_text': '//div[@class="reading-content"]'
    }, 
    'ankoku-kishi-monogatari-yuusha-wo-taosu-tameni-maou-ni-shoukansaremashita': {
        'transit_link': None,
        'article_text': '//div[@class="reading-content"]'
    }, 
}


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
    soup_text = re.sub('\n+', '\n', soup_html.get_text())
    return soup_text.replace('\n', '<br/>\n')

def chapter_md(chapter_link, **kargs):
    xpath_article = kargs.pop('article', None)
    chapter_html = requests.get(chapter_link).content
    chapter_article = html_scraper(
        chapter_html, 
        tag_content = xpath_article
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
    if xpath_transit is not None:
        landing_html = requests.get(chapter_landing).content
        landing_redirect = html_scraper(
            landing_html, 
            href = xpath_transit
        )['href']
        if len(landing_redirect) > 0:
            landing_text = html_scraper(
                landing_html, 
                tag_content = xpath_article
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
    parser.add_argument('-w', '--wait', 
        dest = 'time_wait', type = int, 
        default = 3, 
        help = 'Wait time in-between curls')
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
            page_html = requests.get(page_next).content
            # print (html_scraper(page_html, tag_content = '//table[@id="myTable"]')['tag_content'])
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
                    chapter_extnu = urlPrefixer(x(chapter_data, 'href_extnu'), nu_prefix)
                    chapter_name = x(chapter_data, 'text_chapter')
                    # chapter_name = chapter_zfill(x(chapter_data, 'text_chapter'))
                    chapter_group = x(chapter_data, 'text_group')
                    if chapter_extnu is not None and chapter_name is not None:
                        if chapter_name not in data_watched[series_url].keys():
                            chapter_req = requests.head(chapter_extnu, allow_redirects = True)
                            chapter_url = chapter_req.url
                            print (
                                '[READ] Scraping %s [%s]: %s' % (
                                    chapter_group, 
                                    chapter_name, 
                                    chapter_url
                                )
                            )
                            if series_watch[series_nu]['transit_link'] is None:
                                chapter_out = chapter_md(
                                    chapter_url, 
                                    article = series_watch[series_nu]['article_text']
                                )
                            else:
                                chapter_out = chapter_transit(
                                    chapter_url, 
                                    transit = series_watch[series_nu]['transit_link'], 
                                    article = series_watch[series_nu]['article_text']
                                )
                            if chapter_out is not None:
                                chapter_saveas = os.path.join(series_saveto, 
                                    '%s.md' % string_sanitizer(chapter_name)
                                )
                                data_watched[series_url][chapter_name] = chapter_url
                            else:
                                print ('[#404] %s: "%s" > "%s"' % (chapter_name, chapter_extnu, chapter_url))
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
                            countdown(console_args.time_wait, txt = '%s: done next chapter in' % chapter_name)
                        else:
                            print ('[SKIP] Json "%s"' % data_watched[series_url][chapter_name])
                    else:
                        pass
                if not console_args.check_ulazy:
                    page_nav = html_scraper(page_html, href = xpath_nu_navigation)['href']
                    page_next = '%s/%s' % (series_url.strip('/'), page_nav[0].replace('./', '')) \
                        if len(page_nav) > 0 \
                        else None
                    # print (page_next)
                else:
                    page_next = None
            else:
                page_next = None
            countdown(console_args.time_wait, txt = 'Next page "%s" in' % page_next)
        # Update watched.json after processing each serie
        with open(console_args.path_json, 'w', encoding='utf-8') as j:
            json.dump(data_watched, j, ensure_ascii = False, indent = 4)
