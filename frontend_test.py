#!/usr/bin/env python
#Created by Sam Gleske
#Mon Feb 17 17:05:54 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
import httplib
import json
import qa_nettools
import re
import selenium
import socket
import unittest
import urllib2
from cookielib import CookieJar
from datetime import datetime
from optparse import OptionParser
from os.path import isfile
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sys import exit
from sys import stderr
from time import sleep

VERSION = '0.1.3'
start_url='http://example.com/'
domain_filter='example.com'
href_whitelist=['']
delay=0.0
skip_suites=[]
crawler_excludes='.exe,.dmg'
tested_links={}
preseed={}

def get_link_status(url):
  """
    Gets the HTTP status of the url or returns an error associated with it.  Always returns a string.
  """
  https=False
  url=re.sub(r'(.*)#.*$',r'\1',url)
  url=url.split('/',3)
  if len(url) > 3:
    path='/'+url[3]
  else:
    path='/'
  if url[0] == 'http:':
    port=80
  elif url[0] == 'https:':
    port=443
    https=True
  if ':' in url[2]:
    host=url[2].split(':')[0]
    port=url[2].split(':')[1]
  else:
    host=url[2]
  try:
    headers={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0',
             'Host':host
             }
    if https:
      conn=httplib.HTTPSConnection(host=host,port=port,timeout=10)
    else:
      conn=httplib.HTTPConnection(host=host,port=port,timeout=10)
    conn.request(method="HEAD",url=path,headers=headers)
    response=str(conn.getresponse().status)
    conn.close()
  except socket.gaierror,e:
    response="Socket Error (%d): %s" % (e[0],e[1])
  except StandardError,e:
    if hasattr(e,'getcode') and len(e.getcode()) > 0:
      response=str(e.getcode())
    if hasattr(e, 'message') and len(e.message) > 0:
      response=str(e.message)
    elif hasattr(e, 'msg') and len(e.msg) > 0:
      response=str(e.msg)
    elif type('') == type(e):
      response=e
    else:
      response="Exception occurred without a good error message.  Manually check the URL to see the status.  If it is believed this URL is 100% good then file a issue for a potential bug."
  return response

class TestWrongUrls(unittest.TestCase):
  """
    Test function part of test suite 1
  """
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

class TestBadLinks(unittest.TestCase):
  """
    Test function part of test suite 2
  """
  def __init__(self,page,link,status):
    super(TestBadLinks,self).__init__()
    self.page=page
    self.status=status
    self.link=link
  def runTest(self):
    self.assertEqual(self.status,
                     "200",
                     msg="\n\nOn page: %(page)s\nBad Link: %(link)s\nReturned HTTP Status: %(status)s" % {
                         'page': self.page,
                         'link': self.link,
                         'status': self.status})

class TestBadResources(unittest.TestCase):
  """
    Test function part of test suite 3
  """
  def __init__(self,page,resource,status):
    super(TestBadResources,self).__init__()
    self.page=page
    self.status=status
    self.resource=resource
  def runTest(self):
    self.assertEqual(self.status,
                     "200",
                     msg="\n\nOn page: %(page)s\nResource: %(resource)s\nReturned HTTP Status: %(status)s" % {
                         'page': self.page,
                         'resource': self.resource,
                         'status': self.status})

def href_suite():
  """
    Test Suite 1
    This suite analyzes crawler data and checks for links that are not approved through whitelist or do not match the domain_filter.
  """
  global pages
  suite = unittest.TestSuite()
  for page in pages.keys():
    if page == '__settings__':
      continue
    for link in pages[page]:
      warn=True
      for rule in href_whitelist:
        if len(rule) > 0 and rule in link:
          warn=False
      if warn:
        suite.addTest(TestWrongUrls(domain_filter,page,link))
  return suite

def link_status_codes_suite():
  """
    Test Suite 2
    This suite loads every link reference on every page and checks for bad links in the HTML.  These are inline href <a> links in a page.
  """
  #good tested and bad_tested links are so the program
  #can skip links rather than double test
  #link is the key, http status code is the value
  global tested_links
  global triage
  global options
  suite = unittest.TestSuite()
  for page in pages.keys():
    if page == '__settings__':
      continue
    if not re.sub(r'(.*)#.*$',r'\1',page) in tested_links:
      if not delay == 0:
        sleep(delay)
      tested_links[re.sub(r'(.*)#.*$',r'\1',page)]=get_link_status(page)
    if not tested_links[page] == "200":
      #don't bother testing links on a non-200 status page
      continue
    for linked_page in pages[page]:
      if linked_page[0:4] == 'http':
        if linked_page in tested_links.keys():
          #if the URL has already been tested then skip testing and give the status
          suite.addTest(TestBadLinks(page,linked_page,tested_links[linked_page]))
        else:
          if not delay == 0:
            sleep(delay)
          result=get_link_status(linked_page)
          suite.addTest(TestBadLinks(page,linked_page,result))
          tested_links[linked_page]=result
        if len(options.triage_report) > 0 and not tested_links[linked_page] == "200":
          triage.add_link(page,linked_page,tested_links[linked_page])
  return suite

