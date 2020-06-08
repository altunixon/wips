#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python modules
import os, sys, time, filetype, json
import argparse
from argparse                   import RawTextHelpFormatter
from random                     import randint
from urllib.parse               import unquote, urlsplit
from collections                import namedtuple
# Custom modules
from browsers.requests          import RequestsBrowser
from browsers.login             import site_login_req
from helpers.misc               import db_init, print_log, print_color, countdown, humanize_bytes
from helpers.str_helper         import urlPrefixer, arr2str, string_sanitizer
from helpers.dir_helper         import MkDirP
from helpers.text_file          import keyed_list
from vars.conf_booru            import naming_ifs, config_seperator, supported_sites

def wrapper_check_lazy(index_table, views_first, views_last, **options):
    global mech_dbchecks, my_printer
    refer_first = options.pop('urlfirst', None)
    refer_last  = options.pop('urllast', None)
    res_first = mech_dbchecks.views(views_first, index_table, verbose=False)
    if res_first.skip:
        if len(views_last) == 0:
            my_printer('debug', 
                'CHECK [LAZY] - NoSkip, First: "%s" [%s/%s] %s, Last: "%s" Unknown', 
                refer_first, res_first.count, len(views_first), res_first.skip, refer_last, 
            )
            return False
        else:
            res_last  = mech_dbchecks.views(
                views_last, index_table, verbose=False)
            if res_last.skip:
                my_printer('debug', 
                    'CHECK [LAZY] - SkipAll, First: "%s" [%s/%s] %s, Last: "%s" [%s/%s] %s', 
                    refer_first, res_first.count, len(views_first), res_first.skip, 
                    refer_last, res_last.count, len(views_last), res_last.skip, 
                )
                return True
            else:
                my_printer('debug', 
                    'CHECK [LAZY] - NoSkip, First: "%s" [%s/%s] %s, Last: "%s" [%s/%s] %s', 
                    refer_first, res_first.count, len(views_first), res_first.skip, 
                    refer_last, res_last.count, len(views_last), res_last.skip, 
                )
                return False
    else:
        my_printer('debug', 
            'CHECK [LAZY] - NoSkip, First: "%s" [%s/%s], Ignore Last "%s" (%spg)', 
            refer_first, res_first.count, len(views_first), len(views_last), refer_last, 
        )
        return False

def wrapper_prerun(download_table, path_save_current, path_save_old=None):
    global mech_database
    print ('DEBUG', path_save_current)
    MkDirP(path_save_current, old=path_save_old)
    if mech_database is not None:
        mech_database.run(
            mode='create table', 
            table=download_table, 
            view='VARCHAR(32) PRIMARY KEY', 
            save='TEXT NOT NULL'
        )
    else:
        pass

