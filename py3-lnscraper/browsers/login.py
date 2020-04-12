#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ALT'
import os, re, time, json
from helpers.misc               import check_null, check_either, telltime, print_log, countdown
from helpers.str_helper         import urlPrefixer
from browsers.scraper_lxml      import html_scraper, spiderman, dump_html
from selenium.common.exceptions import NoSuchElementException

# Just be grateful it's not meth, confirmed working with python3
def page_login_sel(current_driver, **login_options):
    login_url = login_options.pop('url', None)
    user_value = login_options.pop('user', None)
    pass_value = login_options.pop('pass', None)
    form_user = login_options.pop('form_user', None)
    form_pass = login_options.pop('form_pass', None)
    form_button = login_options.pop('form_submit', None)
    form_remember = login_options.pop('form_remember', None)
    form_check = login_options.pop('check', None)
    login_debug = login_options.pop('debug', False)
    login_wait = int(login_options.pop('wait', 7))
    if any(need_dis is None for need_dis in [user_value, pass_value, form_user, form_pass, form_button, login_url]):
        if login_debug:
            print_log('error', 'LOGIN [MISS] - Data:\n%s', json.dumps(login_options, indent=True))
            raise Exception('Missing Login Data')
        else:
            print_log('warn', 'LOGIN [MISS] - Data:\n%s\nLogin Skipped.', json.dumps(login_options, indent=True))
    else:
        current_driver.get(login_url)   #Open login page
        countdown(login_wait, txt = 'Loading Login Url: "%s"' % login_url)
        #tryin out closure
        def input_selector(input_identifier):
            if input_identifier.startswith('//'):
                input_object = current_driver.find_element_by_xpath(input_identifier)
            else:
                try:
                    input_object = current_driver.find_element_by_id(input_identifier)
                except NoSuchElementException:
                    input_object = current_driver.find_element_by_name(input_identifier)
            return input_object

        input_selector(form_user).send_keys(user_value)
        countdown(int(login_wait / 2), txt = 'Typing UserName...')
        input_selector(form_pass).send_keys(pass_value)
        countdown(int(login_wait / 2), txt = 'Typing Password...')
        if form_remember is not None:
            input_selector(form_remember).click()    #Select "RememberMe" if possible
        input_selector(form_button).click()  #Click the Submitbutton
        countdown(int(login_wait / 2), txt = 'Push Submit Button...')
        #current_driver.get(verify'])
        if form_check is not None:
            current_driver.get(form_check)
            countdown(login_wait, txt = 'Loading check Url: "%s"' % form_check)
            check_xpath = login_options.pop('check_xpath', None)
            if check_xpath is None:
                return True
            else:
                try:
                    check_object = input_selector(check_xpath).text
                    print_log('info', 'LOGIN [CHCK] - Text: "%s" @ "%s"', check_object, form_check)
                    return True if len(check_object) > 0 else False
                except Exception as excp:
                    print_log('warn', 'LOGIN [FAIL] - Could not check Login status @ "%s"\n%s', form_check, excp)
                    return False
        else:
            return True


# Supports any? browser type, main operation is just to visit the accept link
def blogspot_accept(current_browser, r18_link):
    accept_xpath = '//div[@id="maia-main"]/p/a[@class="maia-button maia-button-primary"]'
    accept_href  = html_scraper(
        current_browser.read(r18_link), 
        href = accept_xpath, 
        refer = r18_link, 
    )
    if len(accept_href['href']) > 0:
        current_browser.browser.get(accept_href['href'][0])
    else:
        pass

def site_login_req(req_browser, **login_params):
    login_dry  = login_params.pop('dry', False)
    login_url  = login_params.pop('url', None)
    login_home = login_params.pop('home', None)
    xhome_chck = login_params.pop('check', None)
    def login_check():
        if login_home is not None \
        and xhome_chck is not None:
            login_text = html_scraper(
                req_browser.read(
                    login_home, 
                    # dump='/tmp/login-check.html', 
                ),
                text_login = xhome_chck, 
                refer = login_url, 
            )['text_login']
            print_log('debug', 
                'LOGIN [CHCK] - Url: "%s" > %s', 
                login_home, login_text)
            if len(login_text) > 0:
                return True
            else:
                return False
        else:
            return True
    if not login_dry:
        xform_lgin = login_params.pop('form', None)
        xform_user = login_params.pop('form_user', None)
        xform_pass = login_params.pop('form_pass', None)
        xform_tokn = login_params.pop('form_token', None)
        xform_rmbr = login_params.pop('form_remember', None)
        value_user = login_params.pop('value_name', None)
        value_pass = login_params.pop('value_pass', None)
        if xform_lgin is not None:
            if str(xform_lgin).isdigit():
                xform_form = '//form[%s]' % xform_lgin
            else:
                xform_form = xform_lgin
        else:
            xform_form = '//form[0]'
        login_html = req_browser.read(login_url)#, dump='/tmp/login.html')
        login_form = spiderman(login_html, refer=login_url)
        login_inputs = login_form.scraper(
            pair=xform_form, 
            name_user=xform_user, 
            name_pass=xform_pass)['pair']
        if len(login_inputs) > 0:
            login_post_data = {
                login_inputs[0].pop(
                    'name_user', None)[0]: value_user,
                login_inputs[0].pop(
                    'name_pass', None)[0]: value_pass
            }
            if xform_tokn is not None and len(xform_tokn) > 0:
                login_token  = login_form.scraper(
                    pair = xform_form, 
                    name = xform_tokn, 
                    value= xform_tokn)['pair']
                if len(login_token) > 0:
                    for token_pair in login_token:
                        login_post_data[
                            token_pair.pop('name', None)[0]
                            ] = token_pair.pop(
                                'value', None)[0]
                else:
                    pass
            else:
                pass
            if xform_rmbr is not None:
                login_remember = login_form.scraper(
                    pair = xform_form, 
                    name = xform_rmbr, 
                    value= xform_rmbr)['pair']
                if len(login_remember) > 0:
                    login_post_data[
                        login_remember[0]['name'][0]
                    ] = '1'
                else:
                    pass
            else:
                pass
            login_action = login_form.scraper(action=xform_form)['action']
            if len(login_action) > 0:
                login_submit = urlPrefixer(login_action[0], login_url)
            else:
                login_submit = login_url
            print(login_submit, json.dumps(login_post_data, indent=True))
            req_browser.post(login_submit, login_post_data)
            return login_check()
        else:
            print_log('error', 'LOGIN [FAIL] - Url: "%s" Could not found input fields', login_url)
            return False
    else:
        return login_check()
