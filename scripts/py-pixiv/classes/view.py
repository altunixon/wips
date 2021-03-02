
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

def pix_get_image(pix_view_urls, pix_meta_data):
    global pix_browser
    # print (pix_view_urls, pix_meta_data)
    errors_count = 0
    for pix_href in pix_view_urls:
        pix_saveas =  os.path.join(pix_meta_data['saveto'], pixiv_savename(pix_href, **pix_meta_data))
        save_name_old = os.path.join(
            pix_meta_data['saveto'], 
            '{0}_{1}'.format(pix_meta_data['userid'], 
                pix_href.strip('/').rsplit('/', 1)[-1]) if \
                pix_meta_data['userid'] is not None else \
                pix_href.strip('/').rsplit('/', 1)[-1]
        )
        if os.path.isfile(save_name_old):
            move_oldfile(save_name_old, pix_saveas, keep=True)
        else:
            dl_status = pix_browser.download(pix_href, pix_saveas, refer=pix_meta_data['refer'])
            if not dl_status['ok']:
                errors_count += 1
            else:
                pass
            countdown(gen_randwait(console_args.wait_time), txt='Wait before processing next Image')
    return {'save': pix_saveas, 'error': errors_count}

# https://www.pixiv.net/member.php?id=37227739
def pix_get_multi(pix_view_urls, pix_meta_data):
    global pix_browser
    # print (pix_view_url, pix_view_hrefs)
    multi_errors_count = 0
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
                    dl_status = pix_get_image(
                        set([urlPrefixer(u, pixiv_fqdn) for u in pix_full_src]),
                        pix_meta_data
                    )
                else:
                    dl_status = {'save': None, 'error': 0}
                    pass
                multi_errors_count += dl_status['error']
        else:
            dl_status = {'save': None, 'error': 0}
            pass
    return {'save': dl_status['save'], 'error': multi_errors_count}

