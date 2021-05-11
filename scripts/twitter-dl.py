#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, sys, time, urllib, json
from lxml                   import html
from urllib.parse           import urlparse, unquote_plus
from browsers.selenium      import SeleniumBrowser
from helpers.misc           import print_log, countdown, create_folder
from helpers.text_caching   import text_cache
from helpers.str_helper     import urlStripper, arr2str, string_sanitizer
from browsers.login         import page_login_sel
from vars.conf_bluebird     import site_config, seperator

default_path = os.path.dirname(os.path.abspath(__file__))
# original_link_format = 'https://pbs.twimg.com/media/{name}.{ext}:orig'
original_link_format = 'https://pbs.twimg.com/media/{name}?format={ext}&name=orig'

def login(mybrowser, loginurl, username, password, verifyurl):
    mybrowser.driver.get(loginurl)
    countdown(console_args.wait, txt='Loading "%s"' % loginurl)
    if os.path.isfile(console_args.cookies):
        mybrowser.load_cookies(console_args.cookies)
        mybrowser.driver.get(loginurl if verifyurl is None else verifyurl)
        countdown(console_args.wait, txt='Loading "%s"' % loginurl)
        logged_in = True if username in mybrowser.driver.title else False
    else:
        logged_in = False
        pass

    if not logged_in:
        u = mybrowser.driver.find_element_by_name("session[username_or_email]") #input_selector(login_infos['form_usr'])
        mybrowser.driver.implicitly_wait(1)
        u.send_keys(username)
        p = mybrowser.driver.find_element_by_name("session[password]") #input_selector(login_infos['form_pwd'])
        mybrowser.driver.implicitly_wait(1)
        p.send_keys(password)
        mybrowser.driver.find_element_by_xpath('//div[@role="button" and @data-testid="LoginForm_Login_Button"]').click()
        countdown(console_args.wait * 3, txt='POSTING login to "%s"' % loginurl)
    else:
        pass

    if verifyurl is not None:
        mybrowser.driver.get(verifyurl)
        countdown(console_args.wait, txt='Loading HOME "%s"' % verifyurl)
    else:
        pass
    print_log('debug', 'LOGIN_TITLE: %s' % mybrowser.driver.title)
    if not console_args.incognito:
        mybrowser.save_cookies(console_args.cookies)
    mybrowser.driver.implicitly_wait(1)

def file_id(file_url, **options):
    url_uquoted = unquote_plus(file_url, encoding='utf-8', errors='-')
    url_parsed = urlparse(url_uquoted)
    url_id = url_parsed.path.rsplit('/', 1)[1].strip()
    url_f = None
    for q in url_parsed.query.strip().split('&'):
        if q.startswith('format='):
            _, url_f = q.split('=', 1)
            break
    return '.'.join([url_id, url_f]) if url_f is not None else url_id

