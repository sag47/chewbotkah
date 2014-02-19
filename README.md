# Automated frontend testing

This project is a modified for public version of `chewbotkah` which runs front-end QA testing on https://www.s2disk.com/.  `chewbotkah` is a little more involved at s2disk.com but I hope that it will give you a decent place to start.

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

Currently there are only two stages.

1. Crawls a domain using a domain filter so it doesn't attempt to crawl the whole internet.  It will grab every unique URL it can script.  It will then run unit tests on the scraped `<a>` elements and check for links off-site.  There is a variable for ignoring certain domains.
2. With the list of unique URLs from the crawler visit each page and profile the page load.  Report any resources which do not return a `200` HTTP status as well as which page it occurred.

There will soon be a third stage.  It will involve visiting each target URL on every page and just checking the HTTP status of the page load (even if the link is off site).  It will only use the unique URL list from the crawler in stage 1 in which to visit pages.  It will not attempt to scrape pages it visits but just get the HTTP return status code.


# Redistribution

Because this software uses a modified component of [`selenium-profiler`](http://code.google.com/p/selenium-profiler/) it must be licensed GNU GPLv3 if it is redistributed.  This is because `selenium-profiler` is licensed under GNU GPLv3.
