#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, json, configparser, re
import argparse
from argparse           import RawTextHelpFormatter
from os                 import path
from os                 import name as os_name
from collections        import namedtuple
from urllib.parse       import unquote, urlsplit, urlencode

from browsers.selenium  import SeleniumBrowser
from browsers.scrapers  import lxml_scraper, lxml_spider, dump_html
from helpers.misc       import db_init, wrapper_listfile, print_log, print_color, countdown
from helpers.str_helper import urlPrefixer, arr2str, string_sanitizer

from vars.conf_pixiv    import *
from classes.checks     import dlcheck
from classes.home       import pixiv_homepage
from classes.index      import pixiv_index
from classes.utils      import pixiv_userid, pixiv_viewid, pixiv_savename, \
    gen_artistname, get_urivalue, gen_randwait, spider_checkattr, move_oldfile

def show_obscured(**options):
    global pix_browser
    click_meltdown = options.pop('meltdown', False)
    click_show = options.pop('show', False)
    try:
        if click_show:
            pix_browser.dom_click(xpath_pview_btnshow, meltdown=False, wait=1)
        else:
            pass
        if pix_browser.dom_click(xpath_pview_tutorial1, meltdown=False, wait=1):
            pix_browser.dom_click(xpath_pview_tutorial2, meltdown=False, wait=1)
        else:
            pass
        return True
        # return self.dom_click(xpath_pview_btnshow, meltdown=click_meltdown, wait=1)
    except Exception as excp:
        print_log('err', 'CLICK [EXCP] - Obscure Click Exception:\n%s\nFrom: obscure_click()', repr(excp))

def pix_get_image(pix_view_urls, pix_dlmeta_data):
    global pix_browser
    # print (pix_view_urls, pix_dlmeta_data)
    success_count = errors_count = 0
    for pix_href in pix_view_urls:
        pix_saveas =  path.join(pix_dlmeta_data['saveto'], pixiv_savename(pix_href, **pix_dlmeta_data))
        save_name_old = path.join(
            pix_dlmeta_data['saveto'], 
            '{0}_{1}'.format(pix_dlmeta_data['userid'], pix_href.strip('/').rsplit('/', 1)[-1])
        )
        if path.isfile(save_name_old):
            move_oldfile(save_name_old, pix_saveas, keep=True)
            success_count += 1
        else:
            dl_status = pix_browser.download(pix_href, pix_saveas, refer=pix_dlmeta_data['refer'])
            if not dl_status['ok']:
                errors_count += 1
            else:
                success_count += 1
            countdown(gen_randwait(console_args.wait_time), txt='Wait before processing next Image')
    return {'save': pix_saveas, 'error': errors_count, 'done': success_count}

# https://www.pixiv.net/member.php?id=37227739
def pix_get_multi(pix_view_urls, pix_dlmeta_data):
    global pix_browser
    # print (pix_view_url, pix_view_hrefs)
    multi_done_count = multi_errors_count = 0
    for pix_href in pix_view_urls:
        pix_browser.get(pix_href, wait=gen_randwait(console_args.wait_time))
        pix_full_view = lxml_scraper(
            pix_browser.read(), 
            href=xpath_pview_mfull, 
            uniq=True,
            refer=pix_href, 
            verbose=console_args.debug
        )['href']
        if len(pix_full_view) > 0:
            for p in pix_full_view:
                pix_view = urlPrefixer(p, pixiv_fqdn)
                pix_browser.get(pix_view, wait=gen_randwait(console_args.wait_time))
                pix_full_src = lxml_scraper(
                    pix_browser.read(), 
                    src=xpath_pview_msrc, 
                    refer=pix_view, 
                    uniq=True, 
                    verbose=console_args.debug
                )['src']
                # print (pix_full_src)
                if len(pix_full_src) > 0:
                    dl_status = pix_get_image(set([urlPrefixer(u, pixiv_fqdn) for u in pix_full_src]), pix_dlmeta_data)
                else:
                    dl_status = {'save': None, 'error': 0, 'done': 0}
                multi_errors_count += dl_status['error']
                multi_done_count += dl_status['done']
        else:
            dl_status = {'save': None, 'error': 0}
    return {'save': dl_status['save'], 'error': multi_errors_count, 'done': multi_done_count}

