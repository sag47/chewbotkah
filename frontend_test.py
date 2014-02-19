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
from optparse import OptionParser
from urllib2 import URLError

VERSION = '0.1.2'
start_url='http://example.com/'
domain_filter='example.com'
href_whitelist=['iana.org']
delay=0.0

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

def href_suite():
  """
    Test Suite 1
    This suite analyzes crawler data and checks for links that are not approved through whitelist or do not match the domain_filter.
  """
  global pages
  suite = unittest.TestSuite()
  for page in pages.keys():
    for link in pages[page]:
      warn=True
      for rule in href_whitelist:
        if len(rule) > 0 and rule in link:
          warn=False
      if warn:
        suite.addTest(TestWrongUrls(domain_filter,page,link))
  return suite

def http_codes_suite():
  """
    Test Suite 2
    This suite profiles the loading of each page from crawler data and determins if there are any non-200 HTTP status resources loading on each page.
  """
  from time import sleep
  global delay
  sel=selenium.selenium('127.0.0.1', 4444, '*firefox', start_url)
  sel.start('captureNetworkTraffic=true')
  suite = unittest.TestSuite()
  for page in pages.keys():
    sel.open(page)
    #wait for javascript to potentially execute
    if delay != 0:
      sleep(0.3)
    raw_xml = sel.captureNetworkTraffic('xml')
    traffic_xml = raw_xml.replace('&', '&amp;').replace('=""GET""', '="GET"').replace('=""POST""', '="POST"') # workaround selenium bugs
    #network traffic details
    nc = NetworkCapture(traffic_xml)
    http_details = nc.get_http_details()
    for status,method,resource,size,time in http_details:
      if method == 'GET':
        suite.addTest(TestBadResources(page,resource,status))
  return suite

def crawl(delay=0.0):
  """
    The crawl function calls a crawler to gather data about a website which can be used by other test suites.
  """
  from sys import exit
  from qa_nettools import crawler
  global pages
  try:
    driver=webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities=DesiredCapabilities.FIREFOX)
  except URLError,e:
    print >> stderr, "Could not open connection to Selenium.  Did you start it?"
    exit(1)
  if not delay == 0:
    print >> stderr, "Crawler request delay: %f seconds" % delay
  crawler=crawler(driver,domain_filter=domain_filter,delay=delay)
  pages=crawler.crawl(start_url)
  driver.quit

if __name__ == '__main__':
  from sys import exit
  STATUS=0
  total=0
  failures=0

  #option parsing
  usage="""\
Usage: %prog --target-url URL --domain-filter STRING --wrong-url-excludes LIST

Description:
  %prog can be used to crawl domains or sub-urls to find dead links and
  resources which are bad.

Examples:
%prog -t 'https://nts.drexel.edu/modules/' -d 'nts.drexel.edu/modules' -e 'www.drexel.edu,goodwin.drexel.edu'"""
  parser = OptionParser(usage=usage,version='%prog ' + VERSION)
  parser.add_option('-d','--domain-filter',dest="domain_filter", help="This filter stops the crawler from traversing the whole web.  This will restrict the crawler to a url pattern", metavar="STRING")
  parser.add_option('-t','--target-url',dest="start_url", help="This is the target page in which the crawler will start.", metavar="URL")
  parser.add_option('-w','--href-whitelist',dest="href_whitelist", help="This is a comma separated list which enables a whitelist of any href links that don't match the --domain-filter to pass and all other references to fail.  Part of test Suite 1.", metavar="LIST")
  parser.add_option('--request-delay',dest="delay", help="Delay all requests by number of seconds.  This number can be a floating point for sub-second precision.", metavar="SECONDS")
  parser.set_defaults(domain_filter=domain_filter,start_url=start_url,href_whitelist=','.join(href_whitelist),delay=delay)
  (options, args) = parser.parse_args()
  if len(args) > 1:
    print >> stderr, "Warning, you've entered values outside of options."
  start_url=options.start_url
  domain_filter=options.domain_filter
  href_whitelist=options.href_whitelist.strip().split(',')
  delay=float(options.delay)

  starttime=datetime.now()
  print >> stderr, "\n"+"#"*70
  print >> stderr, "Target: %s" % start_url
  print >> stderr, "Domain Filter: %s" % domain_filter
  print >> stderr, "HREF Whitelist: %s" % ','.join(href_whitelist)


  print >> stderr, "\n"+"#"*70
  print >> stderr, "Crawling site..."
  crawl(delay)
  print >> stderr, "Done."

  print >> stderr, "\n"+"#"*70
  print >> stderr, "Running Test Suite 1: Check for non-authorized links based on HREF Whitelist and Domain Filter."
  result=unittest.TextTestRunner(verbosity=0).run(href_suite())
  total+=result.testsRun
  failures+=len(result.failures)
  if not result.wasSuccessful():
    STATUS=1

  print >> stderr, "\n"+"#"*70
  print >> stderr, "Running Test Suite 2: Checking HTTP status codes of all site resources."
  if not delay == 0:
    print "Request delay: %f" % delay
  try:
    result=unittest.TextTestRunner(verbosity=0).run(http_codes_suite())
  except Exception,e:
    print >> stderr, "Exception Encountered: %s" % e.message
    print >> stderr, "See documentation README for common errors or file an issue at https://github.com/sag47/frontend_qa/issues."
    exit(1)
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
