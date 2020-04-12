#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time, pickle, sys
import asyncio
import concurrent.futures
from copy import deepcopy
from lxml import etree
from random import randint
from datetime import datetime
from collections import namedtuple
from helpers.file_vrf import FileVerifier, match_size
from helpers.misc import cal_duration, humanize_bytes, print_log, print_color, print_progress_bar, bandwith_calc, countdown
from helpers.dir_helper import MkDirP

class RequestsBrowser():
    def __init__(self, **options):
        self.http_ngcodes = set([
            '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', 
            '414', '415', '416', '417', '418', '419', '420', '421', '422', '423', '424', '425', '426', '428', 
            '429', '430', '431', '440', '444', '449', '450', '451', '494', '495', '496', '497', '498', '499', 
            '500', '501', '502', '503', '504', '505', '506', '507', '508', '509', '510', '511', '520', '521', 
            '522', '523', '524', '525', '526', '527', '530', '598', 
            '204', '205', '206'
        ])
        self.http_okcodes = ([
            '200', '201', '202', '203', '300', '301', '302', '303', '304', '305', '306', '307', '308', 
        ])
        self.verbose    = options.pop('verbose', False)
        self.verify     = options.pop('verify', False)
        self.dlexpect   = options.pop('expect', 'img,arc,zip,rar,torrent')
        self.auto_del   = options.pop('auto_delete', False)
        options_wait    = options.pop('wait', 7)
        self.wait       = int(options_wait) \
            if str(options_wait).isdigit() \
            else 7
        self.wait_rand  = lambda x: randint(x, x+self.wait)
        self.retry      = int(options.pop('retry', 1))
        self.retry_wait = randint(51, 77)
        self.block_size = int(options.pop('chunk', 8192))
        self.cloudflare = options.pop('cloudflare', False)
        self.workers    = options.pop('workers', 1)
        self.debug      = options.pop('debug', False)
        self.pcolor     = options.pop('color', False)
        if self.verbose or self.debug:
            self._brint = print_log if not self.pcolor else print_color
        else:
            self._brint = lambda *x: None
        if self.cloudflare:
            try:
                import cfscrape
                self.browser = cfscrape.create_scraper()
            except Exception as excp:
                raise excp
        else:
            import requests
            import requests.auth
            try:
                from requests.packages.urllib3.exceptions import InsecureRequestWarning
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            except:
                pass
            self.browser = requests.Session()
        cheat_header = options.pop('header', {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'})
        if isinstance(cheat_header, dict):
            self.browser.headers.update(cheat_header)
        else:
            pass
        self.timeout = int(options.pop('timeout', 15))
        self.ssl     = options.pop('ssl', False)
        user_proxy   = options.pop('proxy', '')
        self.browser.proxies.update(
            {'http' : user_proxy, 'https': user_proxy, 'ftp'  : user_proxy,}
        )

    def save_cookies(self, cookie_path, **options):
        cookies_debug = options.pop('debug', False)
        try:
            if cookies_debug:
                print(self.browser.cookies)
            else:
                pass
            with open(cookie_path, 'wb+') as c_f:
                pickle.dump(self.browser.cookies, c_f)
            self._brint('success', 'REQ-COOKIE_SAVE - FILE: "%s" [Success]', cookie_path)
            return True
        except Exception as excp:
            self.browser.cookies.clear()
            self._brint('warn', 'REQ-COOKIE_SAVE - FILE: "%s" [Failed]: %s', cookie_path, str(excp))
            return False

    def load_cookies(self, cookie_path, **options):
        cookies_debug = options.pop('debug', False)
        if os.path.isfile(cookie_path):
            try:
                with open(cookie_path, 'rb') as c_f:
                    self.browser.cookies.update(pickle.load(c_f))
                if cookies_debug:
                    print(self.browser.cookies)
                else:
                    pass
                self._brint('ok', 'REQBR [COOK] - FILE LOAD: "%s", STAT: Cookies load succesful', cookie_path)
                return True
            except Exception as excp:
                self.browser.cookies.clear()
                self._brint('warn', 'REQBR [COOK] - FILE CLEAR: "%s", STAT: Cookies load failed: %s', cookie_path, str(excp))
                return False
        else:
            self._brint('warn', 'REQBR [COOK] - FILE NOTFOUND: "%s", STAT: Skip loading Cookies', cookie_path)
            return False

    def update_headers(self,**headers):
        refer  = headers.pop('refer', None)
        cookie = headers.pop('cookie', None)
        if refer is not None:
            self.browser.headers.update({'Referer': refer})
        else:
            pass
        if cookie is not None:
            self.browser.headers.update({'Cookie': cookie})
        else:
            pass

    def get(self, url, **options):
        re_tries = options.pop('retry', self.retry)
        basic_auth = options.pop('auth', None)
        get_refer = options.pop('refer', None)
        self.update_headers(refer = get_refer)
        read_tries = 0
        read_success = False
        while \
        not read_success \
        and read_tries < re_tries: 
            read_tries += 1
            response_code = None
            try:
                if basic_auth is not None:
                    req_response = self.browser.get(
                        url, 
                        verify = self.ssl, 
                        auth = basic_auth, 
                        timeout = self.timeout)
                else:
                    req_response = self.browser.get(
                        url, 
                        verify = self.ssl, 
                        timeout = self.timeout)
                response_code = req_response.status_code
                read_success = True \
                    if str(response_code) not in self.http_ngcodes \
                    else False
                self._brint(
                    'info' if read_success else 'warn', 
                    'REQBR [#%s] - Url: "%s" %s, Try: [%s/%s]', 
                    response_code, url, read_success, read_tries, re_tries)
            except Exception as excp:
                #raise
                if not self.debug:
                    read_success = False
                    self._brint('error', 'REQBR [#%s] - Url: "%s" %s,\n\tException:\n\t%s,\nTry: [%i/%i] %s', response_code, url, read_success, excp, read_tries, re_tries, response_code)
                    self.sleeper(self.wait, txt='Exception Cooldown:')
                else:
                    raise excp
        else:
            #if self.verbose:
            #    self._brint('info', 'REQBR [#%s] - Url: "%s" %s, Try: [%s/%s]', response_code, url, read_success, read_tries, re_tries)
            #else:
            pass
        return req_response.text if read_success else None

    def read(self, url, **options):
        html_dump = options.pop('dump', None)
        html_text = self.get(url, **options)
        if html_dump is not None:
            try:
                with open(html_dump, 'w+') as dmp:
                    dmp.write(html_text)
            except Exception as excp:
                self._brint('warn', 'REQBR [DUMP] - Url: "%s" to File: "%s", Exception:\n%s', url, html_dump, excp)
        else:
            pass
        return html_text

    def get_header(self, url):
        head_code = None
        head_type = None
        head_clen = 0
        try:
            head      = self.browser.head(url, allow_redirects=True)
            head_code = head.status_code
            head_clen = head.headers.get('content-length')
            head_type = head.headers.get('content-type')
        except Exception as excp:
            self._brint('warn', 'REQBR [%s] - Unable to Request HEADERs for "%s", Going in Blind\n%s', head_code, url, excp)
        header_data = namedtuple('Header', ['code', 'size', 'type'])
        return header_data(
            code = head_code, 
            size = head_clen, 
            type = head_type
        )

    # basicly an async wrapper
    async def download_async(self, srcdstref_list, **common_data):
        dl_saveto = common_data.pop('saveto', None)
        dl_cookies = common_data.pop('cookies', None)
        if dl_cookies is not None:
            self.browser.headers.update({'Cookie': dl_cookies})
        else:
            pass
        with concurrent.futures.ThreadPoolExecutor(max_workers = self.workers) \
        as conc_executor:
            loop = asyncio.get_event_loop()
            promised_results = [
                loop.run_in_executor(
                    conc_executor, 
                    self.download_simpleton, 
                    dl_info['src'], 
                    os.path.join(dl_saveto, dl_info['dst']) \
                        if dl_saveto is not None \
                        else dl_info['dst'], 
                    dl_info['ref']
                ) \
                for dl_info in srcdstref_list
            ]
        return await asyncio.gather(*promised_results)
    
    # conforms to loop.run_in_executor function requirements, no kwargs
    def download_simpleton(self, link_url, save_dst, link_ref=None):
        download_status = {
            'url': link_url, 
            'save': save_dst, 
            'ok': False, 
            'info': None, 
            'response': None, 
            'size': 0
        }
        if link_ref is not None:
            self.browser.headers.update({'Referer': link_ref})
        else:
            pass
        download_request = self.browser.get(
            link_url, verify = self.verify, 
            allow_redirects = True, 
            timeout = self.timeout, 
            stream = True
        )
        respond_code = download_request.status_code
        content_size = download_request.headers.get('content-length')
        content_type = download_request.headers.get('content-type')

        download_status['response'] = respond_code
        download_status['size'] = content_size
        if respond_code is not None \
        and str(respond_code) in self.http_okcodes:
            if os.path.isfile(save_dst):
                if self.verify:
                    file_state = FileVerifier(
                        save_dst,
                        remote=content_size,
                        shtimeout=True,
                        verbose=self.verbose,
                        debug=self.debug
                    ).verify(
                        delete=False, 
                        debug=self.debug
                    )
                    if file_state['verified']:
                        download_status['ok'] = True
                        status_info = 'skip'
                    else:
                        download_status['ok'] = False
                        status_info = 'broken'
                        broken_file = '%s-BROKEN.%s' % tuple(save_dst.rsplit('.', 1))
                        if not os.path.isfile(broken_file):
                            os.rename(save_dst, broken_file)
                        else:
                            pass
                    download_status['info'] = '{state}:verified-{vbool},{vmime}:{head_type}'.format(
                        state = status_info, 
                        vbool = file_state['verified'], 
                        vmime = file_state['type'], 
                        head_type = content_type
                    )
                else:
                    download_status['ok'] = True
                    download_status['info'] = 'skip:novrf-exists,file:%s' % content_type
            else:
                self._brint(
                    'info', 
                    'REQDL [#{code}] - DOWNLOAD Details:\nRefer   : "{refer}"\nSrc     : "{src}"\nContent : "{size_h}" [{size_b}] {type}\nSaveAs  : "{save}"'.format(
                        code = respond_code, 
                        src = link_url, 
                        save = save_dst, 
                        size_h = humanize_bytes(content_size),
                        size_b = content_size, 
                        type = content_type, 
                        refer = link_ref
                    )
                )
                save_part = '%s-PART.%s' % tuple(save_dst.rsplit('.', 1))
                with open(save_part, 'wb+') as save_dump:
                    save_dump.write(download_request.content)
                file_state = FileVerifier(
                    save_part,
                    remote=content_size,
                    shtimeout=True,
                    verbose=self.verbose,
                    debug=self.debug
                ).verify(
                    delete=False, 
                    debug=self.debug
                )
                if file_state['verified']:
                    download_status['ok'] = True
                    os.rename(save_part, save_dst)
                    self._brint('done', 'REQDL [#%s] - Downloaded %s Bytes to "%s"', respond_code, content_size, save_dst)
                else:
                    download_status['ok'] = False
                    self._brint('error', 'REQDL [#%s] - Download to "%s" Failed.', respond_code, content_size, save_dst)
                download_status['info'] = 'manual:verified-{vbool},{vmime}:{head_type}'.format(
                    vbool = file_state['verified'], 
                    vmime = file_state['type'], 
                    head_type = content_type
                )
        else:
            download_status['ok'] = False
            download_status['info'] = 'error:http-%s,file:%s' % (
                respond_code, content_type)
        return download_status

    def sleeper(self, timer_seconds, **options):
        if self.verbose:
            text_msg = options.pop('txt', None)
            countdown(timer_seconds, txt=text_msg)
        else:
            time.sleep(timer_seconds)

    def download_post(self, check_file, **options):
        return None

    def post(self, url, common_data):
        return self.browser.post(
            url, data = common_data, 
            verify = self.ssl)

    def get_header_object(self, url, header_key):
        head_reader = self.browser.head(url, allow_redirects=True)
        return head_reader.headers.get(header_key) \
            if head_reader is not None \
            else None
