#!/usr/bin/env python
#Created by Sam Gleske
#Mon Feb 17 17:51:02 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from qa_nettools import crawler
driver=webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities=DesiredCapabilities.FIREFOX)
crawler=crawler(driver,domain_filter="example.com")
pages=crawler.crawl('http://example.com/')
for page in pages.keys():
  for link in pages[page]:
    print "page:%(page)s, link:%(link)s" % {'page':page,'link':link}