def get_view(pix_view_url, pix_save_to, **pix_view_meta):
    global console_args
    global pix_browser
    pix_view_refer = pix_view_meta.pop('refer', None)

    pix_browser.get(pix_view_url, ait=gen_randwait(console_args.wait_time))
    pix_presenter = lxml_spider(pix_browser.read(), refer=pix_view_refer, verbose=console_args.debug, uniq=True)

    pix_user_id = pix_view_meta.get('uid', None)
    try:
        pix_safe_uid = pixiv_userid(spider_checkattr(pix_user_id, pix_presenter, href=xpath_pview_userid))
    except:
        pix_browser.read(dump=console_args.dump_html)
        raise
    
    pix_view_id = pix_view_meta.pop('vid', None)
    if pix_view_id is None:
        pix_safe_vid = pixiv_viewid(pix_view_url)
    else:
        pix_safe_vid = pix_view_id

    pix_view_title = pix_view_meta.pop('title', None)
    pix_safe_title = string_sanitizer(spider_checkattr(pix_view_title, pix_presenter, text_title=xpath_pview_title))
    pix_meta = {
        'userid': pix_safe_uid, 
        'viewid': pix_safe_vid, 
        'title' : pix_safe_title \
            if pix_safe_title is not None \
            and len(pix_safe_title) > 0 \
            else 'null', 
        'saveto': pix_save_to, 
        'refer' : pix_view_url
    }
    if pix_safe_uid is not None and pix_safe_title is not None:
        for k, v in pix_meta.items():
            if v is None or len(v) == 0:
                print (json.dumps(pix_meta, indent=4, ensure_ascii=False))
                console_printer('debug', 'Debug Null Meta [%s]', k)
                raise Exception ('Null Meta Value [%s]' % k)
            else:
                pass
        pix_ismultipage = pix_presenter.scraper(text_seeall=xpath_pview_seeall)['text_seeall']
        pix_masked      = pix_presenter.scraper(text_masked=xpath_pview_btnshow)['text_masked']
        pix_originals   = pix_presenter.scraper(href=xpath_pview_image)['href']
        pix_gifzip      = pix_presenter.scraper(src=xpath_pview_gif)['src']
    else:
        # hotfix for purged images
        return False

    console_printer('debug', 'VIEW# [READ] - Url: "%s"\n\tMulti :%s,\n\tMasked:%s\n\tSingle:%s,\n\tZip   :%s', pix_view_url, pix_ismultipage, pix_masked,pix_originals, pix_gifzip)
    # isnew_multipage = True if len(pix_ismultipage) > 0 else False
    # print (pix_masked)
    # print (pix_originals, pix_ismultipage, pix_gifzip)
    get_set_url = lambda x: [urlPrefixer(u, pixiv_fqdn) for u in x]
    view_status = {'error': None, 'save': None}
    # GET MULTI (type See All)
    if len(pix_ismultipage) > 0:
        console_printer(
            'debug', 
            'VIEWM [GET#] - MultiPage "%s" %s', 
            pix_view_url, 
            pix_ismultipage
        )
        # CLICK MULTIPAGE "SEE ALL", IGNORE "SHOW"
        pix_browser.dom_click(xpath_pview_seeall, meltdown=True, desc="MULTIVIEW")
        countdown(
            gen_randwait(console_args.wait_time), 
            txt = 'Wait for Multipage to load')
        show_obscured(show=True, meltdown=False)
        pix_seeall_html = pix_browser.read()
        pix_seeall_view = lxml_scraper(
            pix_seeall_html, 
            href=xpath_pview_image,
            uniq=True,
            verbose=console_args.debug,
        )['href']
        if len(pix_seeall_view) > 0:
            # Eliminate View Dupications
            pix_originals = [i for i in pix_originals if i not in pix_seeall_view]
            console_printer('debug', 'VIEWM [GET#] - Url: "%s" Downloading New Multipage (%s)', pix_view_url, len(pix_seeall_view))
            # print (pix_meta)
            # print (json.dumps(pix_meta, indent=4, ensure_ascii=False))
            view_status = pix_get_image(
                get_set_url(pix_seeall_view),
                pix_meta
            )
        else:
            console_printer('debug', 'VIEWM [#404] - Multipage View "%s" could not find any img-original links, maybe increase wait time?', pix_view_url)
    else:
        pass
    # GET MASKED Type "manga" ?
    scripted_src = lambda x: x.split(' = ', 1)[-1].replace('\\', '').stri('"').strip("'")
    if len(pix_masked) > 0:
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
                pix_meta
            )
        else:
            pass
        # member_illust.php?mode=manga
        for pix_masked_reader in pix_masked_view_multi:
            pix_masked_show = urlPrefixer(pix_masked_reader, pixiv_fqdn)
            #pix_meta['refer'] = pix_masked_show
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
                pix_meta['refer'] = pix_masked_show
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
                            pix_meta
                        )
                    else:
                        pass
            elif len(pix_masked_multipage) > 0:
                # Referrer has not changed
                #pix_meta['refer'] = pix_masked_show
                console_printer('debug', 'VIEWM [MASK] - Url: "%s" is MultiPage (%s)', pix_view_url, len(pix_masked_multipage))
                view_status = pix_get_multi(
                    [pix_masked_show],
                    pix_meta
                )
            else:
                console_printer('warn', 'VIEWU [MASK] - Url: "%s" Has unknown type, Refer: "%s"', pix_view_url, pix_meta['refer'])
                pass
            #dump_html(pix_browser.driver.page_source, '/tmp/masked.html')
    else:
        pass
    # GET IMAGE Original
    if len(pix_originals) > 0:
        console_printer('debug', 'VIEWI [ORIG] - GET ImageBig %s', pix_originals)
        view_status = pix_get_image(
            get_set_url(pix_originals),
            pix_meta
        )
    else:
        pass
    # GET GIF
    if len(pix_gifzip) > 0:
        console_printer('debug', 'VIEWI [UGOI] - GET Gif %s', pix_gifzip)
        ugoira_meta_url = "{site}/ajax/illust/{viewid}/ugoira_meta".format(
            site    = pixiv_fqdn,
            viewid  = pix_meta['viewid']
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
        view_status = pix_get_image(ugoira_file_zip, pix_meta)
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
