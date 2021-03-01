#!/usr/bin/env python
# -*- coding: utf-8 -*-

from browsers.scrapers import lxml_scraper, dump_html
from helpers.misc import countdown, print_log, print_color
from helpers.config_file import config_ini
from classes.utils import pixiv_userid, nijie_id
from vars.conf_pixiv import pixiv_fqdn, pixiv_login_form, pixiv_index_identifier, \
    pixiv_follow_private, pixiv_follow_public, pixiv_follow_nextpg, xpath_pfollow_href, xpath_pfollow_next  
from vars.conf_nijie import nijie_fqdn, nijie_login_form, nijie_user_identifier, \
    nijie_follow_list, nijie_follow_nextpg, xpath_nfollow_href, xpath_nfollow_next  
from random import randint

def homepage_init(self, login_browser, **options):
    self.browser = login_browser
    self.login_conf = options.get('config', None)
    self.login_string = options.get('credential', None)
    self.login_ini = config_ini(self.login_conf, 'Login', User=None, Password=None)
    if self.login_string is not None:
        self.username, self.password = self.login_string.split(':', 1)
    else:
        self.username = self.login_ini['User']
        self.password = self.login_ini['Password']
    self.verbose = options.get('verbose', False)
    self.wait = options.get('wait', randint(5,11))
    self.debug = options.get('debug', False)
    self.captcha = options.get('captcha', 0)
    self.cookies = options.get('cookies', None)
    if self.verbose:
        self._brint = print_log if not options.get('color', False) else print_color
    else:
        self._brint = lambda *x: None

def list_following(self, follow_type=None, **options):
    list_limit = int(options.get('limit', 0))
    list_reverse = options.get('reverse', False)
    list_description = options.get('description', False)
    follow_ids = []
    if follow_type is None or self.url_public is None:
        follow_url = self.url_private
    else:
        follow_url = self.url_private if 'private' in follow_type else self.url_public
    follow_page = self.browser.open(follow_url, wait=self.wait, read=True)
    current_page = follow_url
    while current_page is not None:
        if current_page == follow_url:
            current_page_html = follow_page
        else:
            current_page_html = self.browser.open(current_page, wait=self.wait, read=True)
        # dump_html(current_page_html, '/tmp/follow.html')
        current_page_names = lxml_scraper(
            current_page_html,
            href = self.xpath_user, 
            text_user_name = self.xpath_user
        )
        self._brint('debug', 'UHOME [LIST] - Type: "%s", Page: "%s" +%s UserId', 
            follow_type, current_page, len(current_page_names['href']))
        current_follows = dict(zip(
            current_page_names['href'], 
            current_page_names['text_user_name']
        ))
        for x, y in current_follows.items():
            if self.uid_marker in x:
                member_id = self.gen_uid(x, meltdown=True) # troublesome
                if member_id not in follow_ids:
                    if list_description:
                        self._brint('info', 'UHOME [LIST] - Found User %s: [%s], Refer: "%s"', y, member_id, current_page)
                        follow_ids.append('#; %s' % y.strip())
                    follow_ids.append(member_id)
                else:
                    pass
            else:
                self._brint('warn', 'UHOME [LIST] - Invalid User %s: [%s], Refer: "%s"', y, x, current_page)
        # print ('[LIMIT] %s' % list_limit)
        if list_limit > 0 and len(follow_ids) > list_limit:
            break
        else:
            pass
        next_page_links = lxml_scraper(current_page_html, href=self.xpath_next)['href']
        # print (next_page_links)
        if len(next_page_links) == 0:
            current_page = None
        else:
            next_page_url = self.url_nextpg.format(uri=next_page_links[-1])
            if next_page_url != current_page:
                current_page = next_page_url
            else:
                current_page = None
    else:
        self._brint('debug', 'UHOME [LIST] - Type: "%s", Reached the end of Following page.', follow_type)
    if list_limit > 0 \
    and len(follow_ids) > list_limit:
        follow_ids = follow_ids[:list_limit]
    else:
        pass
    self._brint('debug', 'UHOME [LIST] - Type: "%s", %s Following Users added to List, Limit: %s', follow_type, len(follow_ids), list_limit)
    if list_reverse:
        follow_ids.reverse()
    else:
        pass
    return follow_ids

