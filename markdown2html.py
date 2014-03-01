#!/usr/bin/env python
#Created by Sam Gleske
#Fri Feb 28 10:44:32 PST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#Python 2.7.5+
#Convert markdown to html outputting html to stdout
import os
import re
from sys import argv
from sys import exit
from sys import stderr
from markdown2 import Markdown
from quik import FileLoader

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
TEMPLATE_ROOT=PROJECT_PATH+"/assets"

if not len(argv) > 1:
  print >> stderr, "Must provide a markdown file as an argument."
  exit(1)
if not os.path.isfile(argv[1]):
  print >> stderr, "File %s does not exist." % argv[1]
  exit(1)

markdown=Markdown(extras=["fenced-code-blocks"])

with open(argv[1],'r') as f:
  htmlmarkdown=markdown.convert(f.read())

loader = FileLoader(TEMPLATE_ROOT)
template = loader.load_template('report.html')
print template.render(locals(),loader=loader).encode('utf-8')
