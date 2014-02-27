#!/usr/bin/env python
#Created by Sam Gleske
#Wed Feb 26 12:52:09 PST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+

import re

class Page():
  resource_count=0
  resources=[]
  link_count=0
  highpriority=False
  mediumpriority=False
  links=[]
  def __init__(self):
    pass
  def add_resource(self,ref,status):
    #triage the resource
    if not self.highpriority and status == "404":
      self.highpriority=True
    if not self.mediumpriority and not status == "401":
      self.mediumpriority=True
    #increment the resource count
    self.resource_count+=1
    if (self.resource_count+self.link_count) >= 5:
      self.highpriority=True
    #append the resource and status
    self.resources.append((ref,status))

  def add_link(self,ref,status):
    #triage the link
    if not self.highpriority and status == "404":
      self.highpriority=True
    if not self.mediumpriority and not status == "401":
      self.mediumpriority=True
    #increment the resource count
    self.link_count+=1
    if (self.resource_count+self.link_count) >= 5:
      self.highpriority=True
    #append the resource and status
    self.links.append((ref,status))
    pass
  def add_screenshot(self,data):
    """
    Not implemented.
    """
    pass

class triage():
  """
  Triage report generator attempts to make sense of the QA results for the layman web developer.
  """
  #priorities
  _high=[]
  _medium=[]
  _low=[]
  _pages={}
  _found404=False
  _found401=False
  _found30x=False
  def __init__(self):
    pass
  def set_summary(self,total_tests=0,failed_tests=0,runtime="0s"):
    self._total_tests=total_tests
    self._failed_tests=failed_tests
    self._runtime=runtime
  def add_link(self,page,ref,status):
    if not self._found404 and status == "404":
      self._found404=True
    elif not self._found401 and status == "401":
      self._found401=True
    elif not self._found30x and if re.match(r'^30[0-7]$',status):
      self._found30x=True
    if not page in self._pages.keys():
      self._pages[page]=Page()
    self._pages[page].add_link(ref=ref,status=status)
  def add_resource(self,page,ref,status):
    if not self._found404 and status == "404":
      self._found404=True
    elif not self._found401 and status == "401":
      self._found401=True
    elif not self._found30x and if re.match(r'^30[0-7]$',status):
      self._found30x=True
    if not page in self._pages.keys():
      self._pages[page]=Page()
    self._pages[page].add_resource(ref=ref,status=status)
  def report(self):
    #Report Summary
    report=["# Summary",""]
    report+=["Unit tests",
             "",
             "* Passed: `%d`" % (self._total_tests-self._failed_tests),
             "* Failed: `%d`" % self._failed_tests,
             "* Total: `%d`" % self._total_tests,
             "* Run time: `%s`" % self._runtime,
             "",
             "Issues are triaged into three categories: High, Medium, Low.  Each issue is in the form of a link to the page that contains the issue followed by a bullet point list of issues discovered on that page.  There may be an analysis section at the end of this document which might be worth checking out before viewing prioritized issues.  For a description of the HTTP status codes contained in this document please see [rfc2616.10](http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html).",
             ""]
    #Prioritized items
    return '\n'.join(report)
