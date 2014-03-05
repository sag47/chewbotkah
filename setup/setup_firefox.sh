#!/bin/bash
#Sam Gleske
#Mon Feb 17 10:13:43 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#GNU bash, version 4.2.45(1)-release (x86_64-pc-linux-gnu)
#Setup dev env
#http://www.chrisle.me/2013/08/running-headless-selenium-with-chrome/
#http://www.realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/
#libpango1.0-0 libpangox-1.0-0 libpangoxft-1.0-0
set -e

if [ "$1" = "kill" ];then
  #killall -9 Xvfb java firefox openbox
  killall -9 Xvfb java firefox
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
  cd /tmp
  if [ ! -f "selenium-server-standalone-2.39.0.jar" ];then
    wget "https://selenium.googlecode.com/files/selenium-server-standalone-2.39.0.jar"
  fi
  mv -f selenium-server-standalone-2.39.0.jar /usr/local/bin

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
if ! pgrep Xvfb &> /dev/null;then
#  Xvfb :10 +extension RANDR -screen 0 1366x768x24 -ac &> /dev/null &
  Xvfb :10 +extension RANDR -screen 0 1920x1080x24 -ac &> /dev/null &
else
  echo "Xvfb already running."
fi
#echo "Starting openbox window manager..."
#if ! pgrep openbox &> /dev/null;then
#  openbox &> /dev/null &
#else
#  echo "openbox already running."
#fi
firefox &>/dev/null &
echo "Starting Selenium ..."
cd /usr/local/bin
if ! pgrep java &> /dev/null;then
  nohup java -jar ./selenium-server-standalone-2.39.0.jar &> /dev/null &
else 
  echo "java already running."
fi
echo "Done."