def get_view(pix_view_url, pix_save_to, **pix_view_meta):
    global console_args
    global pix_browser
    pix_view_status = namedtuple('GetViewResult', ['ok', 'saveas', 'done', 'total', 'ismulti', 'lastimg', 'purged'])
    pix_view_refer = pix_view_meta.get('refer', None)

    pix_browser.get(pix_view_url, ait=gen_randwait(console_args.wait_time))
    pix_presenter = lxml_spider(pix_browser.read(), refer=pix_view_refer, verbose=console_args.debug, uniq=True)

    pix_user_id = pix_view_meta.get('uid', None)
    try:
        pix_safe_uid = pixiv_userid(spider_checkattr(pix_user_id, pix_presenter, href=xpath_pview_userid))
    except Exception as excp:
        pix_browser.read(dump=console_args.dump_html)
        raise excp
    
    pix_view_id = pix_view_meta.get('vid', None)
    if pix_view_id is None:
        pix_safe_vid = pixiv_viewid(pix_view_url)
    else:
        pix_safe_vid = pix_view_id

    pix_view_title = pix_view_meta.get('title', None)
    pix_safe_title = string_sanitizer(spider_checkattr(pix_view_title, pix_presenter, text_title=xpath_pview_title))
    pix_dlmeta = {
        'userid': pix_safe_uid, 
        'viewid': pix_safe_vid, 
        'title' : pix_safe_title if \
            pix_safe_title is not None and \
            len(pix_safe_title) > 0 else \
            'null', 
        'saveto': pix_save_to, 
        'refer' : pix_view_url
    }
    return_dict = {'ok': False, 'saveas': None, 'done': 0, 'error': 0, 'total': 0, 'ismulti': True, 'lastimg': 0, 'purged': False}
    if pix_safe_uid is not None and pix_safe_title is not None:
        for k, v in pix_dlmeta.items():
            assert v is not None, console_printer('debug', 'Debug Meta [%s] is NUL', k, asstring=True)
            assert len(v) > 0, console_printer('debug', 'Debug Meta [%s] is an empty string len() == 0', k, asstring=True)
        pix_ismultipage = pix_presenter.scraper(text_seeall=xpath_pview_seeall)['text_seeall']
        pix_masked      = pix_presenter.scraper(text_masked=xpath_pview_btnshow)['text_masked']
        pix_originals   = pix_presenter.scraper(href=xpath_pview_image)['href']
        pix_gifzip      = pix_presenter.scraper(src=xpath_pview_gif)['src']
    else:
        # hotfix for purged images
        return_dict['purged'] = True
        return pix_view_status(**return_dict)

    console_printer('debug', 'VIEW# [READ] - Url: "%s"\n\tMulti :%s,\n\tMasked:%s\n\tSingle:%s,\n\tZip   :%s', 
        pix_view_url, pix_ismultipage, pix_masked,pix_originals, pix_gifzip)
    # isnew_multipage = True if len(pix_ismultipage) > 0 else False
    # print (pix_masked)
    # print (pix_originals, pix_ismultipage, pix_gifzip)
    get_set_url = lambda x: [urlPrefixer(u, pixiv_fqdn) for u in x]
    view_status = {'error': None, 'save': None}
    # GET MULTI (type See All)
    if len(pix_ismultipage) > 0:
        return_dict['ismulti'] = True
        console_printer('debug', 'VIEWM [GET#] - MultiPage "%s" %s', pix_view_url, pix_ismultipage)
        # CLICK MULTIPAGE "SEE ALL", IGNORE "SHOW"
        pix_browser.dom_click(xpath_pview_seeall, meltdown=True, desc="MULTIVIEW")
        countdown(gen_randwait(console_args.wait_time), txt='Wait for Multipage to load')
        show_obscured(show=True, meltdown=False)
        pix_seeall_html = pix_browser.read()
        pix_seeall_view = lxml_scraper(pix_seeall_html, href=xpath_pview_image, uniq=True, verbose=console_args.debug)['href']
        pix_seeall_count = len(pix_seeall_view)
        if pix_seeall_count > 0:
            # Eliminate View Dupications
            pix_originals = [i for i in pix_originals if i not in pix_seeall_view]
            console_printer('debug', 'VIEWM [GET#] - Url: "%s" Downloading New Multipage (%s)', pix_view_url, len(pix_seeall_view))
            # print (pix_dlmeta)
            # print (json.dumps(pix_dlmeta, indent=4, ensure_ascii=False))
            view_status = pix_get_image(get_set_url(pix_seeall_view), pix_dlmeta)
            return_dict['saveas'] = view_status['saveas']
            return_dict['done'] += view_status['done']
            return_dict['error'] += view_status['error']
            return_dict['total'] += pix_seeall_count
            return_dict['lastimg'] = '_p%s.' % (pix_seeall_count - 1)
            return_dict['purged'] = False
        else:
            console_printer('debug', 'VIEWM [#404] - Multipage View "%s" could not find any img-original links, maybe increase wait time?', pix_view_url)
    else:
        return_dict['ismulti'] = False
    # GET MASKED Type "manga" ?
    scripted_src = lambda x: x.split(' = ', 1)[-1].replace('\\', '').stri('"').strip("'")
    if len(pix_masked) > 0:
        return_dict['ismulti'] = True
        console_printer('debug', 'VIEW0 [MASK] - Url: "%s" [%s]', pix_view_url, pix_masked)
        if pix_browser.dom_click(xpath_pview_btnshow, hover=False, meltdown=False, desc="MASKED"):
            show_obscured(show=False, meltdown=False)
        else:
            console_printer('warn', 'VIEW0 [MASK] - Url: "%s" [%s], Attempt to Click masked view Failed, reloading Page', pix_view_url, pix_masked)
            pix_browser.driver.refresh()
            countdown(console_args.wait_time, txt='Loading Refreshed Page in:')
            console_printer('debug', 'VIEW0 [NSFW] - Url: "%s" [%s]', pix_view_url, pix_masked)
            show_obscured(show=True, meltdown=True)
            # pix_browser.dom_click(xpath_pview_btnshow, meltdown=True)
        countdown(gen_randwait(console_args.wait_time), txt = 'Loading Masked Gallery')
        
        # REVEALED ITEMS
        pix_masked_html = pix_browser.read()
        pix_masked_view_multi = lxml_scraper(
            pix_masked_html, 
            href=xpath_pview_maskm, # Masked is Multi member_illust.php?mode=manga
            uniq=True,
            verbose=console_args.debug,
        )['href']
        pix_masked_view_single= lxml_scraper(
            pix_masked_html, 
            href=xpath_pview_image, # Masked is Single img-original
            uniq=True,
            verbose=console_args.debug,
        )['href']
        console_printer(
            'debug', 
            'VIEW1 [MASK] - Masked Single: [%s], Multi: [%s]', 
            len(pix_masked_view_single), 
            len(pix_masked_view_multi)
        )

        if len(pix_masked_view_single) > 0:
            console_printer('debug', 'VIEW1 [MASK] - Url: "%s" is SinglePage %s', pix_view_url, pix_masked_view_single)
            view_status = pix_get_image(
                lxml_scraper(
                    pix_browser.read(), 
                    href=xpath_pview_image,
                    verbose=console_args.debug,
                    uniq=True
                )['href'],
                pix_dlmeta
            )
        else:
            pass
        # member_illust.php?mode=manga
        for pix_masked_reader in pix_masked_view_multi:
            pix_masked_show = urlPrefixer(pix_masked_reader, pixiv_fqdn)
            #pix_dlmeta['refer'] = pix_masked_show
            pix_browser.get(pix_masked_show, wait=console_args.wait_time)
            show_obscured(show=True, meltdown=True)
            pix_masked_gallery = lxml_scraper(
                pix_browser.read(), 
                text_script=xpath_pview_script,
                href=xpath_pview_mfull,
                verbose=console_args.debug,
                uniq=True
            )
            pix_masked_scripts   = pix_masked_gallery['text_script']
            pix_masked_multipage = pix_masked_gallery['href']
            if len(pix_masked_scripts) > 0:
                pix_dlmeta['refer'] = pix_masked_show
                console_printer('debug', 'VIEWW [MASK] - Url: "%s" is Swiper (%s)', pix_view_url, len(pix_masked_scripts))
                for pix_masked_src in pix_masked_scripts:
                    # print (pix_masked_src)
                    pix_masked_orig=[
                        scripted_src(i) for \
                        i in pix_masked_src.split(';') if \
                        i.startswith('pixiv.context.originalImages') and \
                        '/img-original' in i
                    ]
                    if len(pix_masked_orig) > 0:
                        view_status = pix_get_image(
                            pix_masked_orig,
                            pix_dlmeta
                        )
                    else:
                        pass
            elif len(pix_masked_multipage) > 0:
                # Referrer has not changed
                #pix_dlmeta['refer'] = pix_masked_show
                console_printer('debug', 'VIEWM [MASK] - Url: "%s" is MultiPage (%s)', pix_view_url, len(pix_masked_multipage))
                view_status = pix_get_multi([pix_masked_show], pix_dlmeta)
            else:
                console_printer('warn', 'VIEWU [MASK] - Url: "%s" Has unknown type, Refer: "%s"', pix_view_url, pix_dlmeta['refer'])
            #dump_html(pix_browser.driver.page_source, '/tmp/masked.html')
    else:
        pass
    # GET IMAGE Original
    if len(pix_originals) > 0:
        console_printer('debug', 'VIEWI [ORIG] - GET ImageBig %s', pix_originals)
        view_status = pix_get_image(
            get_set_url(pix_originals),
            pix_dlmeta
        )
    else:
        pass
    # GET GIF
    if len(pix_gifzip) > 0:
        console_printer('debug', 'VIEWI [UGOI] - GET Gif %s', pix_gifzip)
        ugoira_meta_url = "{site}/ajax/illust/{viewid}/ugoira_meta".format(
            site    = pixiv_fqdn,
            viewid  = pix_dlmeta['viewid']
        )
        # print (ugoira_meta_txt)
        ugoira_meta_txt = pix_browser.read(ugoira_meta_url, wait=3)
        # print (ugoira_meta_txt)
        #dump_html(ugoira_meta_txt, '/tmp/meta.html')
        if ugoira_meta_txt.startswith('<'):
            if '{' in ugoira_meta_txt:
                ugoira_meta_dat = json.loads(
                    lxml_scraper(
                        ugoira_meta_txt, 
                        text_json = xpath_pview_ugoira, 
                        verbose = console_args.debug
                    )['text_json'][0]
                )
                ugoira_file_zip = [ugoira_meta_dat['body']['originalSrc']]
            else:
                ugoira_file_lst = [
                    u.strip('"') \
                    for u in lxml_scraper(
                        ugoira_meta_txt, 
                        #text_json='//body/pre',
                        text_objbox = xpath_pview_zipmeta, 
                        verbose = console_args.debug
                    )['text_objbox'] \
                    if "ugoira" in u
                ]
                # print (ugoira_file_lst)
                ugoira_file_zip = [ugoira_file_lst[-1]] \
                    if len(ugoira_file_lst) > 1 \
                    else ugoira_file_lst
        else:
            ugoira_meta_dat = json.loads(ugoira_meta_txt)
            ugoira_file_zip = [ugoira_meta_dat['body']['originalSrc']]
        #ugoira_file_frames = [
        #    f['file'] for f in ugoira_meta_dat['body']['frames']
        #]
        view_status = pix_get_image(ugoira_file_zip, pix_dlmeta)
    else:
        pass
    # CHECK RESULTS
    if view_status['error'] is not None \
    and view_status['error'] == 0:
        console_printer('ok', 'VIEW# [DONE] - Url: "%s", SaveAs: "%s", Exit: %s\n', pix_view_url, view_status['save'], view_status['error'])
        if pix_database is not None:
            pix_database.run(
                mode = 'insert row', 
                table = pix_user_id \
                    if pix_user_id is not None \
                    else '_misc', 
                view = pix_view_id,
                save = view_status['save']
            )
        else:
            pass
        view_success = True
    else:
        console_printer('err', 'VIEW# [FAIL] - Url: "%s", SaveAs: "%s", Exit: %s\n', pix_view_url, view_status['save'], view_status['error'])
        view_success = False
    return view_success

