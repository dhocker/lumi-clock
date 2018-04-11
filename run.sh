#! /bin/bash
echo Start LumiClock
cd /home/pi/rpi/lumi-clock
# Put the venv at the front of the path
# When its python is run, it will activate the venv
PATH=~/Virtualenvs/lumiclock/bin:$PATH
python lumiclock.py
