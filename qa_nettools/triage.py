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
  _included_resource=False
  _resource_count={}
  _link_count={}
  def __init__(self):
    pass
  def set_summary(self,total_tests=0,failed_tests=0,runtime="0s"):
    """
      Sets summary information to be displayed in the report.
    """
    self._total_tests=total_tests
    self._failed_tests=failed_tests
    self._runtime=runtime
  def add_link(self,page,ref,status):
    """
      Adds a tested link on a page for the final report.
    """
    if not self._found404 and status == "404":
      self._found404=True
    elif not self._found401 and status == "401":
      self._found401=True
    elif not self._found30x and if re.match(r'^30[0-7]$',status):
      self._found30x=True
    if not page in self._pages.keys():
      self._pages[page]=Page()
    if not ref in self._link_count.keys():
      self._link_count[ref]=0
    self._link_count[ref]+=1
    self._pages[page].add_link(ref=ref,status=status)
  def add_resource(self,page,ref,status):
    """
      Adds a tested resource on a page for the final report.
    """
    if not self._found404 and status == "404":
      self._found404=True
    elif not self._found401 and status == "401":
      self._found401=True
    elif not self._found30x and if re.match(r'^30[0-7]$',status):
      self._found30x=True
    if not page in self._pages.keys():
      self._pages[page]=Page()
    if not ref in self._resource_count.keys():
      self._resource_count[ref]=0
    self._resource_count[ref]+=1
    if not self._included_resource and self._resource_count[ref] >= 5:
      self._included_resource=True
    self._pages[page].add_resource(ref=ref,status=status)
  def triage_items(self):
    #categorize all pages
    for page in self._pages.keys():
      if self._pages[page].highpriority:
        self._high.append(page)
      elif self._pages[page].mediumpriority:
        self._medium.append(page)
      else:
        self._low.append(page)
  def report(self):
    """
      Generate a final report in markdown format.
    """
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
    if len(self._high) > 0 or len(self._medium) > 0 or len(self._low) > 0:
      report+=["# Priorities",""]
      if len(self._high) > 0:
        report+=["### High Priority",""]
        for page in self._high:
          report+=[page,""]
          for resource,status in self._pages[page].resources:
            report+=["* Bad Resource: %s returned HTTP status `%s`" % (resource,status)]
          for link,status in self._pages[page].links:
            report+=["* Bad HREF Link: %s returned HTTP status `%s`" % (link,status)]
          report+=[""]
      if len(self._medium) > 0:
        report+=["### Medium Priority",""]
        for page in self._medium:
          report+=[page,""]
          for resource,status in self._pages[page].resources:
            report+=["* Bad Resource: %s returned HTTP status `%s`" % (resource,status)]
          for link,status in self._pages[page].links:
            report+=["* Bad HREF Link: %s returned HTTP status `%s`" % (link,status)]
          report+=[""]
      if len(self._low) > 0:
        report+=["### Low Priority",""]
        for page in self._low:
          report+=[page,""]
          for resource,status in self._pages[page].resources:
            report+=["* Bad Resource: %s returned HTTP status `%s`" % (resource,status)]
          for link,status in self._pages[page].links:
            report+=["* Bad HREF Link: %s returned HTTP status `%s`" % (link,status)]
          report+=[""]
    #Analysis section
    return '\n'.join(report)
