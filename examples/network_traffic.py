#!/usr/bin/env python
#Created by Sam Gleske
#Mon Feb 17 17:51:02 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+

import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#other dependencies
from datetime import datetime
from qa_nettools import NetworkCapture

#driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities=DesiredCapabilities.FIREFOX)
#sel=selenium.selenium('127.0.0.1', 4444, '*webdriver', 'http://example.com/')
#sel.start(['webdriver.remote.sessionid=%s' % driver.session_id, 'captureNetworkTraffic=True'])
#sel.start('captureNetworkTraffic=true',driver=driver)
sel=selenium.selenium('127.0.0.1', 4444, '*pifirefox', 'http://example.com/')
sel.start('captureNetworkTraffic=true')
sel.open('')
sel.wait_for_page_to_load(60000)
end_loading = datetime.now()
raw_xml = sel.captureNetworkTraffic('xml')
traffic_xml = raw_xml.replace('&', '&amp;').replace('=""GET""', '="GET"').replace('=""POST""', '="POST"') # workaround selenium bugs

#network traffic details
nc = NetworkCapture(traffic_xml)
num_requests = nc.get_num_requests()
total_size = nc.get_content_size()
status_map = nc.get_http_status_codes()
print status_map
file_extension_map = nc.get_file_extension_stats()
print file_extension_map
http_details = nc.get_http_details()
print http_details
# for k,v in sorted(status_map.items()):
#   print 'status %s: %s' % (k, v)
# for k,v in sorted(file_extension_map.items()):
#   print '%s: %i, %.3f kb' % (k, v[0], v[1])
# for details in http_details:
#   print '%i, %s, %s, %i, %i ms' % (details[0], details[1], details[2], details[3], details[4])