############################
# PIXIV SPECIFIC FUNCTIONS #
def pixiv_login(self, **options):
    login_cookies = options.get('cookies', self.cookies)
    login_manual = options.get('manual', False)
    login_captcha = int(options.get('captcha', self.captcha))
    login_dump = options.get('dump', None)
    login_meltdown = options.get('meltdown', False)
    try:
        self.browser.open(pixiv_fqdn, wait=self.wait)
        if login_manual or login_captcha > 0:
            self.browser.open(pixiv_login_form['url'], wait=self.wait)
            self.browser.dom_input(pixiv_login_form['user_input'], self.username, meltdown=True, debug=self.debug)
            self.browser.dom_input(pixiv_login_form['pass_input'], self.password, meltdown=True, debug=self.debug)
            self.browser.dom_click(pixiv_login_form['submit'], meltdown=True, debug=self.debug)
            captcha_timer = login_captcha if login_captcha > 0 else 300
            countdown(captcha_timer, 
                txt = 'Do yer CAPTCHA, Also click Login when ya done.')
        else:
            if login_cookies is not None:
                if not self.browser.load_cookies(login_cookies):
                    self.login(manual=True, cookies=login_cookies, meltdown=login_meltdown)
                else:
                    self._brint('ok', 'LOGIN [CKIE] - Cookies: "%s" Loaded', login_cookies)
            else:
                self.login(manual=True, cookies=None, meltdown=login_meltdown)
        # Verification
        self.browser.open(pixiv_login_form['home'], wait=self.wait)
        #self.browser.read(dump='/tmp/pstats.html')
        login_verify = lxml_scraper(
            self.browser.read(dump = login_dump),
            text_verify = pixiv_login_form['verify'],
        )['text_verify']
        # print (login_verify)
        if len(login_verify) > 0:
            self._brint('debug', 'LOGIN [VRFD] - Welcome: %s', login_verify)
            if login_cookies is not None:
                self.browser.save_cookies(login_cookies)
            else:
                pass
        else:
            self._brint('warn', 'LOGIN [WARN] - Unable to find "%s" in %s', self.username, login_verify)
            self._brint('error', 'LOGIN [FAIL] - Login Failed for User: "%s"', self.username)
            if login_meltdown:
                raise Exception ('Login Failed')
            else:
                pass
    except Exception as excp:
        raise excp
# wrapper
def gen_uid_pixiv(self, pixiv_url, **options):
    return pixiv_userid(pixiv_url, **options)

############################
# NIJIE SPECIFIC FUNCTIONS #
def nijie_login(self, **options):
    login_cookies = options.get('cookies', self.cookies)
    login_manual = options.get('manual', False)
    # un-used since nijie doesnt uses captcha, kept for posterity
    login_captcha = int(options.get('captcha', self.captcha))
    login_dump = options.get('dump', None)
    login_meltdown = options.get('meltdown', False)
    try:
        # self.browser.open(nijie_fqdn, wait=self.wait)
        self.browser.open(nijie_login_form['url'], wait=self.wait)
        self.browser.dom_click(nijie_login_form['login_age'], meltdown=True, debug=self.debug)
        self.browser.dom_click(nijie_login_form['login_reveal'], meltdown=True, debug=self.debug)
        self.browser.dom_input(nijie_login_form['user_input'], self.username, meltdown=True, debug=self.debug)
        self.browser.dom_input(nijie_login_form['pass_input'], self.password, meltdown=True, debug=self.debug)
        self.browser.dom_click(nijie_login_form['submit'], meltdown=True, debug=self.debug)
        if login_cookies is not None:
            if not self.browser.load_cookies(login_cookies):
                self.login(manual=True, cookies=login_cookies, meltdown=login_meltdown)
            else:
                self._brint('ok', 'LOGIN [CKIE] - Cookies: "%s" Loaded', login_cookies)
        else:
            self.login(manual=True, cookies=None, meltdown=login_meltdown)
        # Verification
        self.browser.open(nijie_login_form['home'], wait=self.wait)
        #self.browser.read(dump='/tmp/pstats.html')
        login_verify = lxml_scraper(
            self.browser.read(dump = login_dump),
            text_verify = nijie_login_form['verify'],
        )['text_verify']
        # print (login_verify)
        if len(login_verify) > 0:
            self._brint('debug', 'LOGIN [VRFD] - Welcome: %s', login_verify)
            if login_cookies is not None:
                self.browser.save_cookies(login_cookies)
            else:
                pass
        else:
            self._brint('warn', 'LOGIN [WARN] - Unable to find "%s" in %s', self.username, login_verify)
            self._brint('error', 'LOGIN [FAIL] - Login Failed for User: "%s"', self.username)
            if login_meltdown:
                raise Exception ('Login Failed')
            else:
                pass
    except Exception as excp:
        raise excp

# wrapper
def gen_uid_nijie(self, nijie_url, **options):
    return nijie_id(nijie_url, **options)

############################
# PIXIV CLASS CONSTRUCTION #
pixiv_homepage = type("pixiv_homepage", (), {
    "gen_uid": gen_uid_pixiv, 
    "url_private": pixiv_follow_private, 
    "url_public": pixiv_follow_public, 
    "url_nextpg": pixiv_follow_nextpg, 
    "xpath_user": xpath_pfollow_href, 
    "xpath_next": xpath_pfollow_next, 
    "uid_marker": pixiv_index_identifier, 
    "__init__": homepage_init, 
    "login": pixiv_login, 
    "list_following": list_following
})

############################
# NIJIE CLASS CONSTRUCTION #
nijie_homepage = type("nijie_homepage", (), {
    "gen_uid": gen_uid_nijie, 
    "url_private": nijie_follow_list, 
    "url_public": None, 
    "url_nextpg": nijie_follow_nextpg, 
    "xpath_user": xpath_nfollow_href, 
    "xpath_next": xpath_nfollow_next, 
    "uid_marker": nijie_user_identifier, 
    "debug": True, 
    "__init__": homepage_init, 
    "login": nijie_login, 
    "list_following": list_following
})

