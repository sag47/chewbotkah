## v0.1.3

* Feature: `--triage-report` option added.  A very useful feature for first testing extremely large sites.  Issues are triaged into different priorities and an analysis is provided based on the results.  Output format is markdown.
* Feature: `--crawler-excludes` option added.  If matched in an exclude crawler does not attempt to crawl the URL but skips it.
* Feature: `--preseed` option added.  URL HTTP status codes can be preseeded which are assumed to be OK.  This avoids unnecessary errors on `401` authorization pages which must be first manually tested.  The QA tester will not authorize with URLs.  This is also useful for my own testing during report generation debugging.
* Suite 2 and suite 3 have been reversed in the testing order.
* Suite 2 (formerly suite 3) fixes and misc.
  * Major bugfix suite 2.  Previously it was not working.  Since I'm only concerned with HTTP status codes I am using `urllib2` instead.
  * Bugfix don't skip 301/302 resources in test suite 2.
  * Bugfix only check `http` URLs and ignore all others in suite 2.
  * Bugfix test suite 2 now adheres to the request delay setting.
  * Performance optimization: Don't attempt to check a URL multiple times but instead store result in an index.  If it has already been checked then assume the status hasn't changed.
* Bugfix optimize suite 3 (formerly suite 2) don't attempt to profile pages which don't have an HTTP 200 status code.
* Link testing has been pulled into a separate function so it can be utilized by both test suite 2 and suite 3.  The following are bugfixes implemented in this function.
  * Bugfix grabbing HTTP status codes is now more robust with exception handling.
  * Bugfix send spoofed `User-Agent` header for more successful tests.
  * Bugfix send HTTP `Host` header for virtual hosting servers.
  * Bugfix implemented cookie handler to avoid infinite loop HTTP 301 errors.
* Bugfix default domain filter updated based on target string when `--domain-filter` option is not specified.
* Bugfix crawler not properly crawling URLs by stripping strings after `?` in the URL.  This was implemented in an earlier version and turns out to have been a mistake.

## v0.1.2

* Added test suite 3.  Test the status codes of links in HTML.
* `--request-delay` option added.  Delay the time in between network requests of crawler and unit tests.
* `--skip-suites` option added.  Now specific testing suites can be avoided or none run at all.
* `--save-crawl` option added.  Save your crawl data for later use.
* `--load-crawl` option added.  Load previously saved crawl data instead of crawling.
* Renamed `--wrong-url-excludes` to `--href-whitelist`.
* Fixed bug unicode error exception thrown when profiling pages.
* Fixed bug `301` or `302` redirects detected during test suite 2.


---
## v0.1.1

* Fixed `crawler.py` bugs in `qa_nettools` package.
* Fixed `frontend_test.py` because it had several bugs.
* Option parsing for `frontend_test.py`.  No more need for static URLs.


---
## v0.1.0

* Initial release... pretty buggy.
