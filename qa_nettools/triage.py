#!/usr/bin/env python
#Created by Sam Gleske
#Wed Feb 26 12:52:09 PST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+

import re

class Page():
  def __init__(self):
    self.resource_count=0
    self.resources=[]
    self.link_count=0
    self.highpriority=False
    self.mediumpriority=False
    self.links=[]
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
  def __init__(self):
    #priorities
    self._high=[]
    self._medium=[]
    self._low=[]
    self._pages={}
    #analysis variables
    self._found404=False
    self._found401=False
    self._found30x=False
    self._included_resource=False
    self._analyzed=False
    self._resource_count={}
    self._link_count={}
    self._preseeded_links=[]
  def add_link(self,page,ref,status):
    """
      Adds a tested link on a page for the final report.
      Arguments:
        page - string - a parent page
        ref - string - a reference located on parent page
        status - string - HTTP status of the reference
    """
    #analysis logic
    if not self._found404 and status == "404":
      self._found404=True
    if not self._found401 and status == "401":
      self._found401=True
    if not self._found30x and re.match(r'^30[0-7]$',status):
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
      Arguments:
        page - string - a parent page
        ref - string - a reference located on parent page
        status - string - HTTP status of the reference
    """
    #analysis logic
    if not self._found404 and status == "404":
      self._found404=True
    if not self._found401 and status == "401":
      self._found401=True
    if not self._found30x and re.match(r'^30[0-7]$',status):
      self._found30x=True
    if not page in self._pages.keys():
      self._pages[page]=Page()
    if not ref in self._resource_count.keys():
      self._resource_count[ref]=0
    self._resource_count[ref]+=1
    if not self._included_resource and self._resource_count[ref] >= 5:
      self._included_resource=True
    self._pages[page].add_resource(ref=ref,status=status)
  def add_preseeded_links(self,links):
    """
      Add preseeded links to be included in the report.
      Arguments:
        links - list - list of links
    """
    self._preseeded_links=links
  def set_summary(self,total_tests=0,failed_tests=0,runtime="0s"):
    """
      Sets summary information to be displayed in the report.  This should be one of the last functions to run before report.
    """
    self._total_tests=total_tests
    self._failed_tests=failed_tests
    self._runtime=runtime
  def triage_items(self):
    """
      Internally categorize all items.  This should be one of the last functions to run before report.
    """
    #categorize all pages
    for page in self._pages.keys():
      if self._pages[page].highpriority:
        self._high.append(page)
      elif self._pages[page].mediumpriority:
        self._medium.append(page)
      else:
        self._low.append(page)
  def report(self,tested_links):
    """
      Generate a final report in markdown format.
      Arguments:
        tested_links - dictionary - a dictionary of links and status codes
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
      #High priority
      if len(self._high) > 0:
        report+=["### High Priority",""]
        for page in self._high:
          report+=[page,""]
          for resource,status in self._pages[page].resources:
            report+=["* Bad Resource: %s - returned HTTP status `%s`" % (resource,status)]
          for link,status in self._pages[page].links:
            report+=["* Bad HREF Link: %s - returned HTTP status `%s`" % (link,status)]
          report+=[""]
      #Medium priority
      if len(self._medium) > 0:
        report+=["### Medium Priority",""]
        for page in self._medium:
          report+=[page,""]
          for resource,status in self._pages[page].resources:
            report+=["* Bad Resource: %s - returned HTTP status `%s`" % (resource,status)]
          for link,status in self._pages[page].links:
            report+=["* Bad HREF Link: %s - returned HTTP status `%s`" % (link,status)]
          report+=[""]
      #Low priority
      if len(self._low) > 0:
        report+=["### Low Priority",""]
        for page in self._low:
          report+=[page,""]
          for resource,status in self._pages[page].resources:
            report+=["* Bad Resource: %s - returned HTTP status `%s`" % (resource,status)]
          for link,status in self._pages[page].links:
            report+=["* Bad HREF Link: %s - returned HTTP status `%s`" % (link,status)]
          report+=[""]

    #Analysis section
    report+=["# Analysis",""]

    #analysis on HTTP status codes
    if self._found404 or self._found401 or self._found30x:
      self._analyzed=True
      report+=["### Notes for status codes",""]
      if self._found404:
        report+=['* `404` "Not Found" links should be updated so they properly resolve. In the case of an archived item when the resource no longer exists it is best to remove the link but note that the link was removed.']
      if self._found30x:
        report+=['* `30x` "Redirect" links should be resolved in the HTML because it causes a noticeable performance hit on the client. Note that URL shorteners should be avoided if they\'re being used. URL shortening is better suited to social networks rather than websites.']
      if self._found401:
        report+=['* `401` "Unauthorized" links should be manually tested by logging in and verifying that the link is okay. These links may be forced into an "OK" state by preseeding the URLs.']
      report+=[""]

    #probably an included resource analysis
    if self._included_resource:
      self._analyzed=True
      report+=["### Probably an included resource",
               "",
               "The following resources have more than 5 references. They probably exist in a template or include file rather than on the page itself. If they aren't then perhaps consider treating them that way.",
               ""]
      for resource in sorted(self._resource_count,key=self._resource_count.get,reverse=True):
        if self._resource_count[resource] < 5:
          break
        report+=["* %s - found `%d` references to bad resource." % (resource,self._resource_count[resource])]
      report+=[""]

    #top 50 links analysis
    if len(self._link_count) > 0:
      self._analyzed=True
      report+=["### Top 50 referenced links",
               "",
               "Here's the top 50 or less referenced links no matter what page they're on.  If a developer or client knows the links are correct then perhaps preseed values for the next [`frontend_qa`](https://github.com/sag47/frontend_qa) run.",
               ""]
      count=0
      for link in sorted(self._link_count,key=self._link_count.get,reverse=True):
        if not count < 50:
          break
        report+=["* {link} - returned HTTP status `{status}` is referenced `{count}` times.".format(link=link,status=tested_links[link],count=self._link_count[link])]
        count+=1
      report+=[""]

    #preseeded links analysis
    if len(self._preseeded_links) > 0:
      self._analyzed=True
      report+=["### Preseeded links",
               "",
               "The following links were preseeded. The links are assumed to be OK.",
               "",
               "```"]
      report+=self._preseeded_links
      report+=["```",""]

    if not self._analyzed:
      report+=["No comment.",""]
    return '\n'.join(report)
