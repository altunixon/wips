#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time
from helpers.misc import countdown, print_log, print_color
from vars.conf_pixiv import xpath_pview_tutorial1, xpath_pview_tutorial2, xpath_pview_type_show

class macros():
    def __init__(self, mah_browser, **options):
        self.browser = mah_browser
        self.verbose = options.pop('verbose', False)
        self._brint = print_log if not options.pop('color', False) else print_color
        self.dump = options.pop('dump', None)

    def meltdown(self, exception_obj, meltdown_trigger=False):
        if self.dump is not None and not os.path.isfile(self.dump):
            with open(self.dump, 'w+') as dmp_html:
                dmp_html.write(self.browser.read())
        else:
            pass
        self._brint(
            'warn' if not meltdown_trigger else 'err', 
            'MACRO [EXCP] - Exception:\n%s\n%s', 
            str(exception_obj), 
            '=' * 21
        )
        if meltdown_trigger:
            raise exception_obj
        else:
            pass

    def cooldown(self, cooldown_time):
        if cooldown_time < 1:
            pass
        else:
            if self.verbose:
                countdown(cooldown_time, txt='Cooldown in:')
            else:
                time.sleep(cooldown_time)

    def obscure_click(self, **options):
        click_meltdown = options.pop('meltdown', False)
        click_show = options.pop('show', False)
        try:
            if click_show:
                self.dom_click(xpath_pview_type_show, meltdown=click_meltdown, wait=1)
            else:
                pass
            if self.dom_click(xpath_pview_tutorial1, meltdown=False, wait=1):
                self.dom_click(xpath_pview_tutorial2, meltdown=False, wait=1)
            else:
                pass
            return True
            # return self.dom_click(xpath_pview_type_show, meltdown=click_meltdown, wait=1)
        except Exception as excp:
            self._brint('err', 'CLICK [EXCP] - Obscure Click Exception:\n%s\nFrom: obscure_click()', str(excp))
            return False

    def dom_input(self, input_xpath, input_value, **options):
        input_strict = options.pop('meltdown', False)
        input_delay = options.pop('delay', 1)
        input_wait = options.pop('wait', 3)
        try:
            input_element = self.browser.driver.find_element_by_xpath(input_xpath)
            self.browser.driver.implicitly_wait(input_delay)
            input_element.click()
            input_element.send_keys(input_value)
            self.cooldown(input_wait)
            return True
        except Exception as excp:
            self._brint('err', 'INPUT [INSR] - Could not Input value into <%s>' % input_xpath)
            self.meltdown(excp, input_strict)
            return False

    def dom_click(self, element_xpath, **options):
        clicky_hover = options.pop('hover', False)
        clicky_strict = options.pop('meltdown', False)
        clicky_cooldown = options.pop('wait', 0)
        clicky_whatis = options.pop('desc', 'MISC')
        clicky_element = self.browser.driver.find_elements_by_xpath(element_xpath)
        if len(clicky_element) > 0:
            self._brint('debug', 'CLICK [XELM] - Found (%s) %s Clickable Element(s), Clicking 1st one: "%s" @ "%s"', 
                len(clicky_element), clicky_whatis, clicky_element[0].text, self.browser.driver.current_url)
            try:
                if clicky_hover:
                    self._brint('debug', 'HOVER [XELM] - Hovering Over Element: "%s" @ "%s"', 
                        clicky_element[0].text, self.browser.driver.current_url)
                    from selenium.webdriver.common.action_chains import ActionChains
                    action = ActionChains(self.browser.driver)
                    action.move_to_element(clicky_element[0]).perform()
                    self.cooldown(3)
                else:
                    pass
                clicky_element[0].click()
                self.cooldown(clicky_cooldown)
                return True
            except Exception as excp:
                self._brint('err', 'CLICK [XELM] - Element %s [%s] XPath: <%s> Could not be Clicked.\nTry visit: "%s" on your browser for details', 
                    clicky_whatis, clicky_element[0].text, element_xpath, self.browser.driver.current_url)
                self.meltdown(excp, clicky_strict)
                return False
        else:
            self._brint('warn', 'CLICK [XPTH] - NotFound %s Clickable Element by XPath: <%s>\nTry visit: "%s" on your browser for details', 
                clicky_whatis, element_xpath, self.browser.driver.current_url)
            self.meltdown(Exception('Element NotFound<%s>' % element_xpath), clicky_strict)
            return False
