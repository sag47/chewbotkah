#!/usr/bin/env python
#Created by Sam Gleske
#Mon Feb 17 21:16:53 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sys import stderr
from time import sleep

class crawler():
  """
    Crawls a website and creates an index of all links.  The index is a python dictionary using each unique URL as a key.  Within each key entry is a list of URLs found on that page.  A URL on the page is discovered by looking for <a> elements by tag name and extracted by getting the href attribute.

    Arguments:
      driver - A selenium webdriver object.
      domain_filter - a string that will be used to search in other strings to restrict the crawler to this filter.

    Returned object is like.
    {
      'http://example.com/': ['http://www.iana.org/domains/example']
    }

    Careful, this script is designed to crawl a whole website and find all pages.  If a site is large enough consider splitting up the work and refining the domain_filter.
  """
  pages={}
  def __init__(self,driver,domain_filter="example.com",delay=0):
    if domain_filter == "example.com":
      print >> stderr, "Warning: your crawler is initialized with example.com."
    self.driver=driver
    self.domain_filter=domain_filter
    self.delay=delay
  def _consume(self,url):
    try:
      if '?' in url:
        url=url.split('?')[0]
      if url in self.pages:
        return ''
      self.pages[url]=[]
      self.driver.get(url)
      tags=[]
      if self.delay > 0:
        sleep(self.delay)
      if len(self.driver.find_elements_by_tag_name('a')) > 0:
        for tag in self.driver.find_elements_by_tag_name('a'):
          if not type(tag.get_attribute('href')) == type(None):
            self.pages[url].append(tag.get_attribute('href'))
      if len(self.pages[url]) > 0:
        for link in self.pages[url]:
          if (self.domain_filter in link) and not ('#' in link) and not (link in self.pages.keys()):
            self._consume(link)
    except Exception,e:
      pass
  def crawl(self,url):
    self._consume(url)
    return self.pages

if __name__ == '__main__':
  driver=webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities=DesiredCapabilities.FIREFOX)
  crawler=crawler(driver,domain_filter="example.com")
  pages=crawler.crawl('http://example.com/')
  print pages
