#!/usr/bin/python

from twython import Twython
import json
import cgi

consumer_key = "QZwOVsnTParlVIh0ratSHBwad"
consumer_secret = "KafCkTmyIlGOUiGFpqawPcVMZISzVXZW9J3thzlbcYyy9RY1I6"

print "Content-type: application/json"
print

form = cgi.FieldStorage()
print form