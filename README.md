# Automated frontend testing

This project is a modified for public version of `chewbotkah` which runs front-end Quality Assurance (QA) testing on https://www.s2disk.com/.  `chewbotkah` is a little more involved at s2disk.com but I hope that it will give you a decent place to start for your own front end testing.  Automate all the things!

# Setup for headless testing...

Install Ubuntu 13.10 (Server or Desktop) in a VirtualBox Virtual Machine.

First run `setup.sh` as root.  Then run `setup.sh` as a normal user.

    sudo ./setup/setup_firefox.sh
    ./setup/setup_firefox.sh
    #run some basic tests against example.com
    ./frontend_test.py
    ./setup/setup_firefox.sh kill

If you run `setup.sh` twice it should autodetect running processes.

# What does it do?

It crawls a frontend and attempts to run basic quality assurance tests in stages.

Currently there are only two stages.

1. Crawls a domain using a domain filter so it doesn't attempt to crawl the whole internet.  It will grab every unique URL it can scrape.  This builds an index of domain specific pages matching the `--domain-filter` option.  Each index contains a set of links found on the page.
2. Run individual test suites on the crawled data.

## Suites

The testing stages are organized into Suites.  Currently there are only 2 suites.

* Suite 1 - This suite analyzes crawler data and checks for links that are not approved through whitelist or do not match the `--domain-filter`.  This operates on the `href` attribute of `<a>` element in the scrape data.  This does not actually perform any network requests but uses the crawl data.
* Suite 2 - This suite profiles the loading of each page on the domain from crawler data and determins if there are any non-200 HTTP status resources loading on each page.  This only tests the crawler indexes and does not check links within pages.

## Commonly encountered exceptions

* `ERROR: There was an unexpected Alert! [An error occurred! TypeError: a is null]` - This likely means that DOM elements were changed or not ready.  While all requests wait to execute until after DOMReady they can't account for JavaScript manipulating the page.  To mitigate this use the `--request-delay` option.


# Redistribution

Because this software uses a modified component of [`selenium-profiler`](http://code.google.com/p/selenium-profiler/) it must be licensed GNU GPLv3 if it is redistributed.  This is because `selenium-profiler` is licensed under GNU GPLv3.
