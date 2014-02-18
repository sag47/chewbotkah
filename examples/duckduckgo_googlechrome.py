#!/usr/bin/env python
#Created by Sam Gleske
#Mon Feb 17 13:12:04 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
#http://www.realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/
#http://selenium-python.readthedocs.org/en/latest/getting-started.html#selenium-remote-webdriver

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities=DesiredCapabilities.CHROME)
driver.get("http://duckduckgo.com/")
driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
driver.find_element_by_id("search_button_homepage").click()
print driver.current_url
driver.quit