def do_post(view_url, save_path, table_name, **options):
    global console_args
    global mech_database
    global post_page
    global external_source
    view_dry = options.pop('dryrun', False)
    view_id = options.pop('id', None)
    if view_id is None or len(view_id) == 0:
        view_id = gen_viewid(view_url)
    else:
        pass
    post_images = post_page.get(view_url, id=view_id)
    if not view_dry:
        dlpost_returns = {
            'ok': False, 
            'success': 0, 
            'failed': 0, 
            'total': 0, 
            'code404': False
        }
        post_exsource = None
        n_max = len(post_images)
        if post_images is not None or n_max > 0:
            dlpost_returns['total'] = n_max
            my_printer('info', 
                'VIEW  [GET#] - Url: "%s", Id: "%s" (%s Imgs)', 
                view_url, view_id, n_max
            )
            for post_img in post_images:
                post_exsource = post_img.source
                image_saveas = os.path.join(
                    save_path, post_img.file
                )
                post_dlstat = mech_browser.download(
                    post_img.src, 
                    image_saveas,
                    refer   = view_url)
                print_log('ok', 
                    'IMAGE [DONE] - Src: "%s", Dst: "%s", Success [%s], Size [%s/%s], Info [%s]',
                    post_img.src, 
                    image_saveas, 
                    post_dlstat['ok'], 
                    post_dlstat['size'], 
                    humanize_bytes(post_dlstat['size']), 
                    post_dlstat['info'].upper(), 
                )
                if post_dlstat['ok']:
                    dlpost_returns['success'] += 1
                else:
                    dlpost_returns['failed'] += 1
            dlpost_result = namedtuple(
                'DownloadPost', list(dlpost_returns.keys())
            )
            if dlpost_returns['success'] >= dlpost_returns['total'] \
            and dlpost_returns['success'] > 0:
                my_printer('ok', 
                    'IMAGE [DONE] - Url: "%s" (%s Imgs)', 
                    view_url, dlpost_returns['success']
                )
                if mech_database is not None:
                    mech_database.run(
                        mode='insert row', 
                        table=table_name, 
                        view=view_id,
                        save=image_saveas
                    )
                else:
                    pass
                dlpost_returns['ok'] = True
            else:
                my_printer('error', 
                    'IMAGE [FAIL] - Url: "%s" (%s/%s Imgs)', 
                    view_url, dlpost_returns['success'], dlpost_returns['total']
                )
            if post_exsource is not None:
                external_source['{tag} {id}'.format(tag=table_name, id=view_id)] = post_exsource
            else:
                pass
        else:
            dlpost_returns['code404'] = True
            my_printer('error', 'VIEW  [#404] - Url: "%s"', view_url)
        return dlpost_result(**dlpost_returns)
    else:
        post_files = []
        for post_info in post_images:
            post_files.append({
                'src': post_info.src, 
                'saveas': post_info.saveas, 
            })
        return post_files



