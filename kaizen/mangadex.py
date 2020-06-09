#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, json
from random                 import randint
from shutil                 import move
from urllib.parse           import unquote, urlsplit
from browsers.selenium      import SeleniumBrowser
from browsers.requests      import RequestsBrowser
from browsers.scraper_lxml  import html_scraper, spiderman
from helpers.str_helper     import urlPrefixer, string_sanitizer
from helpers.misc           import db_init, print_log, countdown, FormatDefault

from selenium.webdriver.common.action_chains import ActionChains

def check_quick(chap_list, index_list):
    pass

def get_html(get_url, **options):
    global console_args, mdex_visual
    viewer_dump = options.pop('dump', None)
    viewer_html = mdex_visual.read(
        get_url, 
        wait = randint(7, 11), 
        dump = viewer_dump
    )
    viewer_pgskip = mdex_visual.driver.find_elements_by_xpath(
        '//div[contains(@class, "alert-warning")]'
    )
    if len(viewer_pgskip) > 0:
        for warn_element in viewer_pgskip:
            if 'gap between chapter' in warn_element.text.lower():
                print_log('warn', 'CHAPGAP: %s', viewer_pgskip[0].text)
                viewer_pgskip[0].click()
                countdown(randint(7, 11), txt='Re-Loading "%s"' % get_url)
                viewer_html = mdex_visual.read(dump = viewer_dump)
                break
            else:
                pass
            # print (warn_element.get_attribute('outerHTML'))
    else:
        pass
    return viewer_html

