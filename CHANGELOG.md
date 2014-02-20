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