def main(page_url, path_workdir, page_config, **options):
    global console_args
    global mech_browser
    global mech_database, mech_dbchecks
    global mech_loggedin, index_page, post_page
    global my_printer

    page_tagname    = gen_tag(page_url, fifo=True)
    page_saveto     = os.path.join(path_workdir, page_tagname)
    wrapper_prerun(page_tagname, page_saveto)
    page_isdeviant  = True if 'deviantart.com' in page_config.fqdn else False

    # LOGIN
    if page_config.login is None \
    or page_config.fqdn in mech_loggedin:
        my_printer('debug', 'LOGIN [SKIP] - Site: "%s" Dont need to login again (%s).', page_config.fqdn, page_config.login)
    else:
        if site_login_req(mech_browser, **page_config.login):
            my_printer('debug', 'LOGIN [_OK_] - Site: "%s" Logged-in.', page_config.fqdn)
            mech_loggedin.add(page_config.fqdn)
        else:
            my_printer('debug', 'LOGIN [FAIL] - Site: "%s" Could not login with Credentials: %s.', page_config.fqdn, page_config.login)
            pass
    # LANDING
    download_returns = {
        'ok': False, 'code404': False, 
        'total': 0, 'success': 0, 'failed': 0
    }
    landing_page = index_page.get_landing(page_url)
    current_page = page_url
    downloaded_indexes = set([])
    if not landing_page.code404 or landing_page.vcount > 0:
        # CHECK LAZY
        if console_args.lazy:
            if page_config.index['last'] is None \
            and page_config.index['list'] is None:
                # print (landing_page.next, landing_page.last)
                lazy_finish = False
            else:
                # print ('next:', landing_page.next, 'last:', landing_page.last)
                if landing_page.next is None:
                    lazy_finish = False
                else:
                    if landing_page.last is not None:
                        views_page_last  = index_page.get_views(
                            urlPrefixer(landing_page.last, page_url)
                        ).views
                        # print (views_page_last)
                        views_page_first = landing_page.views
                    else:
                        if landing_page.list is not None \
                        and len(landing_page.list) > 0:
                            views_page_last  = index_page.get_views(
                                urlPrefixer(landing_page.list[-1], page_url)
                            ).views
                            views_page_first = landing_page.views
                        else:
                            views_page_first = None
                    if views_page_first is None:
                        lazy_finish = False
                    else:
                        lazy_finish = wrapper_check_lazy(
                            page_tagname, 
                            views_page_first, 
                            views_page_last, 
                            urlfirst= page_url, 
                            urllast = landing_page.last, 
                            verbose = console_args.verbose)
        else:
            lazy_finish = False
        # print ('Lazy:', lazy_finish)
        if not lazy_finish:
            while current_page is not None:
                if current_page == page_url:
                    current_page_obj = landing_page
                else:
                    current_page_obj = index_page.get_views(current_page)
                download_returns['total'] += current_page_obj.vcount
                my_printer('info', 
                    'INDEX [CHCK] - Url: "%s" (%s Imgs)', 
                    current_page, current_page_obj.vcount
                )
                # print ("DEBUG", current_page_obj.next); time.sleep(90)
                index_precheck = mech_dbchecks.views(
                    current_page_obj.views, 
                    page_tagname, 
                    verbose=False
                )
                if index_precheck.skip:
                    download_returns['success'] += current_page_obj.vcount
                    my_printer('info', 
                        'INDEX [SKIP] - Url: "%s" [%s/%s] db/img', 
                        current_page, 
                        index_precheck.count, 
                        current_page_obj.vcount
                    )
                    current_page = urlPrefixer(current_page_obj.next, page_url) \
                        if current_page_obj.vcount > 0 \
                        and current_page_obj.next not in downloaded_indexes \
                        else None
                    countdown(
                        gen_randwait(console_args.wait, half=True), 
                        txt = 'Next Index "%s" in:' % current_page
                    )
                else:
                    download_returns['success'] = 0
                    for view_href in current_page_obj.views:
                        view_id  = gen_viewid(
                            view_href, deviant = page_isdeviant)
                        view_url = urlPrefixer(view_href, page_url)
                        view_precheck = mech_dbchecks.view(
                            view_href, 
                            page_tagname, 
                            id=view_id, 
                            verbose=False
                        )
                        if view_precheck.skip:
                            download_returns['success'] += 1
                        else:
                            post_dlresult = do_post(
                                view_url, 
                                page_saveto, 
                                page_tagname, 
                                id=view_id)
                            if post_dlresult.ok:
                                download_returns['success'] += 1
                                countdown(
                                    gen_randwait(console_args.wait, half=True), 
                                    txt = 'Next Post in:'
                                )
                            else:
                                download_returns['failed'] += 1
                        my_printer('info', 
                            'INDEX [STAT] - Url: "%s" Currently at [%s/%s] Posts', 
                            current_page, download_returns['success'], current_page_obj.vcount
                        )
                        # print (view_id, view_url)
                    my_printer('info', 
                        'INDEX [DONE] - Index: "%s" Downloaded [%s/%s] Posts', 
                        current_page, download_returns['success'], current_page_obj.vcount
                    )
                    # GET NEXT
                    current_page = urlPrefixer(current_page_obj.next, page_url) \
                        if current_page_obj.vcount > 0 \
                        and current_page_obj.next not in downloaded_indexes \
                        else None
                    my_printer('info', 'INDEX [NEXT] - Url: "%s"', current_page)
                    if current_page is not None:
                        countdown(
                            gen_randwait(console_args.wait, more=1.5), 
                            txt = 'Next Index "%s" in:' % current_page)
                    else:
                        pass
                if console_args.only_update:
                    break
                else:
                    downloaded_indexes.add(current_page_obj.next)
            download_returns['ok'] = True \
                if download_returns['success'] >= download_returns['total'] \
                else False
        else:
            countdown(console_args.wait, txt = 'Lazy Skipped "%s":' % page_url)
            download_returns['ok'] = True
    else:
        download_returns['code404'] = True
        my_printer('error', 'INDEX [#404] - Url: "%s"', page_url)
    download_tally = namedtuple(
        'DownloadTally', list(download_returns.keys()))
    return download_tally(**download_returns)

