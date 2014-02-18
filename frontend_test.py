#!/usr/bin/env python
#Created by Sam Gleske
#Mon Feb 17 17:05:54 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
import unittest
import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from qa_nettools import NetworkCapture
from datetime import datetime
from sys import stderr

start_url='http://example.com/'
domain_filter='example.com'
wrong_url_excludes=['iana.org']

class TestWrongUrls(unittest.TestCase):
  def __init__(self,domain_filter,page,link):
    super(TestWrongUrls,self).__init__()
    self.domain_filter=domain_filter
    self.page=page
    self.link=link
  def runTest(self):
    self.assertIn(self.domain_filter,
                  self.link,
                  msg="\n\nOn page: %(page)s\nLink pointing off domain: %(link)s" % {
                      'page': self.page,
                      'link': self.link})

class TestBadResources(unittest.TestCase):
  def __init__(self,page,resource,status):
    super(TestBadResources,self).__init__()
    self.page=page
    self.status=status
    self.resource=resource
  def runTest(self):
    self.assertEqual(int(self.status),
                     200,
                     msg="\n\nOn page: %(page)s\nResource: %(resource)s\nReturned HTTP Status: %(status)s" % {
                         'page': self.page,
                         'resource' :self.resource,
                         'status': self.status})

def crawl_suite():
  from qa_nettools import crawler
  global pages
  driver=webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities=DesiredCapabilities.FIREFOX)
  crawler=crawler(driver,domain_filter=domain_filter)
  pages=crawler.crawl(start_url)
  driver.quit
  suite = unittest.TestSuite()
  for page in pages.keys():
    for link in pages[page]:
      warn=True
      for rule in wrong_url_excludes:
        if len(rule) > 0 and rule in link:
          warn=False
      if warn:
        suite.addTest(TestWrongUrls(domain_filter,page,link))
  return suite

def http_codes_suite():
  from sys import exit
  from time import sleep
  sel=selenium.selenium('127.0.0.1', 4444, '*firefox', start_url)
  sel.start('captureNetworkTraffic=true')
  suite = unittest.TestSuite()
  for page in pages.keys():
    sel.open(page)
    #wait for javascript to potentially execute
    sleep(0.1)
    raw_xml = sel.captureNetworkTraffic('xml')
    traffic_xml = raw_xml.replace('&', '&amp;').replace('=""GET""', '="GET"').replace('=""POST""', '="POST"') # workaround selenium bugs
    #network traffic details
    nc = NetworkCapture(traffic_xml)
    http_details = nc.get_http_details()
    for status,method,resource,size,time in http_details:
      if method == 'GET':
        suite.addTest(TestBadResources(page,resource,status))
  return suite

if __name__ == '__main__':
  from sys import exit
  STATUS=0
  total=0
  failures=0

  #option parsing

  starttime=datetime.now()
  print >> stderr, "\n"+"#"*70
  print >> stderr, "Target: %s" % start_url
  print >> stderr, "Domain Filter: %s" % domain_filter
  print >> stderr, "Wrong URL Excludes: %s" % ','.join(wrong_url_excludes)
  print >> stderr, "Crawling site for bad links in html..."
  result=unittest.TextTestRunner(verbosity=0).run(crawl_suite())
  total+=result.testsRun
  failures+=len(result.failures)
  if not result.wasSuccessful():
    STATUS=1

  print >> stderr, "\n"+"#"*70
  print >> stderr, "Checking HTTP status codes of all site resources..."
  result=unittest.TextTestRunner(verbosity=0).run(http_codes_suite())
  total+=result.testsRun
  failures+=len(result.failures)
  if not result.wasSuccessful():
    STATUS=1

  endtime=datetime.now()
  print >> stderr, "\n"+"#"*70
  print >> stderr, "Total: Ran %s tests." % str(total)
  if failures == 0:
    print >> stderr, "All OK!"
  else:
    print >> stderr, "%(failures)d failed tests." % {'failures': failures}
  mins=(endtime-starttime).seconds/60
  secs=(endtime-starttime).seconds
  microsecs=(endtime-starttime).microseconds/1000000.0
  if mins > 0:
    print >> stderr, "Elapsed time: %(mins)dm %(secs)ss" % {'mins': mins,'secs':secs-(mins*60)+microsecs}
  else:
    print >> stderr, "Elapsed time: %(secs)ss" % {'secs':secs+microsecs}
  exit(STATUS)
