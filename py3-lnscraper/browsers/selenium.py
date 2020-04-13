#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, json
from time                   import sleep
from lxml                   import etree
from platform               import system
from helpers.file_vrf       import FileVerifier
from helpers.misc           import cal_duration, humanize_bytes, countdown, print_log, print_color
from selenium               import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy                import Proxy, ProxyType
from browsers.requests      import RequestsBrowser
import pickle

class SeleniumBrowser():
    def __init__(self, **options):
        self.prog_path  = os.path.dirname(os.path.abspath(__file__))
        self.capability = options.pop('capability', 'chrome')
        self.html_404   = '//*[contains(@Text(), "This site can’t be reached")]'
        # self.type    = 'unknown'
        self.driver_bin = options.pop('driver_bin', None)
        self.wait    = int(options.pop('wait', 31))
        self.retries = int(options.pop('retry', 2))
        self.verify  = options.pop('verify', False)
        self.dlexpect= options.pop('expect', 'img,arc,zip,rar,torrent,mp4,webm,misc')
        self.verbose = options.pop('verbose', True)
        self.pcolor  = options.pop('color', False)
        self._brint  = print_log if not self.pcolor else print_color
        self.debug   = options.pop('debug', False)
        self.proxy   = options.pop('proxy', '')
        self.proxyDict = {
            "http"  : self.proxy,
            "https" : self.proxy,
            "ftp"   : self.proxy,
            } \
            if len(self.proxy) > 0 \
            else None

        self.driver = self.init_browser(
            self.capability, 
            **options, 
            proxy=self.proxyDict)
        # Set page load wait time        
        self.driver.implicitly_wait(self.wait)
        # External downloader
        cheat_header = options.pop('header', {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'})
        self.downloader = RequestsBrowser(
            header  = cheat_header, 
            proxy   = self.proxy, 
            verify  = self.verify, 
            expect  = self.dlexpect, 
            retry   = self.retries, 
            verbose = self.verbose, 
            color   = self.pcolor, 
        )

    def init_browser(self, br_capability, **options):
        private     = options.pop('private', False)
        off_screen  = options.pop('hide', False)
        head_less   = options.pop('headless', False)
        verbose     = options.pop('verbose', True)
        proxyDict   = options.pop('proxy', None)
        window_size = options.pop('window', '640x480')
        chrome_extension = options.pop('extension', None)
        ostype_nt   = True \
            if os.name == 'nt' \
            or 'cygwin' in system().lower() \
            else False
        if br_capability.lower() == 'firefox':
            # self.type = 'firefox'
            web_driver = self.driver_bin \
                if self.driver_bin is not None \
                else os.path.join(
                    self.prog_path, 
                    'geckodriver.exe' \
                        if ostype_nt \
                        else 'geckodriver'
                )
            #os.environ["webdriver.gecko.driver"] = web_driver
            firefox_prof = webdriver.FirefoxProfile()
            firefox_prof.set_preference(
                "browser.privatebrowsing.autostart", True)
            firefox_prof.set_preference("reader.parse-on-load.enabled", False)
            firefox_prof.set_preference("devtools.jsonview.enabled", False)
            firefox_prof.set_preference('network.proxy.Kind', 'Direct')
            firefox_opts = webdriver.FirefoxOptions()
            if head_less:
                firefox_opts.add_argument('-headless')
            else:
                pass
            if proxyDict is not None:
                driver = webdriver.Firefox(
                    executable_path = web_driver, 
                    firefox_profile = firefox_prof, 
                    firefox_options = firefox_opts,
                    proxy           = self.proxyDict
                )
            else:
                driver = webdriver.Firefox(
                    executable_path = web_driver, 
                    firefox_profile = firefox_prof, 
                    firefox_options = firefox_opts
                )
            #self.browser_settings_url = 'about:preferences#privacy'
            #self.clear_button = None
        elif br_capability.lower() == 'chrome' \
        or br_capability.lower() == 'chromium':
            # self.type = 'chrome'
            web_driver = self.driver_bin \
                if self.driver_bin is not None \
                else os.path.join(
                    self.prog_path, 
                    'chromedriver.exe' \
                        if ostype_nt \
                        else 'chromedriver'
                )
            #os.environ["webdriver.chrome.driver"] = web_driver
            chrome_useropts = webdriver.ChromeOptions()
            chrome_useropts.add_argument('--no-proxy-server')
            if off_screen: chrome_useropts.add_argument('--window-position="-1920,-1080"')
            else: pass
            if private: chrome_useropts.add_argument('--incognito')
            else: pass
            if head_less:
                chrome_useropts.add_argument('--headless')
                chrome_useropts.add_argument('--disable-gpu')
            else:
                if chrome_extension is not None:
                    chrome_useropts.add_argument(
                        '--load-extension=%s' % chrome_extension)
                else:
                    pass
            chrome_useropts.add_argument('--no-sandbox')
            chrome_useropts.add_argument('--disable-dev-shm-usage')
            if proxyDict is not None:
                chrome_useropts.add_argument(
                    '--proxy-server=%s' % proxyDict['http'])
            else:
                pass
            driver = webdriver.Chrome(
                web_driver, 
                chrome_options = chrome_useropts
            )
            #self.browser_settings_url = 'chrome://settings/clearBrowserData'
            #self.clear_button = '* /deep/ #clearBrowsingDataConfirm'
        else:
            if '@' in br_capability:
                remote_cap, remote_uri = br_capability.split('@', 1)
                if remote_cap.lower() == 'chrome':
                    web_cap = DesiredCapabilities.CHROME
                else:
                    web_cap = DesiredCapabilities.FIREFOX
            else:
                remote_uri = br_capability
                web_cap    = DesiredCapabilities.FIREFOX
            #print(remote_uri)
            if remote_uri is not None:
                web_driver = 'http://{uri}/wd/hub'.format(uri=remote_uri) \
                    if '://' not in remote_uri \
                    else remote_uri
                try:
                    if proxyDict is not None:
                        driver = webdriver.Remote(
                            command_executor     = web_driver, 
                            desired_capabilities = web_cap,
                            proxy                = self.proxyDict)
                    else:
                        driver = webdriver.Remote(
                            command_executor     = web_driver, 
                            desired_capabilities = web_cap)
                except Exception as excp:
                    raise excp
            else:
                raise Exception(
                    'SEDRV [INIT] - Browser Capability [%s] Invalid.' % br_capability)
            #self.browser_settings_url = None
            #self.clear_button = None
            self.capability = web_cap['browserName']
        if verbose:
            self._brint(
                'debug', 'SEDRV [INIT] - Spunned up [%s] WebDriver: "%s"', 
                self.capability, web_driver)
        else:
            pass
        if not head_less:
            w_x, w_y = window_size.split('x', 1)
            # driver.set_window_position(0, 0)
            driver.set_window_size(int(w_x), int(w_y))
        else:
            pass
        return driver


    def close(self):
        try:
            self.driver.stop_client()
            self.driver.quit()
        except Exception as excp:
            print(excp)
            self._brint('debug', 'SEDRV [EXIT] Browser already closed/crashed.')

    def __del__(self):
        self._brint('debug', 'SEDRV [DEL#] GOODBYE WORLD...')
        self.close()
        #self.clear_cache()
        #self.driver.close()
        #self.driver.stop()

    def save_cookies(self, cookie_path):
        try:
            #print(json.dumps(self.driver.get_cookies(), indent=True))
            with open(cookie_path, 'wb+') as c_f:
                pickle.dump(self.driver.get_cookies(), c_f)
            if self.verbose:
                self._brint('success', 'SEDRV [CKIE] - SaveTo: "%s" [Success]', cookie_path)
            return True
        except Exception as excp:
            self.driver.delete_all_cookies()
            if self.verbose:
                self._brint('warn', 'SEDRV [CKIE] - SaveTo: "%s" [Failed]: %s', cookie_path, str(excp))
            return False

    def load_cookies(self, cookie_path, **options):
        cookies_type = options.pop('type', 'pickle')
        if os.path.isfile(cookie_path):
            # print (cookies_type, cookie_path)
            try:
                if cookies_type == 'pickle':
                    with open(cookie_path, "rb") as c_f:
                        for cookie in pickle.load(c_f):
                            # print (json.dumps(cookie, indent=4, ensure_ascii=False, sort_keys=True))
                            # Fix pixiv cookies float expiry error
                            if 'expiry' in cookie.keys():
                                pickle_fix = int(cookie['expiry'])
                                cookie['expiry'] = pickle_fix
                            else:
                                pass
                            # print (cookie)
                            self.driver.add_cookie(cookie)
                else:
                    with open(cookie_path, "r") as c_f:
                        for cookie in json.load(c_f):
                            self.driver.add_cookie(cookie)
                # fake_cookie = {'path': '/', 'name': 'PHPSESSID', 'secure': True, 'domain': '.pixiv.net', 'httpOnly': True, 'value': '38580702_47c6faa0fa00e065bcceb582ced0da82', 'expiry': 1562038731.476166}
                # self.driver.add_cookie(fake_cookie)
                if self.verbose:
                    self._brint('success', 'SEDRV [CKIE] - File: "%s" Load [Success]', cookie_path)
                return True
            except Exception as excp:
                self.driver.delete_all_cookies()
                if self.verbose:
                    self._brint(
                        'warn', 'SEDRV [CKIE] - File: "%s" Load [Failed]\nCookies Exception:\n%s\n', 
                        cookie_path, str(excp))
                return False
        else:
            if self.verbose:
                self._brint('warn', 'SEDRV [CKIE] - File: "%s" Load [NotFound]', cookie_path)
            return False
            
    #def dump_cookies(self, cookie_path):
    #    ret_cookies = {}
    #    for cookie in pickle.load(open(cookie_path, "rb")):
    #        self._brint('debug', 'placeholder')

    def get(self, url, **options):
        read_html = options.pop('read', False)
        read_wait = options.pop('wait', self.wait)
        try:
            self.driver.get(url)
            #old_page = self.driver.find_element_by_tag_name('html')
            if self.verbose:
                countdown(read_wait, txt = 'Loading "%s" in:' % url)
            else:
                sleep(read_wait)
            if read_html:
                return self.driver.page_source
            else:
                return None
        except Exception as excp:
            self._brint(
                'error', 'SEDRV [OPEN] - Selenium [%s] Webdriver Crashed While Opening "%s"', 
                self.capability, url)
            self.close()
            raise excp

    def read(self, url=None, **options):
        # read_wait = int(options.pop('wait', 0))
        read_dump = options.pop('dump', None)
        if url is None:
            html_text = self.driver.page_source
        else:
            html_text = self.get(url, **options, read=True)
        if read_dump is not None:
            with open(read_dump, 'w+') as dmp:
                dmp.write(html_text)
        else:
            pass
        if len(html_text) > 100:
            try:
                check_404 = self.driver.find_element_by_xpath(self.html_404)
                if len(check_404) > 0:
                    self._brint('err', 'SEDRV [#404] - Could not Read: "%s", Reason: <%s>', url, self.html_404)
                    return None
                else:
                    return html_text
            except:
                return html_text
        else:
            self._brint('err', 'SEDRV [#404] - Could not Read: "%s", Reason: %s', url, html_text)
            return None

    def ctrl_s(self, src, saveas, **options):
        return None

    def post(self, post_url, post_data):
        return None

    def download(self, src, save_as, **options):
        referer     = options.pop('refer', None)
        dlverbose   = options.pop('verbose', self.verbose)
        try:
            # add referer header and download
            download_state = self.downloader.download(
                src, 
                save_as, 
                timeout = 30.0, 
                refer   = referer, 
                verbose = dlverbose)
            self._brint(
                'ok', 'SEDWL [DONE] - Src: "%s", Size: %s, Status: %s, Refer: "%s"', 
                src, download_state['size'], download_state['info'], referer
            )
        except Exception as excp:
            self._brint(
                'error', 'SEDWL [FAIL] - Src: "%s", Refer: "%s", Tried: %i', 
                src, referer, self.retries)
            if self.debug:
                raise excp
            else:
                download_state = {'ok': False, 'info': None, 'size': None}
        return download_state