#https://twitter.com/sherryken777/media
def main():
    global console_args, console_color
    #print(main_opts['database'].split(':',1)[1].strip().split(','))
    path_saveto = os.path.normpath(console_args.save_path)
    if console_args.list_file is not None:
        list_cache = text_cache(expire=900)
        console_args.url.extend([u.strip() \
            for u in list_cache.read(console_args.list_file) \
            if not u.startswith('#') and len(u.strip()) > 0
        ])
    else:
        list_cache = None

    mybr = SeleniumBrowser(
        private     = console_args.incognito, 
        capability  = console_args.browser, 
        driverbin   = console_args.driver, 
        hide        = console_args.hide, 
        headless    = console_args.headless, 
        javascript  = True,
        verify      = console_args.verify, 
        verbose     = console_args.verbose, 
        color       = console_color
    )
    #page_login_sel(mybr.driver, **site_config['login'])
    if os.path.isfile(console_args.config):
        with open(console_args.config) as cnf:
            twitter_conf = json.load(cnf)
    else:
        twitter_conf = None
    assert twitter_conf is not None, 'Config file(JSON) Unavailable'
    twitter_user = twitter_conf['login'].get('username', None)
    twitter_pass = twitter_conf['login'].get('password', None)
    if twitter_user is not None and twitter_pass is not None:
        login(
            mybr,
            twitter_conf['login'].get('url', None), 
            twitter_user,
            twitter_pass,
            twitter_conf['login'].get('verify', None)
        )

    if console_args.database is None:
        main_dldb = None
    else:
        if console_args.database.startswith('sqlite:'):
            from databases.dldb_sqlite import dldb_sqlite
            main_dldb = dldb_sqlite(console_args.database.split(':',1)[1].strip())
        elif console_args.database.startswith('mysql:'):
            from databases.dldb_mysql_connector import dldb_mysql
            mysql_connect_strs = console_args.database.split(':',1)[1].strip().split(',')
            mysql_connect = {}
            for connect_str in mysql_connect_strs:
                o, v = connect_str.split('=',1)
                mysql_connect[o] = v
            main_dldb = dldb_mysql(**mysql_connect) if len(mysql_connect.keys()) >= 4 else None
        else:
            main_dldb = None

    twats = []
    for user_url in console_args.url:
        if seperator in user_url:
            anurl = user_url.split(seperator, 1)[0]
            apath = os.path.normpath(user_url.rsplit(seperator, 1)[1])
        else:
            anurl = user_url
            apath = path_saveto
        #print_log('info', anurl)
        twat_name = anurl.rsplit('/',1)[0] if \
                    site_config['fqdn'] not in anurl else \
                    anurl.rsplit(site_config['fqdn'], 1)[1].strip('/').split('/',1)[0]
        twat_save   = os.path.join(apath, twat_name)
        if site_config['fqdn'] not in anurl:
            twat_url = 'https://%s/%s' % (site_config['fqdn'], anurl.strip('/'))
        else:
            twat_url = anurl.strip('/')
        if '/media' not in twat_url:
            twat_url = '%s/media' % twat_url
        else:
            pass
        #print_log('info', twat_name, twat_url, twat_save)
        twats.append({
            'media': twat_url, 
            'save': twat_save, 
            'user': twat_name, 
            'raw': user_url
        })

    try:
        xphoto = site_config['photo']
        ximage = site_config['image']
        xvideo = site_config['video']
        for atwat in twats:
            if not os.path.exists(atwat['save']):
                try:
                    create_folder(atwat['save'])
                except:
                    raise
            else:
                pass
            print_log('info', 'Save to: "%s"', atwat['save'])

            twat_table = atwat['user'] if console_args.force_table is None else console_args.force_table
            if main_dldb is not None:
                main_dldb.run(
                    table=twat_table,
                    mode='create table',
                    view='text',
                    save='text'
                )
            else:
                pass

            mybr.get(atwat['media'])
            countdown(console_args.wait * 3, txt = 'Loading "%s" in' % atwat['media'])

            media_collection = set()
            last_height = mybr.driver.execute_script("return document.body.scrollHeight")
            cease_and_desist = False
            while not cease_and_desist:
                orig_imgs = []
                for media_photo in mybr.driver.find_elements_by_xpath(xphoto):
                    media_link = media_photo.get_attribute('href')
                    #print (media_link)
                    if '1328425270349598721' in media_link:
                        print_log('debug', 'WHAH [%s] ?', media_link)
                    orig_imgs.append({
                        'meta': 's{0}-p{1}'.format(*media_link.split('/status/', 1)[-1].split('/photo/', 1)), 
                        'src': media_photo.find_element_by_xpath(ximage).get_attribute('src') #?
                    })

                orig_videos = [ {'meta': None, 'src': mahd.get_attribute('src')} for \
                    mahd in mybr.driver.find_elements_by_xpath(xvideo) ]
                orig_posters = [] if not console_args.get_thumb else \
                    [ {'meta': None, 'src': mahd.get_attribute('poster')} for \
                        mahd in mybr.driver.find_elements_by_xpath(xvideo) ]
                orig_medias = orig_imgs + orig_videos + orig_posters

                # media_sanitized = [x.strip() for x in orig_medias if x not in media_collection and 'blob:' not in x and len(x.strip()) > 0]
                media_error = 0
                for media_data in orig_medias:
                    #print_log('info', orig)
                    media_url = media_data.get('src', None).strip()
                    media_meta = media_data.get('meta', None)
                    media_id = None if media_url is None else file_id(media_url)
                    print (media_id)
                    media_dbact = True if main_dldb is not None and media_id is not None else False
                    #print (media_url, media_id); exit()
                    if media_url in media_collection:
                        print_log('warn', 'SKIP [DUPE] Src: "%s", Meta: %s', media_url, media_meta)
                    elif 'blob:' in media_url:
                        print_log('warn', 'SKIP [BLOB] Src: "%s", Meta: %s', media_url, media_meta)
                    elif media_url is not None and len(media_url) > 7:
                        socmed_dlsearch = main_dldb.run(
                                table=twat_table,
                                mode='select row',
                                view=media_id
                            ) if media_dbact else \
                            []
                        #print('REAL DEBUG', socmed_dlsearch)
                        if len(socmed_dlsearch) > 0:
                            print_log('info', 'SKIP [IMG#] - Url: "%s", DB: %s', 
                                media_url, len(socmed_dlsearch))
                            if console_args.lazy:
                                print_log('info', 'SKIP [LAZY] - User: "%s"', user_url)
                                cease_and_desist = True
                                break
                            else:
                                pass
                        else:
                            #print('bog "%s"' % media_url)
                            media_url_name = media_url.rsplit('/', 1)[1]
                            # print('bog "%s" "%s"' % (media_url, media_url_name))
                            if '?' in media_url_name:
                                media_name, media_ext = (media_id.rsplit('.', 1)) if \
                                    '.' in media_id else \
                                    (media_id, 'DAT')
                            else:
                                media_name, media_ext = media_url_name.rsplit('.', 1)

                            media_save_byhuman = os.path.join(atwat['save'], '{user} {name}.{ext}'.format(
                                user=atwat['user'], name=media_name, ext=media_ext))
                            if not console_args.timestamp or media_meta is None:
                                media_save = media_save_byhuman
                                #media_save = os.path.join(atwat['save'], '{user} {name}.{ext}'.format(
                                #    user=atwat['user'], name=media_name, ext=media_ext))
                            else:
                                media_save = os.path.join(atwat['save'], '{user} {meta} {name}.{ext}'.format(
                                    user=atwat['user'], meta=media_meta, name=media_name, ext=media_ext))
                            
                            if all(x not in media_url for x in site_config['type_videos']):
                                media_url_sane = original_link_format.format(name=media_name, ext=media_ext) if \
                                    '?' in media_url else \
                                    '%s:orig' % media_url
                            else:
                                media_url_sane = media_url
                            # Actual download
                            if os.path.isfile(media_save_byhuman):
                                if media_save_byhuman != media_save:
                                    print_log('debug', 'MOVE [OLD#] save: "%s", to: "%s"', media_save_byhuman, media_save)
                                    if not os.path.isfile(media_save):
                                        os.rename(media_save_byhuman, media_save)
                                        solved_with = 'OLDFILE_MOVED'
                                    else:
                                        print_log('warn', 'MOVE [DUPE] save: "%s", to: "%s", Both exists', media_save_byhuman, media_save)
                                        solved_with = 'NOCLOBBER_SKIP'
                                else:
                                    print_log('debug', 'SKIP [OLD#] save: "%s"', media_save)
                                    solved_with = 'SAMEFILE_SKIP'
                                media_dlstat = {
                                   'ok': True,
                                   'info': 'Previously saved by hand, %s' % solved_with,
                                   'old_name': media_save_byhuman,
                                   'new_name': media_save
                                }
                            else:
                                media_dlstat = mybr.download(media_url_sane, media_save, refer=None)
                            if media_dlstat['ok']:
                                if media_dbact:
                                    main_dldb.run(
                                        table= twat_table,
                                        mode = 'insert row',
                                        view = media_id,
                                        save = media_save
                                    )
                                else:
                                    pass
                            else:
                                media_error += 1
                                pass
                            countdown(console_args.wait, txt = 'Download next file in:')
                        media_collection.add(media_url)
                    else:
                        print_log('warn', 'INVA [URL#] Src: "%s", Meta: "%s"', media_url, media_meta)
                #for orig in orig_medias:
                #    media_collection.add(orig)
                print_log('debug', 'Scroll Height: %s', last_height)
                mybr.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                countdown(console_args.wait * 3, txt = 'Loading after scroll, Continue in:')
                # Calculate new scroll height and compare with last scroll height
                #mybr.driver.switchTo().window(mybr.driver.windowHandles[0])
                mybr.driver.execute_script("window.focus();")
                new_height = mybr.driver.execute_script("return document.body.scrollHeight")
                #sekimatsu  = mybr.driver.find_elements_by_xpath(site_config['endpage'])
                if new_height == last_height: #and len(sekimatsu) > 0:
                    print_log('info', 'Reached the end of page for "%s"', anurl)
                    break
                else:
                    #mybr.driver.execute_script("window.focus();")
                    #time.sleep(5)
                    last_height = new_height
            print_log('info', 'Found %s items from "%s"', len(media_collection), atwat)
            
            countdown(console_args.wait * 3, txt = 'Process next Item in:')
            if list_cache is not None and media_error == 0:
                list_cache.comment(console_args.list_file, user_url)
                list_cache.check_dump(console_args.list_file)
            else:
                pass
        if list_cache is not None:
            list_cache.close()
        else:
            pass
        mybr.save_cookies(console_args.cookies)
    except Exception as excp:
        if list_cache is not None:
            # print (json.dumps(list_cache.store, indent=True))
            list_cache.close()
            mybr.save_cookies(console_args.cookies)
        else:
            pass
        if console_args.debug:
            print (repr(excp))
            _ = input('Press any key to exit\n')
        raise excp