def pix_main(urls):
    global console_args, console_color
    global pix_browser, pix_database, pix_cookies
    pix_home.login(meltdown=True)
    pix_browser.dom_click(xpath_pindex_newspop, meltdown=False, desc="Close Update Notification")

    raw_urls = [] if urls is None else urls
    if console_args.url_file is not None:
        if ':' in console_args.url_file:
            book_type, book_file = console_args.url_file.split(':', 1)
            list_cache = wrapper_listfile(book_file, forcerw=True)
            # print (book_type, book_file)
            book_current = pix_home.list_following(
                book_type, 
                reverse = False, 
                limit = console_args.following_limit, 
                description = True
            )
            # print (book_current)
            book_cache = list_cache.read()
            raw_urls.extend([x for x in book_current if not x.startswith('#')])
            if len(book_cache) > 0:
                print (len(book_cache), 'not Dump', book_file, json.dumps(book_cache, indent=4))
                raw_urls.extend([u.strip() for u in book_cache if not u.startswith('#') and len(u.strip()) > 0])
                list_cache.upsert(book_current)
            else:
                list_cache.upsert(book_current)
                print ('Dumping:', len(book_current), book_file)
                list_cache.dump()
        else:
            book_file = console_args.url_file
            if book_file != 'private' and book_file != 'public' and path.isfile(book_file):
                list_cache = wrapper_listfile(book_file, forcerw=True)
                raw_urls.extend([u.strip() for u in list_cache.read() if not u.startswith('#') and len(u.strip()) > 0])
            else:
                raw_urls.extend(pix_home.list_following(book_file, reverse=False, limit=console_args.following_limit))
                list_cache = None
                # list_cache.insert(book_file, raw_urls)
    else:
        list_cache = None
        if len(raw_urls) == 0:
            raw_urls.extend(pix_home.list_following('private', reverse=False, limit=console_args.following_limit))
        else:
            pass
    # print (len(raw_urls), raw_urls)
    #exit()
    try:
        # Pre-run Check
        index_chckd = set([])
        if len(raw_urls) > 0:
            for one_url in raw_urls:
                get_errors = 0
                if config_seperator in one_url:
                    parsed_url  = one_url.split(config_seperator, 1)[0].strip()
                    save_path   = path.normpath(one_url.rsplit(config_seperator, 1)[1].strip())
                else:
                    parsed_url  = one_url.strip()
                    save_path   = path.normpath(console_args.saveto)

                # https://www.pixiv.net/member_illust.php?mode=medium&illust_id=56956592
                if pixiv_post_identifier in one_url:
                    save_misc = path.join(save_path, '_misc') if \
                        not console_args.notree else \
                        save_path
                    if '_misc' not in index_chckd:
                        index_chckd.add('_misc')
                        pix_check.createnew('_misc', save_misc)
                    else:
                        pass
                    v_id    = pixiv_viewid(one_url)
                    v_url   = pixiv_illust_view.format(vid=v_id)
                    v_check = pix_check.view('_misc', v_id)
                    if v_check.skip:
                        console_printer('info', 'VIEW# [SKIP] - Url: "%s", DB _misc: %s', v_url, len(v_check.data))
                        view_ok = True
                    else:
                        view_ok = get_view(v_url, save_misc, title=None, uid=None, vid=v_id)
                    if not view_ok:
                        get_errors += 1
                    else:
                        pass
                    pix_available = True
                else:
                    #pix_url = pixiv_illust_index + parsed_url if \
                    #    parsed_url.isdigit() else \
                    if pixiv_index_identifier in parsed_url:
                        pix_id = pixiv_userid(parsed_url)
                    else:
                        pix_id = parsed_url
                    pix_url = pixiv_illust_index.format(uid=pix_id)
                    pix_landing_html = pix_browser.read(pix_url, wait=console_args.wait_time)
                    pix_landing = pixiv_index(pix_url, pix_landing_html, verbose=console_args.debug, color=console_color)
                    pix_clickable = pix_browser.dom_click(xpath_pindex_seeall, meltdown=False, desc="Reveal Indexes")
                    pix_available = all(pix_landing.available() and pix_clickable)
                    if pix_available:
                        countdown(console_args.wait_time, txt='Revealing Artworks in')
                        # print ('REVEAL', pix_browser.driver.current_url)
                        # pix_landing_html = pix_browser.read(reload=True)
                        pix_uid = pix_landing.uid
                        if not console_args.notree:
                            index_savedir = '{uid}_{mname}'.format(uid=pix_uid, mname=pix_landing.userhp())
                            save_index = path.normpath(path.join(save_path, index_savedir))
                        else:
                            save_index = path.normpath(save_path)
                        # print (save_index)
                        if pix_uid not in index_chckd: # create table if not exists
                            index_chckd.add(pix_uid)
                            pix_check.createnew(pix_uid, save_index)
                        else:
                            pass

                        current_url = pix_url = pix_browser.driver.current_url
                        # print (current_url, pix_url, pix_browser.driver.current_url)
                        processed_indexes = set([])
                        current_skip = False
                        while current_url is not None:
                            processed_indexes.add(current_url)
                            current_url = urlPrefixer(current_url, pixiv_fqdn) # JANKY AF
                            if current_url == pix_url:
                                pix_index = pix_landing
                            else:
                                pix_browser.get(current_url, wait=console_args.wait_time)
                                pix_index = pixiv_index(current_url, pix_browser.read(), uid=pix_uid)
                            # LAZY
                            current_viewport = pix_index.views()
                            if pix_database is not None:
                                v_check_all = pix_check.views(pix_index.uid, current_viewport.views)
                            else:
                                v_check_all = pix_check.vchecks_null
                            # print (json.dumps(current_viewport._asdict(), indent=4, ensure_ascii=False, sort_keys=True))    
                            if not v_check_all.skip:
                                console_printer('info', 'INDEX [INFO] - Url: "%s" %s: [%s/%s]', 
                                    current_url, pix_index.uid, v_check_all.done, v_check_all.total)
                                # NAVIGATING CURRENT VIEWS
                                for v_data in current_viewport.views:
                                    # print (json.dumps(v_data, indent=4, ensure_ascii=False, sort_keys=True))
                                    v_href = v_data['href'][0]
                                    v_id = pixiv_viewid(v_href)
                                    # v_url = urlPrefixer(v_href, pixiv_fqdn)
                                    v_url = pixiv_illust_view.format(vid=v_id)
                                    if pix_database is None:
                                        if console_args.lazy_skip:
                                            # from glob import glob > glob('{path}/{uid}_{vid}_p*.*'.format())
                                            v_check = pix_check.glob_glob(save_index, pix_index.uid, v_id, lastimg=1)
                                        else:
                                            v_check = pix_check.vcheck_null
                                    else:
                                        if current_viewport.count_multipage > 0 and v_href in current_viewport.multipage:
                                            console_printer('debug', 'VIEW# [MULT] - Url: "%s"', v_url)
                                            if console_args.lazy_skip:
                                                # check the first? last? image in multipage (the _pXX part)
                                                v_check = pix_check.bypass(pix_index.uid, v_id)
                                            else:
                                                v_check = pix_check.view(pix_index.uid, v_id)
                                        else:
                                            console_printer('debug', 'VIEW# [SNGL] - Url: "%s"', v_url)
                                            v_check = pix_check.view(pix_index.uid, v_id)
                                    if v_check.skip:
                                        console_printer('info', 'VIEW# [SKIP] - Url: "%s", %s: [%s]', v_url, pix_index.uid, v_check.done)
                                        view_ok = True
                                        if console_args.lazy_skip:
                                            console_printer('info', 'INDEX [LAZY] - Url: "%s", Break at View: "%s" Found[%s]', current_url, v_url, v_check.done)
                                            current_skip = True
                                            break
                                    else:
                                        # PORTING? KEEP
                                        view_ok = get_view(
                                            v_url, 
                                            save_index,
                                            title = v_data['text_title'][0] \
                                                if len(v_data['text_title']) > 0 \
                                                else None,
                                            uid = pix_index.uid, 
                                            vid = v_id
                                        )
                                    if not view_ok:
                                        get_errors += 1
                                    else:
                                        pass
                                # END VIEWS
                            else:
                                console_printer('debug', 'INDEX [SKIP] - Url: "%s" %s: [%s/%s]', 
                                    current_url, pix_index.uid, v_check_all.done, v_check_all.total)
                                if console_args.lazy_skip:
                                    current_skip = True
                            # END PORT
                            current_url = pix_index.nextpg(pool=processed_indexes) \
                                if len(current_viewport.views) > 0 and not current_skip \
                                else None
                            if current_url is not None:
                                countdown(console_args.wait_time, txt='Next: "%s"' % current_url)
                                console_printer('debug', 'INDEX [NEXT] - Url: "%s".', current_url)
                            else:
                                pass
                        console_printer('info', 'PIXIV [DONE] - User ID (%s) Download Completed: "%s"', pix_id, one_url)
                    else:
                        console_printer('warn', 'PIXIV [#404] - User ID (%s) Has been Purged: "%s"', pix_id, one_url)
                        pass
                countdown(gen_randwait(console_args.wait_time * 2), txt='Next Link in: ')
                if list_cache is not None and get_errors == 0:
                    #list_cache.comment(one_url)
                    list_cache.comment(one_url, comment='#' if pix_available else '# 404 USER #')
                    list_cache.check_dump()
                else:
                    pass
            pix_browser.save_cookies(pix_cookies)
        else:
            console_printer('error', 'INDEX [NOTF] - No url nor existing url list file supplied.\n%s', vars(console_args))
        if list_cache is not None:
            list_cache.close()
        else:
            pass
    except Exception as excp:
        if list_cache is not None:
            list_cache.close()
        else:
            pass
        raise excp
        # countdown(999)

