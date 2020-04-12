#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time, pickle, sys
from copy import deepcopy
from lxml import etree
from random import randint
from datetime import datetime
from collections import namedtuple
from helpers.file_vrf import FileVerifier, match_size
from helpers.misc import cal_duration, humanize_bytes, print_log, print_color, print_progress_bar, bandwith_calc, countdown

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
        self.dlexpect   = options.pop('expect', 'img,arc,zip,rar,torrent,mp4,webm,misc')
        self.auto_del   = options.pop('auto_delete', False)
        options_wait    = options.pop('wait', 7)
        self.wait       = int(options_wait) \
            if str(options_wait).isdigit() \
            else 7
        self.retry      = int(options.pop('retry', 2))
        self.retry_wait = randint(51, 77)
        self.block_size = int(options.pop('chunk', 8192))
        self.cloudflare = options.pop('cloudflare', False)
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

    def download_pre(self, check_file, **options):
        file_size   = options.pop('size', None)
        pars_verify = options.pop('verify', False)
        pars_autorm = options.pop('delete', False)
        if os.path.isfile(check_file):
            if file_size is not None \
            and str(file_size).isdigit():
                if match_size(check_file, file_size, True):
                    file_state = {'verified': True} \
                        if not pars_verify \
                        else FileVerifier(
                            check_file,
                            remote=file_size,
                            shtimeout=True,
                            verbose=self.verbose,
                            debug=False
                        ).verify(
                            delete=pars_autorm, 
                            debug=False)
                else:
                    file_state = {'verified': True} \
                        if not pars_verify \
                        else {'verified': False}
            else:
                file_state = {'verified': True}
            if file_state['verified']:
                self._brint('info', 
                    'REQDL [SKIP] - File: "%s", Verified (%s) %s, Return [True]', 
                    check_file, file_size, pars_verify)
                precheck_results = {
                    'ok': True,
                    'type': 'skip:verify-ok' \
                        if pars_verify \
                        else 'skip:verify-no'
                }
            else: 
                self._brint('warn', 'REQDL [SKIP] - File: "%s", Verification Failed %s, Return [False]', check_file, file_size)
                precheck_results = {
                    'ok': False,
                    'type': 'manual:verify-failed'
                }
        else:
            precheck_results = {'ok': False, 'type': 'skip:match-size'}
        download_prechecks = namedtuple('PreCheck', list(precheck_results.keys()))
        return download_prechecks(**precheck_results)

    def download_write(self, file_remote, file_path, **options):
        file_block = options.pop('block', self.block_size)
        file_iter  = options.pop('iter', False)
        file_size  = options.pop('size', 0)
        try:
            if file_iter:
                dlt_start = time.time()
                with open(file_path, 'wb+', file_block) as save_file:
                    # 8192
                    for file_chunk \
                    in file_remote.iter_content(chunk_size = self.block_size):
                        save_file.write(file_chunk)
                        print_progress_bar(
                            save_file.tell(), 
                            file_size,
                            # label = '{:16}'.format('Progress'), 
                            label = 'Progress',
                            color = self.pcolor
                        )
                dlt_end = time.time()
                print (
                    ' [{duration:.2f} sec] [{speed:.2f} kB/s]'.format(
                        **bandwith_calc(dlt_start, dlt_end, file_size)
                    )
                )
            else:
                with open(file_path, 'wb+') as save_file:
                    save_file.write(file_remote.content)
            return True
        except Exception as excp:
            self._brint('error', 'REQDL [WR+B] - WRITE File: "%s" Failed (%s bytes), Exception:\n%s', file_path, file_size, excp)
            return False

    def download_func(self, url, save_as, **options):
        refer     = options.pop('refer', None)
        func_verbose = options.pop('verbose', self.verbose)
        head_code = options.pop('code', None)
        file_resp = self.browser.get(
            url, 
            verify          = self.verify, 
            allow_redirects = True, 
            timeout         = self.timeout, 
            stream          = True
        )
        head_size   = file_resp.headers.get('content-length')
        remote_size = int(head_size) \
            if head_size is not None \
            and str(head_size).isdigit() \
            else 0
        save_part = '%s.part' % save_as
        remote_type = file_resp.headers.get('content-type') \
            if head_code is not None \
            else 'UnknownType'
        self._brint(
            'info', 
            '''REQDL [#{code}] - DOWNLOAD Details:
Refer   : "{refer}"
Src     : "{src}"
Content : "{size_h}" [{size_b}] {type}
SaveAs  : "{save}"'''.format(
                code = file_resp.status_code, 
                src = url, 
                save = save_as, 
                size_h = humanize_bytes(remote_size),
                size_b = remote_size, 
                type = remote_type, 
                refer = refer
            )
        )
        if remote_size is None or remote_size <= 0:
            self._brint('warn', 'REQDL [#%s] - Src: "%s" Remote file size Unavailable, Download anyway.', head_code, url)
            write_status = self.download_write(
                file_resp, save_part, iter=False, size=remote_size)
        else:
            #print('START', save_part)
            if self.verbose:
                # uses 4096, 8192 seem to make socket timeout appears more frequently? somehow?
                write_status = self.download_write(
                    file_resp, 
                    save_part, 
                    iter = func_verbose, 
                    block = 4096, 
                    size = remote_size)
            else:
                write_status = self.download_write(
                    file_resp, save_part, iter=False, size=remote_size)
                    
        if write_status:
            self._brint(
                'debug', 
                'REQDL [#%s] - Written %s (%s) From Src: "%s" to SaveAs: "%s"', 
                head_code, humanize_bytes(remote_size), remote_size, url, save_as)
            try:
                os.rename(save_part, save_as)
            except Exception as excp:
                self._brint(
                'warn', 
                'REQDL [#%s] - Seems like youre having a Race Condition on your hand\nRename:\n\tFrom: %s\n\tTo  : %s', 
                head_code, save_part, save_as)
                raise excp
            if remote_size > 0:
                download_size = remote_size
            else:
                download_size = int(os.path.getsize(save_as))
            return download_size
        else:
            self._brint(
                'err', 
                'REQDL [#%s] - Write Failed %s (%s) From Src: "%s" to SaveAs: "%s"', 
                head_code, humanize_bytes(remote_size), remote_size, url, save_as)
            return 0

    def sleeper(self, timer_seconds, **options):
        if self.verbose:
            text_msg = options.pop('txt', None)
            countdown(timer_seconds, txt=text_msg)
        else:
            time.sleep(timer_seconds)

    def download_post(self, check_file, **options):
        return None

    def download(self, url, save_as, **options):
        self.update_headers(**options)
        dlrefer  = options.pop('refer', None)
        dlverify = options.pop('verify', self.verify)
        dlexpect = options.pop('expect', self.dlexpect)
        dlverbose = options.pop('verbose', self.verbose)
        head_info = self.get_header(url)
        pre_check = self.download_pre(
            save_as, 
            size    = head_info.size, 
            verify  = dlverify,
            delete  = False)
        if pre_check.ok:
            downloaded_stat = True
            download_type   = pre_check.type
            downloaded_size = head_info.size
        else:
            #print('START DOWNLOAD WHILE')
            self._brint('info', 'REQDL [HEAD] - Src: "%s" [#%s %s %s Bytes]', url, head_info.code, head_info.type, head_info.size)
            downloaded_stat = False
            download_type   = pre_check.type
            downloaded_size = head_info.size
            dltried  = 0
            downloaded_stat = False
            while str(head_info.code) not in self.http_ngcodes \
            and dltried < self.retry \
            and not downloaded_stat:
                dltried += 1
                try:
                    downloaded_size = self.download_func(
                        url, save_as, 
                        refer = dlrefer, 
                        code  = head_info.code, 
                        verbose = dlverbose
                    )
                    modedel = 'mv' if dltried >= self.retry else 'rm'
                    # Verification, skip delete on fail if this is the last try
                    #self.auto_del = False \
                    #    if dltried >= self.retry \
                    #    else True
                    file_state = FileVerifier(
                        save_as, 
                        remote = downloaded_size, 
                        shtimeout = True, 
                        verbose = self.verbose,
                        debug = self.debug
                    ).verify(
                        delete = self.auto_del, 
                        mode = modedel, 
                        debug = self.debug, 
                    )
                    self._brint(
                        'ok' if file_state['verified'] else 'err', 
                        'REQDL [#%s] - Src: "%s", Size: %s (%s), Verifired: [%s/%s], Tries: [%s/%s]', 
                        head_info.code, url, downloaded_size, 
                        humanize_bytes(downloaded_size), 
                        file_state['type'], file_state['verified'], 
                        dltried, self.retry)
                    downloaded_stat = file_state['verified'] \
                        if file_state['type'] is not None \
                        and file_state['type'] in dlexpect \
                        else False
                    download_type = 'manual-verify-{type}-{verified}'.format(**file_state)
                    if not downloaded_stat:
                        self.sleeper(self.retry_wait, txt='Retry %s in:' % (dltried + 1))
                        head_info = self.get_header(url) \
                            if dltried > 0 \
                            else head_info
                    else:
                        self.sleeper(self.wait, txt='[REQDL] Success Cooldown:')
                except Exception as excp: 
                    downloaded_size = 0
                    downloaded_stat = False
                    download_type   = 'manual-exception'
                    self._brint('error', 'REQDL [#%s] - RETRY Src: "%s",\n\tException:\n\t%s\nTries: [%s/%s] in%s seconds.', head_info.code, url, str(excp), dltried, self.retry, self.retry_wait)
                    # exc_type, _, exc_tb = sys.exc_info()
                    # self._brint('error', 'REQDL [#%s] - RETRY Src: "%s",\n\tException: [%s] %s\n\t%s\nTries:[%s/%s] in %s seconds.', head_info.code, url, exc_type, exc_tb.tb_lineno, str(excp),dltried, self.retry, self.retry_wait)
                    self.sleeper(self.retry_wait, txt = 'Retry "%s" in:' % url)
                    if not self.debug:
                        head_info = self.get_header(url) \
                            if dltried > 0 \
                            else head_info
                    else:
                        raise excp
            # else:
            #     self._brint('debug', 
            #         'REQBR [#%s] - Src: "%s", Size: %s (%s), Tries: [%s/%s]', 
            #         head_info.code, url, downloaded_size, 
            #         humanize_bytes(downloaded_size), 
            #         dltried, self.retry)
        return {
            'ok': downloaded_stat, 
            'info': download_type.lower(), 
            'size': int(downloaded_size) \
                if str(downloaded_size).isdigit() \
                else downloaded_size,
        }

    def post(self, url, post_data):
        return self.browser.post(
            url, data = post_data, 
            verify = self.ssl)

    def get_header_object(self, url, header_key):
        head_reader = self.browser.head(url, allow_redirects=True)
        return head_reader.headers.get(header_key) \
            if head_reader is not None \
            else None