if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(
        description='Download URL',
        argument_default=argparse.SUPPRESS, 
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        dest='url_list', nargs='*', default=[],
        help='an URL for the accumulator')
    parser.add_argument(
        '-o', '--out-path', dest='saveto', nargs='?', default=os.path.join(os.getcwd(), 'downloads'), 
        help='Download to folder')
    parser.add_argument(
        '-f', '--list-file', dest='url_file', nargs='?', default=None, 
        help='List file')
    parser.add_argument(
        '-d', '--database', dest='db_connector', nargs='?', default=None, 
        help='Set database connect string, default=None database is disabled')
    parser.add_argument(
        '-b','--browser',dest='browser',nargs='?',default='chrome',
        help='Browser type: default=chrome (via native chromewebdriver) use firefox if needed be.')
    parser.add_argument(
        '-c', '--check', dest='verify', action='store_true', 
        help='Force Verify image if file is not in db, by default will not verify if file exists in db or destination')
    parser.set_defaults(verify=False)
    parser.add_argument(
        '-w', '--wait', dest='wait', nargs='?', type=int, default=10,
        help='wait n seconds between downloads (default = 5 seconds).')
    parser.add_argument(
        '-q', '--quiet', dest='verbose', action='store_false', 
        help='Quiet, subdue all output print only essential info, disable delete corrupt prompt')
    parser.set_defaults(verbose=True)
    parser.add_argument(
        '-r', '--redownload', dest='redownload', action='store_true', 
        help='Redownload if possible, ignore db file status')
    parser.set_defaults(redownload=False)
    parser.add_argument(
        '--reverse', dest='reverse_order', action='store_true', 
        help='Revert chapter order, download oldest first')
    parser.set_defaults(reverse_order=False)
    parser.add_argument(
        '--lazy', dest='lazy', action='store_true', 
        help='Skip on first downloaded chapter, should only be used for increment downloads.')
    parser.set_defaults(lazy=False)
    parser.add_argument(
        '--headless', dest='headless', action='store_true', 
        help='Headless mode.')
    parser.set_defaults(headless=False)
    console_args = parser.parse_args()
    mdex_db = db_init(console_args.db_connector)
    # DECLARE BROWSERS
    mdex_cloudflr = RequestsBrowser(
        verify      = console_args.verify, 
        verbose     = console_args.verbose,
        cloudflare  = True,
        retry       = 1
    )
    mdex_visual = SeleniumBrowser(
        private     = True, 
        capability  = console_args.browser, 
        hide        = False,
        headless    = console_args.headless,
        verify      = console_args.verify
    )

    if console_args.url_file is None:
        pass
    else:
        if len(console_args.url_file) == 0:
            for sdir in next(os.walk(console_args.saveto))[1]:
                url_path = sdir.rsplit('(', 1)[-1].strip(')')
                console_args.url_list.append(url_path)
        else:
            if os.path.isfile(console_args.url_file):
                with open(console_args.url_file, 'r') as uf:
                    url_fl = [
                        u.strip() for u in uf.read().splitlines() \
                            if len(u.strip()) > 0 \
                            and not u.startswith('#')
                    ]
                console_args.url_list.extend(url_path)
            else:
                pass
        

    for mdex_url in console_args.url_list:
        mdex_series = string_sanitizer(
            mdex_url.split('//',1)[1].split('.',1)[0] \
                if '//' in mdex_url \
                else mdex_url.strip('/').split('/', 1)[0]
        )

        mdex_fqdn = 'https://mangadex.org'
        xpath_index_infos = {
            'text_title' : '//span[@class="mx-1"]', 
            'text_artist': '//a[contains(@href, "/search?artist=")]', 
            'content'    : '//meta[@name="description"]', 
            'href'       : '//li[contains(@class, "page-item")]/a[contains(@href, "/title/")]'
        }
        xpath_chapter_rows = {
            'pair'      : '//div[contains(@class, "chapter-row") and @data-id]',
            'data-chapter': '//div[contains(@class, "chapter-row")]',
            'text_group': '//div[contains(@class, "chapter-list-group")]/a[contains(@href, "/group/")]',
            'href'      : '//div[contains(@class, "col-lg-")]/a[contains(@href, "/chapter/")]',
            'text_title': '//div[contains(@class, "col-lg-")]/a[contains(@href, "/chapter/")]',
            'title'     : '//div[contains(@class, "chapter-list-flag")]/span[contains(@class, "flag")]'
        }
        xpath_viewer_display = {
            'src' : ['//div[contains(@class, "reader-image-wrapper")]/img[contains(@src, "/data")]'],
            'href': '//a[contains(@class, "page-link-right")]/span', # and @data-action="page"
            'text_total': '//span[@class="total-pages"]'
        }
        # xpath_viewer_next = '//div[contains# (@class, "reader-image-wrapper")]'
        xpath_viewer_next = '//a[contains(@class, "arrow-link") and @data-action="page" and @data-direction="right" and @data-by="1"]'
        # xpath_view_pgnext = '//div[contains(@class, "reader-image-wrapper")]/img[contains(@src, "/data/")]'
        xpath_view_pgnext = '//a[contains(@class, "page-link-right") and contains(@href, "/chapter/{chapter}/{page}")]/span'
        series_name_format = '[{artist}] {title} ({id})'
        chapter_name_format = '{series} ({chapter}) {title} [{group}] [{id}]'
        chapter_page_format = '{series}-ch{chapter}_pg{page_num:03d}-{link_name}'
        mdex_whitelist_language = set(['English', 'Japanese'])
        mdex_blacklist_group = set(['MangaPlus'])
        #xpath_index_pages = '//li[contains(@class, "page-item")]/a[contains(@href, "/title/")]'
        if 'title/' in mdex_url:
            series_id = mdex_url.split('title/', 1)[1].split('/')[0]
            series_url = urlPrefixer(mdex_url, mdex_fqdn)
        else:
            series_id  = mdex_url.strip('/').split('/', 1)[0]
            series_url = urlPrefixer(mdex_url, mdex_fqdn + '/title/').strip('/')
        #print(series_url)
        # GET SERIES LANDING PAGE
        series_html = mdex_cloudflr.get(
            series_url, 
            wait=console_args.wait, 
            read=True)
        #with open('/tmp/mdex_%s.html' % mdex_series, 'w+') as mdex:
        #    mdex.write(series_html)

        index_spider = spiderman(
            series_html, 
            refer=series_url, 
            verbose=console_args.verbose)
        index_infos = index_spider.scraper(**xpath_index_infos)
        index_display_name = string_sanitizer(index_infos['text_title'][0])
        mdex_save_dir = string_sanitizer(
            series_name_format.format(
                artist  = ', '.join(index_infos['text_artist']),
                title   = index_display_name,
                id      = series_id
            ),
            paranoia=True
        )
        mdex_save_path = os.path.join(console_args.saveto, mdex_save_dir)
        #print(json.dumps(index_infos['href'], indent=4))
        # INDEXES LOOP
        index_all = [series_url]
        index_nav = [urlPrefixer(u, mdex_fqdn) \
            for u in index_infos['href'] \
                if not series_url.endswith(u)]
        for u in index_nav:
            if u not in index_all \
            and u.strip('/') != '%s/chapters/1' % series_url.strip('/'):
                index_all.append(u)
            else:
                pass
        #print(index_all)
        skip_series = False
        index_pages_ordered = sorted(index_all, key=len)
        if console_args.reverse_order:
            index_pages_ordered.reverse()
        else:
            pass
        for index_pg in index_pages_ordered:
            print_log(
                'debug', 
                'PROCESSING %s\nManga: %s', 
                index_pg, 
                mdex_save_dir
            )
            # GENERATE CHAPTERS LIST
            if index_pg.endswith('/1') or index_pg == series_url:
                chapter_infos = html_scraper(
                    series_html, 
                    **xpath_chapter_rows,
                    uniq=True
                )['pair']
            else:
                index_url = urlPrefixer(index_pg, mdex_fqdn)
                #print('BOGGOS', index_pg, index_url)
                index_html= mdex_cloudflr.get(
                    index_url, 
                    wait=console_args.wait, 
                    read=True)
                chapter_infos = html_scraper(
                    index_html, 
                    **xpath_chapter_rows,
                    uniq=True)['pair']
            # PROCESS CHAPTERS
            if console_args.reverse_order:
                chapter_infos.reverse()
            else:
                pass
            for chapter_data in chapter_infos:
                #print(json.dumps(chapter_data, indent=4))
                # IGNORE ERRY THING NOT IN WHITELIST
                if len(chapter_data['title']) > 0 \
                and chapter_data['title'][0] in mdex_whitelist_language \
                and chapter_data['text_group'][0] not in mdex_blacklist_group:
                    print_log('info', 'GETTING: {href} {title} Chapter: {data-chapter} {text_title} {text_group}'.format(**chapter_data))
                    chapter_url = urlPrefixer(
                        chapter_data['href'][0], mdex_fqdn)
                    # chapter_no = int(float(chapter_data['data-chapter'][0]))
                    chapter_no = '%03d' % int(chapter_data['data-chapter'][0]) \
                        if '.' not in chapter_data['data-chapter'][0] \
                        else '%05.1f' % float(chapter_data['data-chapter'][0])
                    chapter_id = chapter_url.strip('/').rsplit('/', 1)[1]
                    table_id = '%s_%s' % (series_id, chapter_id)
                    if mdex_db is not None:
                        mdex_db.run(
                            table=table_id, 
                            mode='create table', 
                            view='VARCHAR(32) PRIMARY KEY', 
                            save='TEXT'
                        )
                        chapter_downloaded = mdex_db.run(
                            table=table_id, 
                            mode='select all',
                            default=True)
                    else:
                        chapter_downloaded = []
                    chapter_folder = string_sanitizer(
                        chapter_name_format.format(
                            series = index_display_name, 
                            chapter= chapter_no,
                            title  = chapter_data['text_title'][0],
                            group  = chapter_data['text_group'][0],
                            id     = chapter_id
                        ),
                        paranoia=True
                    )
                    page_saveto = os.path.join(mdex_save_path, chapter_folder)
                    if not os.path.exists(page_saveto):
                        os.makedirs(page_saveto)
                    else:
                        pass
                    landing_html = get_html(
                        chapter_url, 
                        # dump = '/tmp/%s-1.html' % chapter_id
                    )
                    landing_data = html_scraper(
                        landing_html, 
                        **xpath_viewer_display,
                        uniq=True
                    )
                    chapter_tally = int(landing_data['text_total'][0])
                    if len(chapter_downloaded) < chapter_tally:
                        for pg_i in range(1, chapter_tally + 1):
                            # page_next_xpath = xpath_view_pgnext.format(
                            #     chapter = chapter_id, 
                            #     page = pg_i
                            # )
                            # page_next_xpath = xpath_viewer_display['src'][0]
                            page_uri = '{chapter}/{page}'.format(
                                chapter = chapter_url.strip('/'), 
                                page    = pg_i
                            )
                            page_id = '%s_%s' % (chapter_id, pg_i)
                            if mdex_db is not None:
                                db_view = mdex_db.run(
                                    table=table_id, 
                                    mode='select row', 
                                    view=page_id
                                )
                            else:
                                db_view = ()
                            if len(db_view) == 0:
                                page_imgsrc = None
                                page_retry  = 0
                                while page_imgsrc is None:
                                    page_retry += 1
                                    if pg_i == 1:
                                        page_data = landing_data
                                    else:
                                        page_html = get_html(
                                            page_uri, 
                                            # dump = '/tmp/%s-%s.html' % (chapter_id, pg_i)
                                        )
                                        page_data = html_scraper(
                                            # mdex_visual.read(wait = randint(7, 11)), 
                                            page_html, 
                                            **xpath_viewer_display, 
                                            uniq=True
                                        )
                                    if len(page_data['src']) > 0:
                                        page_imgsrc = page_data['src'][0]
                                    else:
                                        if page_retry < 3:
                                            print_log('debug', 'Could not found any image in Page: "%s" Try [%s/3]', page_uri, page_retry)
                                        else:
                                            print_log('error', 'Could not found any image in Page: "%s" after [%s/3] Tries', page_uri, page_retry)
                                            exit()
                                        page_imgsrc = None
                                        countdown(
                                            console_args.wait, 
                                            txt = 'Retry "%s" in:' % page_uri)
                                page_saveas = os.path.join(
                                    page_saveto, 
                                    chapter_page_format.format(
                                        series  = series_id,
                                        chapter = chapter_no,
                                        page_num  = pg_i,
                                        link_name = page_imgsrc.rsplit('/', 1)[-1]
                                    )
                                )
                                page_stat = mdex_cloudflr.download(
                                    page_imgsrc, 
                                    page_saveas, 
                                    refer=page_uri
                                )
                                if page_stat['ok']:
                                    print_log(
                                        'success', 
                                        'DOWNLOAD [%s] Src: "%s", SaveAs: "%s" (%s)', 
                                        page_stat['info'].upper(), 
                                        page_imgsrc, 
                                        page_saveas, 
                                        page_stat['size'])
                                    if mdex_db is not None:
                                        mdex_db.run(
                                            table=table_id,   
                                            mode='insert row', 
                                            view=page_id, 
                                            save=page_saveas)
                                    else:
                                        pass
                                else:
                                    print_log(
                                        'error', 
                                        'DOWNLOAD FAILED [%s] Url: "%s", Src: "%s", SaveAs: "%s" (%s)', 
                                        page_stat['info'].upper(), 
                                        page_uri, 
                                        page_imgsrc, 
                                        page_saveas,
                                        page_stat['size'])
                            else:
                                print_log('debug', 'SKIPCH "%s" Page: "%s", DB: %s', chapter_folder, page_uri, len(db_view))
                            # fix chaptergaps problems, maybe, nope, problem remains
                            # print_log('debug', 'CLICK2 "%s" Page: [%s]', chapter_folder, pg_i + 1)
                            # viewer_pgnext = mdex_visual.driver.find_elements_by_xpath(
                            #     xpath_viewer_display['href'])
                            # ActionChains(mdex_visual.driver).move_to_element_with_offset(
                            #     viewer_pgnext[0], 15, 31).click().perform()
                    else:
                        print_log('debug', 'SKIPCH "%s" Url: "%s" %s: %s/%s Pages Downloaded\n', chapter_folder, chapter_url, chapter_folder, len(chapter_downloaded), chapter_tally)
                        if console_args.lazy:
                            print_log('debug', 'SKIPSR "%s" Series Url: "%s" Lazy.', mdex_save_dir, series_url)
                            skip_series = True
                            break
                        else:
                            pass
                else:
                    print_log('warn', 'IGNORE {title} "{href}" ({data-chapter}) {text_title} {text_group}\n'.format(**chapter_data))
                    pass
            if console_args.lazy and skip_series:
                break
            else:
                pass
    else:
        pass
