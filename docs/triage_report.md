# Triage Report Feature

This feature was created for large websites (`10000+` pages) which are going
through the testing and optimizing process for the first time.  Only HTTP
`non-200` status pages, resources, or anchors are reported.  Successful tests
are omitted.  This feature provides developers with a prioritized list of pages
which have been triaged into High, Medium, and Low categories.  It also provides
an in-depth analysis on issues that have been discovered.  This document is an
explanation of that process.  Triage and analysis is a work in progress but this
is a summary of what is currently implemented.

### High priority

High priority items are categorized two ways.

1. If resources or anchor links return HTTP status `404` then it automatically
   gets categorized high priority.  Only a single resource or anchor needs to
   return `404` and the whole page is categorized.
2. If a page has more than one hundred HTTP `non-200` status resources or
   anchors regardless of type then it is categorized as high priority.

### Medium priority

All HTTP status codes that aren't high priority or don't return `401` status
codes are categorized.  If at least one resource or anchor fits the previous
description then it gets categorized.

### Low priority

A page consisting solely of HTTP status `401` pages, resources, and anchors are
categorized as low.  If even a single resource is not `401` then medium or high
priority is then categorized.  The only exception is when there are more than
one hundred `401` links and resources will this type be categorized as high
priority.

## Analysis

Depending on what status codes are encounted different opinions are offered
about that status code.  Analysis will actively look for resources that have
more than 5 references and let a develop know it might exist in an include file.
A tally of the top 50 referenced links will also be included with insight on how
to resolve the issues.
