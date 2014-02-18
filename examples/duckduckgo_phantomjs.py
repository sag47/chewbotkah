#!/usr/bin/env
#Created by Sam Gleske
#Mon Feb 17 19:24:04 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
#http://www.realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/
from selenium import webdriver
driver = webdriver.PhantomJS()
driver.get("http://duckduckgo.com/")
driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
driver.find_element_by_id("search_button_homepage").click()
print driver.current_url
driver.quit
