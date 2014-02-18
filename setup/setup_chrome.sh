#!/bin/bash
#Sam Gleske
#Mon Feb 17 10:13:43 EST 2014
#Ubuntu 13.10
#Linux 3.11.0-12-generic x86_64
#GNU bash, version 4.2.45(1)-release (x86_64-pc-linux-gnu)
#Setup dev env
#http://www.chrisle.me/2013/08/running-headless-selenium-with-chrome/
#http://www.realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/
set -e

if [ "$1" = "kill" ];then
  killall -9 Xvfb java chrome chromedriver
  exit
fi

if [ -e /.installed ]; then
  echo 'Already installed.'
elif [ "$USER" = "root" ];then
  echo ''
  echo 'INSTALLING'
  echo '----------'

  # Add Google public key to apt
  wget -q -O - "https://dl-ssl.google.com/linux/linux_signing_key.pub" | sudo apt-key add -

  # Add Google to the apt-get source list
  echo 'deb http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list

  # Update app-get
  apt-get update

  # Install Java, Chrome, Xvfb, fonts, pip, and unzip
  apt-get -y install openjdk-7-jre google-chrome-stable unzip xvfb xfonts-cyrillic xfonts-100dpi xfonts-75dpi xfonts-tipa python-pip
  #install selenium bindings for python
  pip install selenium

  # Download and copy the ChromeDriver to /usr/local/bin
  cd /tmp
  if [ ! -f "chromedriver_linux64.zip" ];then
    wget "http://chromedriver.storage.googleapis.com/2.9/chromedriver_linux64.zip"
  fi
  if [ ! -f "selenium-server-standalone-2.39.0.jar" ];then
    wget "https://selenium.googlecode.com/files/selenium-server-standalone-2.39.0.jar"
  fi
  unzip chromedriver_linux64.zip
  mv -f chromedriver /usr/local/bin
  mv -f selenium-server-standalone-2.39.0.jar /usr/local/bin
  chmod 755 /usr/local/bin/chromedriver

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

# Start Xvfb, Chrome, and Selenium in the background
export DISPLAY=:10

echo "Starting Xvfb ..."
if ! pgrep Xvfb &> /dev/null;then
  Xvfb :10 +extension RANDR -screen 0 1366x768x24 -ac &
else
  echo "Xvfb already running."
fi

# echo "Starting Google Chrome ..."
# if ! pgrep '^chrome$' &> /dev/null;then
#   google-chrome --no-proxy-server --remote-debugging-port=9222 &
# else
#   echo "chrome already running."
# fi

echo "Starting Selenium ..."
cd /usr/local/bin
if ! pgrep java &> /dev/null;then
  nohup java -jar ./selenium-server-standalone-2.39.0.jar &
else 
  echo "java already running."
fi