#-------------------------------------------------------------------------------

# CALLING MAIN
if __name__ == "__main__":
    
    myerrs = 0
    default_path= path.dirname(path.abspath(sys.argv[0]))
    script_name = path.basename(sys.argv[0]).split('.',1)[0].strip()
    
    parser = argparse.ArgumentParser(
        description='Download URL',
        argument_default=argparse.SUPPRESS, formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        dest='url_list', nargs='*', default=None, 
        help='an URL for the accumulator')
    parser.add_argument(
        '-f', '--list-file', dest='url_file', nargs='?', default=None, help='List file')
    parser.add_argument(
        '-c', '--config', dest='conf_file', nargs='?', default=None, 
        help='Configuration INI File, Currently just Used for Login Credentials')
    parser.add_argument(
        '--credential', dest='user_pass', nargs='?', default=None, 
        help='Credential in format Username:Password, takes precedent over [--config]')
    parser.add_argument(
        '-d', '--database', dest='database', nargs='?', default=None, 
        help='Database Connector-string, Default=None provide no database storage')
    parser.add_argument(
        '-o', '--out-path', dest='saveto', nargs='?', default=path.join(default_path, 'downloads'), 
        help='Download to folder')
    parser.add_argument(
        '--nt', '--notree', dest='notree', action='store_true', 
        help='Download directlyto output folder, do not add artist folder')
    parser.set_defaults(notree=False)
    parser.add_argument(
        '-r', '--re-download', dest='re_download', action='store_true', 
        help='Redownload if possible (file does not exists or can\'t be verified in dl path), ignore db file status')
    parser.set_defaults(re_download=False)
    parser.add_argument(
        '-n', '--page-number', dest='pages', nargs='?', default=None, 
        help='Download pages (ex: 1,4,9 / 1-4,9) apply to all url, overwritten by url options')
    parser.add_argument(
        '-w', '--wait', dest='wait_time', nargs='?', type=int, default=7, 
        help='Sleep between Downloads, avoid soft-ban')
    parser.add_argument(
        '--captcha', dest='captcha_time', nargs='?', type=int, default=0, 
        help='Manual CAPTCHA Solving time')
    parser.add_argument(
        '--flimit', dest='following_limit', nargs='?', type=int, default=0, 
        help='Set following search limit, default=0, unlimited')
    parser.add_argument(
        '--check', dest='verify', action='store_true', 
        help='Force Verify image if file is not in db, default=do not verify if file exists in db or destination')
    parser.set_defaults(verify=False)
    parser.add_argument(
        '-q', '--quiet', dest='verbose', action='store_false', 
        help='Quiet, subdue all output print only essential info, disable delete corrupt prompt')
    parser.set_defaults(verbose=True)
    parser.add_argument(
        '-b', '--browser', dest='browser', nargs='?', default='chrome', 
        help='Browser type: default=chrome (via native chromewebdriver) use firefox if needed be.')
    parser.add_argument(
        '--driver', dest='driver', nargs='?', default=None, 
        help='WebDriver binary path, by default, selenium will uses whichever apropriate webdriver found in env PATH.')
    parser.add_argument(
        '-i', '--incognito', dest='incognito', action='store_true', 
        help='Use Private browsing')
    parser.set_defaults(incognito=False)
    parser.add_argument(
        '--hidden', dest='hide', action='store_true', 
        help='Hide browser window off-screen (needed for on focus load function of twatter).')
    parser.set_defaults(hide=False)
    parser.add_argument(
        '--headless', dest='headless', action='store_true', 
        help='Headless mode, untested.')
    parser.set_defaults(headless=False)
    parser.add_argument(
        '-z', '--lazy', dest='lazy_skip', action='store_true', 
        help='Lazy skip, if latest image is in db, check if last image is also downloaded, if yes, skip current url (uptodate).')
    parser.set_defaults(lazy_skip=False)
    parser.add_argument(
        '--cookies', dest='cookies', nargs='?', default=None, 
        help='Load custom cookies')
    parser.add_argument(
        '--window', dest='window_size', nargs='?', default='640x480', 
        help='Set browser window size: default=640x480')
    parser.add_argument(
        '--extension', dest='chrome_extension', nargs='?', default=None, 
        help='Chrome extension path, must contains manifest.js, check "/home/alt/.config/chromium/Default/Extensions" on linux. Ignored if browser type is not Chrome.')
    parser.add_argument(
        '--debug', dest='debug', action='store_true', 
        help='Debug mode, only skip single images, retries all multi image')
    parser.set_defaults(debug=False)
    parser.add_argument(
        '--dump', dest='dump_html', nargs='?', default=None, 
        help='Dump html content to file on error')
    
    console_args = parser.parse_args()
    console_color = True if os_name != 'nt' else False
    console_printer = print_color if console_color else print_log
    # Database
    pix_database = db_init(console_args.database)
    # Browser
    pix_browser = SeleniumBrowser(
        private     = console_args.incognito, 
        capability  = console_args.browser, 
        driverbin   = console_args.driver, 
        hide        = console_args.hide, 
        headless    = console_args.headless, 
        verify      = console_args.verify, 
        window      = console_args.window_size, 
        extension   = console_args.chrome_extension, 
        retry       = 2, 
        verbose     = console_args.verbose, 
        color       = console_color
    )
    default_cookies = path.join( default_path, 
        string_sanitizer( '{browser}_{inscript}_cookies.txt'.format( 
            inscript = script_name, 
            browser = pix_browser.capability
        ) ) )
    pix_cookies = console_args.cookies \
        if console_args.cookies is not None \
        else default_cookies
    
    pix_check = dlcheck(
        pix_database, 
        console_args.saveto, 
        verbose = console_args.verbose, 
        redl = console_args.re_download, 
        color = console_color
    )
    pix_home = pixiv_homepage(
        pix_browser, 
        config = console_args.conf_file, 
        credential = console_args.user_pass, 
        cookies = pix_cookies, 
        captcha = console_args.captcha_time, 
        wait = console_args.wait_time, 
        color = console_color
    )
    try:
        pix_main(console_args.url_list)
    except Exception as excp:
        if console_args.debug:
            input("Press Enter when youre ready...")
        raise excp
else:
    pass
