#!/usr/bin/env python
#Created by Sam Gleske
#Wed Feb 26 12:52:09 PST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+

class triage():
  """
  Triage report generator attempts to make sense of the QA results for the layman web developer.
  """
  def __init__(self,total_tests=0,failed_tests=0,runtime="0s"):
    self.total_tests=total_tests
    self.failed_tests=failed_tests
    self.runtime=runtime
  def report(self):
    report=["# Summary",""]
    report+=["Unit tests",
             "",
             "* Passed: `%d`" % (self.total_tests-self.failed_tests),
             "* Failed: `%d`" % self.failed_tests,
             "* Total: `%d`" % self.total_tests,
             "",
             "Run time: `%s`" % self.runtime]
    return '\n'.join(report)