if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(
        description='Download URL',
        argument_default=argparse.SUPPRESS, 
        formatter_class=RawTextHelpFormatter)
    args_parser.add_argument(
        dest='urls', nargs='*', default=None,
        help='an URL for the accumulator')
    args_parser.add_argument(
        '-f', '--list-file', dest='file', nargs='?', default=None, 
        help='List file')
    args_parser.add_argument(
        '-d', '--database',  dest='database', nargs='?', default=None, 
        help='Database Connector-string, Default=None provide no database storage')
    args_parser.add_argument(
        '-o', '--out-path', dest='saveto', nargs='?', 
        default=os.path.join(os.getcwd(), 'downloads'), 
        help='Download to folder')
    args_parser.add_argument(
        '-l', '--lq-sample', dest='sample', action='store_true', 
        help='download resized sample image too')
    args_parser.set_defaults(sample=False)
    args_parser.add_argument(
        '--png', dest='hq_png', action='store_true', 
        help='<Placeholder, have no effect> Only download PNG image, mainly for yande.re on others: force ignore sample image, even if thats the only image available.')
    args_parser.set_defaults(hq_png=False)
    args_parser.add_argument(
        '-n', '--naming-scheme', dest='name', action='store_true', 
        help='<Deprecated, flag has no effect, keep for posterity> include view id in file name.')
    args_parser.set_defaults(name_scheme=True)
    args_parser.add_argument(
        '-t', '--tag-tree', dest='tree', action='store_true', 
        help='Create tag folder to store downloads.')
    args_parser.set_defaults(tag_folder=False)
    args_parser.add_argument(
        '-r', '--re-download', dest='redownload', action='store_true', 
        help='Redownload if possible (file does not exists or can\'t be verified in dl path), ignore db file status.')
    args_parser.set_defaults(redownload=False)
    args_parser.add_argument(
        '-w', '--wait', dest='wait', nargs='?', type=int, default=7, 
        help='Sleep between Downloads, avoid soft-ban.')
    args_parser.add_argument(
        '--source', dest='source_links', nargs='?', default=None, 
        help='Save Source links to JSON file')
    args_parser.add_argument(
        '-c', '--check', dest='verify', action='store_true', 
        help='Force Verify image if file is not in db, default=do not verify if file exists in db or destination.')
    args_parser.set_defaults(verify=False)
    args_parser.add_argument(
        '-q', '--quiet', dest='verbose', action='store_false', 
        help='Quiet, subdue all output print only essential info, disable delete corrupt prompt.')
    args_parser.set_defaults(verbose=True)
    args_parser.add_argument(
        '-z', '--lazy', dest='lazy', action='store_true', 
        help='Lazy skip, if latest image is in db, check if last image is also downloaded, if yes, skip current url (uptodate).')
    args_parser.set_defaults(lazy=False)
    args_parser.add_argument(
        '-u', '--update', dest='only_update', action='store_true', 
        help='Only download the first page, for quick updates')
    args_parser.set_defaults(only_update=False)
    args_parser.add_argument(
        '-m', '--multi-download', dest='multi_download', nargs='?', type=int, default=0, 
        help='Download multiple file at the same time, recommended value is 2, default = 0.')
    args_parser.add_argument(
        '--debug', dest='debug', action='store_true', 
        help='Debug mode more verbose, raise on error.')
    args_parser.set_defaults(debug=False)
    # Parse Console Args
    console_args = args_parser.parse_args()
    console_color = True if os.name != 'nt' else False
    if console_args.verbose:
        if console_color:
            my_printer = print_color
        else:
            my_printer = print_log
    else:
        my_printer = lambda *x: None
    # Basics
    script_file = os.path.realpath(sys.path[0])
    script_path = os.path.dirname(script_file)
    script_name = os.path.basename(script_file).rsplit('.', 1)[0]

    from classes.utils import *
    from classes.database import checks
    from classes.utils import optception, get_siteconfigs, gen_randwait, gen_viewid, gen_tag, merge_two_dicts, isindex, gen_savename
    from classes import index, post

    # Browser
    mech_loggedin = set([])
    mech_browser = RequestsBrowser(
        verify  = console_args.verify, 
        verbose = console_args.verbose,
        retry   = 2, 
        debug   = console_args.debug, 
        color   = console_color
    )
    mech_cookies = os.path.join(script_path, '%s_cookies.txt' % script_name)
    # Database
    mech_database = db_init(console_args.database)
    mech_dbchecks = checks(mech_database, verbose=console_args.verbose)
    # Util & Wrapper Functions
    # ListFile
    if console_args.file is not None:
        if ':' in console_args.file:
            list_key, list_file = console_args.file.split(':', 1)
        else:
            list_key, list_file = None, console_args.file
        list_custom = keyed_list(list_file)
        file_klist = list_custom.read(list=True, key=list_key)
    else:
        file_klist = []
    index_combined = console_args.urls + file_klist
    # Main
    external_source = {}
    for index_urc in index_combined:
        if config_seperator in index_urc:
            indxu, indxd = index_urc.split(config_seperator, 1)
            index_url   = indxu.strip()
            index_workd = indxd.strip()
        else:
            index_url   = index_urc
            index_workd = console_args.saveto
        site_conf = get_siteconfigs(index_url)
        if site_conf is None:
            my_printer('warn', 'SITE  [SKIP] - Url: "%s" Is not supported', index_urc)
        else:
            # CREATING REUSABLE OBJECTS
            index_page = index.page(
                mech_browser, 
                **site_conf.index
            )
            post_page = post.page(
                mech_browser, 
                **site_conf.image, 
                lq = console_args.sample, 
                onetag = True
            )
            
            index_isurl_check = isindex(index_url)
            if index_isurl_check:
                my_printer('info', 'TYPE  [INDX] - Url: "%s" Conf: (%s)', index_url, site_conf.fqdn)
                page_dlresult = main(
                    index_url, 
                    index_workd, 
                    site_conf
                )
                my_printer('info', 'INDEX [DONE] - Url: "%s" Conf: (%s), Downloaded [%s/%s] Img, Ok: %s', index_url, site_conf.fqdn, page_dlresult.success, page_dlresult.total, page_dlresult.ok)
            else:
                my_printer('info', 'TYPE  [POST] - Url: "%s" Conf: (%s)', index_url, site_conf.fqdn)
                wrapper_prerun('_misc', index_workd)
                page_dlresult = do_post(
                    index_url, index_workd, '_misc', 
                    id='null' if 'rule34' in index_url else None)
                my_printer('info', 'POST  [GET#] - Url: "%s" Conf: (%s), Downloaded [%s/%s] Img, Ok: %s', index_url, site_conf.fqdn, page_dlresult.success, page_dlresult.total, page_dlresult.ok)

            # WAIT Before Next Url
            countdown(
                gen_randwait(
                    console_args.wait, 
                    more=1.5 if index_isurl_check else 1), 
                txt = 'Next Page in:')
    my_printer(
        'info', 'SITE  [DONE] - Processed: [%s] Urls', 
        len(index_combined))
    if len(external_source.keys()) > 0:
        if console_args.source_links is None:
            my_printer('debug', 'Consider download (%s) from source\n%s\n', len(external_source.keys()), json.dumps(external_source, indent=4, sort_keys=True, ensure_ascii=False))
        else:
            with open(console_args.source_links, 'w+') as source_jf:
                json.dump(external_source, source_jf, indent=4, sort_keys=True, ensure_ascii=False)
            my_printer('debug', 'Dumped (%s) External links to file "%s"', len(external_source.keys()), console_args.source_links)
    else:
        pass
else:
    pass
