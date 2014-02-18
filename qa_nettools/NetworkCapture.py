#!/usr/bin/env python
#Modified by Sam Gleske
#Mon Feb 17 20:00:05 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
#I have modified portions of the original NetworkCapture object.

#  http://code.google.com/p/selenium-profiler/
#  Selenium Web/HTTP Profiler
#  Copyright (c) 2009-2011 Corey Goldberg (corey@goldb.org)
#  License: GNU GPLv3
import json
from datetime import datetime
import xml.etree.ElementTree as etree

class NetworkCapture(object):
  """
    NetworkCapture object designed to eat XML from selenium XML.
  """
  def __init__(self, xml_blob):
    """
      xml_blob - selenium xml output
    """
    self.xml_blob = xml_blob
    self.dom = etree.ElementTree(etree.fromstring(xml_blob))
  def get_json(self):
    results = []
    for child in self.dom.getiterator():
      if child.tag == 'entry':
        url = child.attrib.get('url')
        start_time = child.attrib.get('start')
        time_in_millis = child.attrib.get('timeInMillis')
        results.append((url, start_time, time_in_millis))
    return json.dumps(results)
  def get_content_size(self):  # total kb passed through the proxy
    byte_sizes = []
    for child in self.dom.getiterator():
      if child.tag == 'entry':
        byte_sizes.append(child.attrib.get('bytes'))
    total_size = sum([int(bytes) for bytes in byte_sizes]) / 1000.0
    return total_size
  def get_num_requests(self):
    num_requests = 0
    for child in self.dom.getiterator():
      if child.tag == 'entry':
        num_requests += 1
    return num_requests
  def get_http_status_codes(self):
    status_map = {}
    for child in self.dom.getiterator():
      if child.tag == 'entry':
        try:
          status_map[child.attrib.get('statusCode')] += 1
        except KeyError:
          status_map[child.attrib.get('statusCode')] = 1
    return status_map
  def get_http_details(self):
    http_details = []
    for child in self.dom.getiterator():
      if child.tag == 'entry':
        url = child.attrib.get('url') + '?'
        url_stem = url.split('?')[0]
        #doc = '/' + url_stem.split('/')[-1]
        if 'favicon.ico' in url_stem:
          continue
        doc = url_stem
        status = int(child.attrib.get('statusCode'))
        method = child.attrib.get('method').replace("'", '')
        size = int(child.attrib.get('bytes'))
        time = int(child.attrib.get('timeInMillis'))
        http_details.append((status, method, doc, size, time))
    http_details.sort(cmp=lambda x,y: cmp(x[3], y[3])) # sort by size
    return http_details
  def get_file_extension_stats(self):
    file_extension_map = {}  # k=extension v=(count,size) 
    for child in self.dom.getiterator():
      if child.tag == 'entry':
        size = float(child.attrib.get('bytes')) / 1000.0
        url = child.attrib.get('url') + '?'
        url_stem = url.split('?')[0]
        doc = url_stem.split('/')[-1]
        if '.' in doc:
          file_extension = doc.split('.')[-1]
        else:
          file_extension = 'unknown'
        try:
          file_extension_map[file_extension][0] += 1
          file_extension_map[file_extension][1] += size
        except KeyError:
          file_extension_map[file_extension] = [1, size]
    return file_extension_map
  def get_network_times(self):
    timings = []
    start_times = []
    end_times = []
    for child in self.dom.getiterator():
      if child.tag == 'entry':
        timings.append(child.attrib.get('timeInMillis'))
        start_times.append(child.attrib.get('start')) 
        end_times.append(child.attrib.get('end'))
    start_times.sort()
    end_times.sort()
    start_first_request = self.convert_time(start_times[0])
    end_first_request = self.convert_time(end_times[0])
    end_last_request = self.convert_time(end_times[-1])
    return (start_first_request, end_first_request, end_last_request)
  def convert_time(self, date_string):
    if '-' in date_string: split_char = '-'
    else: split_char = '+'
    dt = datetime.strptime(''.join(date_string.split(split_char)[:-1]), '%Y%m%dT%H:%M:%S.%f')  
    return dt

