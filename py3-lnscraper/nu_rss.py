#!/usr/bin/env python3
import requests, os, re, json, feedparser, time
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
series_extras = set(['ss', 'intermission', 'prologue', 'epilogue', 'illust', 'side', 'part'])

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
    # decompose broke mercenary wordads c131
    return soup_text.replace('\n', '<br/>\n')

def chapter_md(chapter_link, **kargs):
    xpath_article = kargs.pop('article', None)
    wait_seconds = kargs.pop('wait', 5)
    # chapter_html = requests.get(chapter_link).content
    chapter_html = browser_sel.get(chapter_link, read=True, wait=wait_seconds)
    time.sleep(wait_seconds)
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
    wait_seconds = kargs.pop('wait', 5)
    if xpath_transit is not None:
        # landing_html = requests.get(chapter_landing).content
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

def chapter_name(chapter_text, **kwargs):
    chapter_elem = [string_sanitizer(x) for x in chapter_text.split() if len(x) > 0]
    chapter_check = lambda x, v, c: x[v:] if x[v].startswith('v') and x[c].startswith('c') else x[c:]
    if len(chapter_elem) >= 3:
        # matches 'name v24 c30 part1' 'name c31 part2' 'name v1 prologue' 'name v1s c5 epilogue'
        if any(x in chapter_elem[-1] for x in series_extras):
            chapter_x = '-'.join(chapter_check(chapter_elem, -3, -2))
        # matches 'name v1 c9 part 3' 'name c10 part 1'
        elif chapter_elem[-1].isdigit():
            chapter_x = '-'.join(chapter_check(chapter_elem, -4, -3))
        # matches 'name v1 c1' 'name c10'
        else:
            chapter_x = '-'.join(chapter_check(chapter_elem, -2, -1))
        # edge cases 'name ss 10' > 'name-ss-10'
        # 'series name ch 30' > 'name-ch-30', index exeption if string has less than 4 element after split()
    else:
        chapter_x = chapter_elem[-1]
    return chapter_x

if __name__ == '__main__':
    path_base = os.path.dirname(os.path.realpath(__file__))
    path_conf = os.path.join(path_base, 'list.json')
    browser_sel = SeleniumBrowser(
        capability='chrome@localhost:4445', 
        driver_bin='/usr/bin/chromedriver'
    )

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
    console_args = parser.parse_args()
    
    # Set various wait times
    wait_boiler = namedtuple('WaitTime', ['low', 'medium', 'high'])
    if console_args.time_wait < 10:
        wait_time = wait_boiler(
            console_args.time_wait, 
            round(console_args.time_wait * 1.5), 
            round(console_args.time_wait * 2.5)
        )
    else:
        wait_time = wait_boiler(
            round(console_args.time_wait * 0.75), 
            console_args.time_wait, 
            round(console_args.time_wait * 1.5)
        )
    # Load/Init JSON
    conf_list = json2dict(path_conf)
    # Config format: { "template1": {"redirect", "article"}, "template2": {"redirect", "article"}, "list": {"name": {"redirect", "article"}, } }
    series_watch = {}
    if os.path.isfile(path_conf):
        for k, v in conf_list["list"].items():
            series_watch[k] = {}
            nu_saveto = os.path.join(console_args.path_out, string_sanitizer(k))
            MkDirP(nu_saveto, meltdown=True)
            series_watch[k]['saveto'] = nu_saveto
            if isinstance(v, str):
                if v in conf_list.keys():
                    series_watch[k].update(conf_list[v])
                else:
                    print ('[SKIP] Conf Template NotFound: "%s" = %s' % (k, v))
            elif isinstance(v, dict):
                if 'article' in v.keys() and len(v['article']) > 0:
                    series_watch[k].update(v)
                else:
                    print ('[SKIP] Conf XPath Missing: "%s" = %s' % (k, v))
            else:
                print ('[SKIP] Conf Invalid: "%s" = %s' % (k, v))
    else:
        pass
    # print (json.dumps(series_watch, indent=4))
    data_watched = json2dict(console_args.path_json)
    for x in series_watch.keys():
        if x not in data_watched:
            data_watched[x] = {}
        else:
            pass

    rss_url = conf_list["rss"]
    rss_feed = feedparser.parse(rss_url)
    for rss_update in rss_feed.entries:
        rss_chapter = chapter_name(rss_update['title'])
        # rss_chapter = rss_update['title'].split()[-1].strip()
        if not rss_chapter.startswith('v') and not rss_chapter.startswith('c'):
            rss_chapter = string_sanitizer('-'.join(rss_update['title'].split()[-2:]))
        else:
            rss_chapter = string_sanitizer(rss_chapter)
        rss_title = rss_update['summary'].split(':')[-1].strip()
        rss_extnu = rss_update['link']
        # print (rss_title, rss_chapter, rss_extnu)
        for series_id, series_data in series_watch.items():
            # print (series_id)
            if series_id in rss_title:
                if rss_chapter not in data_watched[series_id].keys():
                    browser_sel.get(rss_extnu, read=False, wait=wait_time.medium)
                    if browser_sel.driver.current_url != rss_extnu:
                        chapter_url = browser_sel.driver.current_url
                    else:
                        raise
                    if len(chapter_url) > 0 and len(rss_chapter) > 0:
                        if 'transit' not in series_data.keys() \
                        or series_data['transit'] is None:
                            chapter_out = chapter_md(
                                chapter_url, 
                                article = series_data['article'], 
                                wait = wait_time.medium
                            )
                        else:
                            chapter_out = chapter_transit(
                                chapter_url, 
                                transit = series_data['transit'], 
                                article = series_data['article'], 
                                wait = wait_time.medium
                            )
                        print ('[READ] Scraping [%s %s]: %s' % (series_id, rss_title, chapter_url))
                        # print (series_id, series_data)
                        if chapter_out is not None:
                            chapter_saveas = os.path.join(series_data['saveto'], '%s.md' % string_sanitizer(rss_chapter))
                            data_watched[series_id][rss_chapter] = chapter_url
                        else:
                            print ('[#404] %s %s: "%s" > "%s"' % (series_id, rss_chapter, rss_extnu, chapter_url))
                            chapter_saveas = os.path.join(series_data['saveto'], '%s-BLANK.md' % string_sanitizer(rss_chapter))
                            chapter_out = '#404: %s [%s] <br/>\nJump: "%s" <br/>\nDest: "%s"' % (
                                series_id, rss_chapter, rss_extnu, chapter_url)
                        if not os.path.isfile(chapter_saveas):
                            with open(chapter_saveas, 'w') as sf:
                                sf.write(chapter_out)
                        else:
                            print ('[SKIP] File "%s" Exists.' % chapter_saveas)
                        countdown(wait_time.low, txt = '%s: done next chapter in' % rss_chapter)
                    else:
                        print ('[ERRO] Rss invalid data:\n"%s"' % json.dumps(rss_update))
                    break
                else:
                    print ('[SKIP] Json "%s": "%s"' % (rss_chapter, data_watched[series_id][rss_chapter]))
            else:
                pass
    with open(console_args.path_json, 'w', encoding='utf-8') as j:
        json.dump(data_watched, j, ensure_ascii=False, indent=4, sort_keys=True)