def resource_status_codes_suite():
  """
    Test Suite 3
    This suite profiles the loading of each page from crawler data and determins if there are any non-200 HTTP status resources loading on each page.
  """
  global tested_links
  global triage
  global options
  try:
    sel=selenium.selenium('127.0.0.1', 4444, '*firefox', start_url)
    sel.start('captureNetworkTraffic=true')
  except socket.error,e:
    print >> stderr, "Could not open connection to Selenium.  Did you start it?"
    exit(1)
  suite = unittest.TestSuite()
  for page in pages.keys():
    if page == '__settings__':
      continue
    if not re.sub(r'(.*)#.*$',r'\1',page) in tested_links:
      tested_links[re.sub(r'(.*)#.*$',r'\1',page)]=get_link_status(page)
    if not tested_links[re.sub(r'(.*)#.*$',r'\1',page)] == "200":
      #don't bother testing resources on a non-200 status page
      continue
    sel.open(page)
    #wait for javascript to potentially execute
    if not delay == 0:
      sleep(delay)
    raw_xml = sel.captureNetworkTraffic('xml')
    traffic_xml = raw_xml.replace('&', '&amp;').replace('=""GET""', '="GET"').replace('=""POST""', '="POST"') # workaround selenium bugs
    #network traffic details
    nc = qa_nettools.NetworkCapture(traffic_xml.encode('ascii', 'ignore'))
    http_details = nc.get_http_details()
    for status,method,resource,size,time in http_details:
      if method == 'GET':
        suite.addTest(TestBadResources(page,resource,str(status)))
        if len(options.triage_report) > 0 and not str(status) == "200":
          triage.add_resource(page,resource,str(status))
  return suite

def crawl():
  """
    The crawl function calls a crawler to gather data about a website which can be used by other test suites.
  """
  global pages
  try:
    driver=webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities=DesiredCapabilities.FIREFOX)
  except urllib2.URLError,e:
    print >> stderr, "Could not open connection to Selenium.  Did you start it?"
    exit(1)
  if not delay == 0:
    print >> stderr, "Crawler request delay: %f seconds" % delay
  crawler=qa_nettools.crawler(driver,domain_filter=domain_filter,delay=delay,excludes=crawler_excludes)
  pages=crawler.crawl(start_url)
  driver.quit

