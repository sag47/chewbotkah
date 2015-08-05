#!/bin/bash
#Sam Gleske
#Mon Feb 17 10:13:43 EST 2014
#Ubuntu 14.04.2 LTS
#Linux 3.13.0-58-generic x86_64
#GNU bash, version 4.3.11(1)-release (x86_64-pc-linux-gnu)
#Setup dev env
#http://www.chrisle.me/2013/08/running-headless-selenium-with-chrome/
#http://www.realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/
#libpango1.0-0 libpangox-1.0-0 libpangoxft-1.0-0
set -e

remote_selenium="http://selenium-release.storage.googleapis.com/2.47/selenium-server-standalone-2.47.1.jar"
local_selenium="/usr/local/bin/selenium-server-standalone-2.47.1.jar"

xvfb_pid="$(ps aux | grep -v grep | grep 'Xvfb :10' | awk '{print $2}')"
selenium_pid="$(ps aux | grep -v grep | grep 'java.*selenium-server-standalone' | awk '{print $2}')"

if [ "$1" = "kill" ];then
  #killall -9 Xvfb java
  kill -9 ${xvfb_pid} ${selenium_pid}
  exit
fi

if [ -e /.installed ]; then
  echo 'Already installed.'
elif [ "$USER" = "root" ];then
  echo ''
  echo 'INSTALLING'
  echo '----------'

  # Update app-get
  apt-get update

  # Install java, firefox, pip, unzip, and Xvfb
  #apt-get -y install openjdk-7-jre unzip python-pip firefox xvfb xfonts-cyrillic xfonts-100dpi xfonts-75dpi xfonts-tipa openbox
  apt-get -y install openjdk-7-jre unzip python-pip firefox xvfb xfonts-cyrillic xfonts-100dpi xfonts-75dpi xfonts-tipa
  #install selenium bindings for python
  pip install selenium
  #markdown2html prereqs
  pip install markdown2
  pip install pygments
  pip install quik


  # Download and copy the ChromeDriver to /usr/local/bin
  if [ ! -f "${local_selenium}" ];then
    wget -O "${local_selenium}" "${remote_selenium}"
  fi

  # Don't reinstall everything
  touch /.installed
else
  echo "Must be root to run install."
  exit 1
fi

if [ "$USER" = "root" ];then
  echo "Done."
  echo "Run setup.sh again as normal user for environment."
  exit
fi

# Start Xvfb, and Selenium in the background
export DISPLAY=:10

echo "Starting Xvfb ..."
if [ -z "${xvfb_pid}" ];then
#  Xvfb :10 +extension RANDR -screen 0 1366x768x24 -ac &> /dev/null &
  Xvfb :10 +extension RANDR -screen 0 1920x1080x24 -ac &> /dev/null &
else
  echo "Xvfb already running."
fi

echo "Starting Selenium ..."
if [ -z "${selenium_pid}" ];then
  nohup java -jar "${local_selenium}" &> ./selenium.log &
else
  echo "java already running."
fi

while ! nc localhost 4444 < /dev/null &>/dev/null;do
  sleep 1
done
echo "Done."