if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter
    script_cwd = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    script_name =  '.'.join(os.path.basename(__file__).split('.')[:-1]).strip()
    parser = argparse.ArgumentParser(description='Download URL',
        argument_default=argparse.SUPPRESS, formatter_class=RawTextHelpFormatter)
    parser.add_argument('url', nargs='*', default=[],
        help='an URL for the accumulator.')
    parser.add_argument('-f', '--file', dest='list_file', nargs='?', 
        default=None,
        help='List file')
    parser.add_argument('-c', '--config', dest='config', nargs='?',
        default=os.path.join(script_cwd, 'twitter.json'),
        help='Config file (JSON)')
    parser.add_argument('-o', '--output-dir', dest='save_path', nargs='?',
        default=os.path.join(script_cwd, 'Downloads'),
        help='Download to folder')
    parser.add_argument('-d', '--database', dest='database', nargs='?',
        default=None,
        help='Set database connect string, default=None database is disabled.')
    parser.add_argument('-w', '--wait', dest='wait', nargs='?', type=int,
        default=5,
        help='wait n seconds between downloads (default = 5 seconds).')
    parser.add_argument('-r', '--redownload', dest='redownload',
        action='store_true',
        help='Redownload if possible, ignore db file status.')
    parser.set_defaults(redownload=False)
    parser.add_argument('-b', '--browser', dest='browser', nargs='?',
        default='chrome',
        help='Browser type: default=chrome (via native chromewebdriver) use firefox if needed be.')
    parser.add_argument(
        '--driver', dest='driver', nargs='?', default=None, 
        help='WebDriver binary path, by default, selenium will uses whichever apropriate webdriver found in env PATH.')
    parser.add_argument(
        '--table', dest='force_table', nargs='?', default=None,
        help='Force all database actions to use specified table')
    parser.add_argument('--cookies', dest='cookies', nargs='?',
        default=os.path.join(script_dir, 'twitter-cookies.pkl'),
        help='Cookies file path')
    parser.add_argument('-i', '--incognito', dest='incognito',
        action='store_true',
        help='Use Private browsing, will not let you save cookies for later sessions')
    parser.set_defaults(incognito=False)
    parser.add_argument('--hidden', dest='hide',
        action='store_true',
        help='Hide browser window off-screen (needed for on focus load function of twatter).')
    parser.set_defaults(hide=False)
    parser.add_argument('--headless', dest='headless',
        action='store_true',
        help='Headless mode, doesnt work very well with twitter since headless mode does not support javascript.')
    parser.set_defaults(headless=False)
    parser.add_argument('--check', dest='verify',
        action='store_true',
        help='Enable verify procedure, if not triggered file exists it will be counted as valid (new downloads will still be checked).')
    parser.set_defaults(verify=False)
    parser.add_argument('-q', '--quiet', dest='verbose', 
        action='store_false', 
        help='Quiet, subdue all output print only essential info, disable delete corrupt prompt')
    parser.set_defaults(verbose=True)
    parser.add_argument('--lazy', dest='lazy', 
        action='store_true', 
        help='Skip on first downloaded file, should only be used for increment downloads.')
    parser.set_defaults(lazy=False)
    parser.add_argument('--timestamp', dest='timestamp',
        action='store_true',
        help='Add time stamp and photo number to image name (Exprimental).')
    parser.set_defaults(timestamp=False)
    parser.add_argument('--debug', dest='debug',
        action='store_true',
        help='Debug mode, print traceback and keep browser open')
    parser.set_defaults(debug=False)
    parser.add_argument('--thumbnail', dest='get_thumb',
        action='store_true',
        help='Also get video thumbnail, usually not worth it')
    parser.set_defaults(get_thumb=False)
    console_args = parser.parse_args()
    console_color = True if os.name != 'nt' else False
    #print(main_opts)
    main()
    #time.sleep(999)
    print_log('info', 'END - Finished processing %i URL(s)', len(console_args.url))
    #del mybr
else:
    pass