if __name__ == '__main__':
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
  parser.add_option('-t','--target-url',dest="start_url", help="This is the target page in which the crawler will start.", metavar="URL")
  parser.add_option('-d','--domain-filter',dest="domain_filter", help="This filter stops the crawler from traversing the whole web.  This will restrict the crawler to a url pattern.", metavar="STRING")
  parser.add_option('-w','--href-whitelist',dest="href_whitelist", help="This is a comma separated list which enables a whitelist of any href links that don't match the --domain-filter to pass and all other references to fail.  Part of test Suite 1.", metavar="LIST")
  parser.add_option('--request-delay',dest="delay", help="Delay all requests by number of seconds.  This number can be a floating point for sub-second precision.", metavar="SECONDS")
  parser.add_option('--skip-suites',dest="skip_suites", help="Skip test suites to avoid running them.  Comma separated list of numbers or ranges.", metavar="NUM")
  parser.add_option('--save-crawl',dest="save_crawl", help="Save your crawl data to a JSON formatted file.", metavar="FILE")
  parser.add_option('--load-crawl',dest="load_crawl", help="Load JSON formatted crawl data instead of crawling.", metavar="FILE")
  parser.add_option('--crawler-excludes',dest="crawler_excludes", help="Comma separated word list.  If word is in URL then the crawler won't attempt to crawl it.", metavar="LIST")
  parser.add_option('--preseed',dest="preseed", help="JSON formatted file with a default list of links and status to override for testing.", metavar="FILE")
  parser.add_option('--triage-report',dest="triage_report", help="Generate a report with all errors triaged in a markdown format.", metavar="FILE")
  parser.set_defaults(domain_filter=domain_filter,
                      start_url=start_url,
                      href_whitelist=','.join(href_whitelist),
                      delay=delay,
                      skip_suites=','.join(skip_suites),
                      save_crawl='',
                      load_crawl='',
                      crawler_excludes=crawler_excludes,
                      preseed="",
                      triage_report="")
  (options, args) = parser.parse_args()
  if len(args) > 1:
    print >> stderr, "Warning, you've entered values outside of options."
  if len(options.save_crawl) > 0 and len(options.load_crawl) > 0:
    print >> stderr, "Incompatible options selected.  May not load a crawl and save a crawl."
    exit(1)
  if len(options.load_crawl) > 0 and not isfile(options.load_crawl):
    print >> stderr, "Crawl file does not exist!"
    exit(1)
  if len(options.preseed) > 0 and not isfile(options.preseed):
    print >> stderr, "Preseed file does not exist."
    exit(1)
  start_url=options.start_url
  if not options.start_url == 'http://example.com/' and options.domain_filter == 'example.com':
    domain_filter=options.start_url.split('/')[2]
  else:
    domain_filter=options.domain_filter
  href_whitelist=options.href_whitelist.strip().split(',')
  crawler_excludes=options.crawler_excludes
  delay=float(options.delay)
  for suite in options.skip_suites.strip().split(','):
    if  re.match('^[0-9]+-[0-9]+$',suite):
      for x in range(int(suite.split('-')[0]),int(suite.split('-')[1])+1):
        skip_suites.append(str(x))
    else:
      skip_suites.append(suite)

  if len(options.triage_report) > 0:
    triage=qa_nettools.triage()
  starttime=datetime.now()
  print >> stderr, "\n"+"#"*70
  if len(options.preseed):
    try:
      print >> stderr, "Preseeding results."
      with open(options.preseed,'r') as f:
        tested_links=preseed=json.load(f)
      if len(options.triage_report) > 0:
        triage.add_preseeded_links(preseed.keys())
    except Exception,e:
      print >> stderr, "Not a valid preseed data file!  Must be in JSON format.  Aborting."
      exit(1)
  if len(options.load_crawl) == 0:
    print >> stderr, "Target: %s" % start_url
    print >> stderr, "Domain Filter: %s" % domain_filter

  #start of crawl stage
  if len(options.load_crawl) == 0:
    print >> stderr, "Crawling site..."
    print >> stderr, "Crawler Excludes: %s" % crawler_excludes
    crawl()
    if len(options.save_crawl) > 0:
      print >> stderr, "Saving crawl data: %s" % options.save_crawl
      try:
        with open(options.save_crawl,'w') as f:
          json.dump(pages,f)
      except Exception,e:
        print >> stderr, "Error: %s" % e.message
  else:
    print >> stderr, "Load crawl data: %s" % options.load_crawl
    try:
      with open(options.load_crawl,'r') as f:
        pages=json.load(f)
    except Exception,e:
      print >> stderr, "Not a valid crawl data file!  Must be in JSON format.  Aborting."
      exit(1)
  #end of crawl stage

  #start of suite 1
  if not '1' in skip_suites:
    print >> stderr, "\n"+"#"*70
    print >> stderr, "Running Test Suite 1: Check for non-authorized links based on HREF Whitelist and Domain Filter."
    print >> stderr, "HREF Whitelist: %s" % ','.join(href_whitelist)
    result=unittest.TextTestRunner(verbosity=0).run(href_suite())
    total+=result.testsRun
    failures+=len(result.failures)
    if not result.wasSuccessful():
      STATUS=1
  #end of suite 1

  #start of suite 2
  if not '2' in skip_suites:
    print >> stderr, "\n"+"#"*70
    print >> stderr, "Running Test Suite 2: Checking HTTP status codes of all inline links."
    if not delay == 0:
      print >> stderr, "Request delay: %f" % delay
    result=unittest.TextTestRunner(verbosity=0).run(link_status_codes_suite())
    total+=result.testsRun
    failures+=len(result.failures)
    if not result.wasSuccessful():
      STATUS=1
  #end of suite 2

  #start of suite 3
  if not '3' in skip_suites:
    print >> stderr, "\n"+"#"*70
    print >> stderr, "Running Test Suite 3: Checking HTTP status codes of all site resources."
    if not delay == 0:
      print >> stderr, "Request delay: %f" % delay
    try:
      result=unittest.TextTestRunner(verbosity=0).run(resource_status_codes_suite())
    except Exception,e:
      print >> stderr, "Exception Encountered: %s" % e.message
      print >> stderr, "See documentation README for common errors or file an issue at https://github.com/sag47/frontend_qa/issues."
      exit(1)
    total+=result.testsRun
    failures+=len(result.failures)
    if not result.wasSuccessful():
      STATUS=1
  #end of suite 3

  endtime=datetime.now()
  print >> stderr, "\n"+"#"*70
  print >> stderr, "Total: Ran %s tests." % str(total)
  if not failures == 0:
    print >> stderr, "%(failures)d failed tests." % {'failures': failures}
  elif not total == 0:
    print >> stderr, "All OK!"
  mins=(endtime-starttime).seconds/60
  secs=(endtime-starttime).seconds
  microsecs=(endtime-starttime).microseconds/1000000.0
  if mins > 0:
    runtime="%(mins)dm %(secs)ss" % {'mins': mins,'secs':secs-(mins*60)+microsecs}
  else:
    runtime="%(secs)ss" % {'secs':secs+microsecs}
  print >> stderr, "Elapsed time: %(runtime)s" % {'runtime':runtime}
  if len(options.triage_report) > 0:
    print >> stderr, "Generating triage report."
    triage.set_summary(total_tests=total,failed_tests=failures,runtime=runtime,request_delay=delay)
    triage.triage_items()
    with open(options.triage_report,'w') as f:
      f.write(triage.report(tested_links=tested_links))

  exit(STATUS)
