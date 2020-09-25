#!/usr/bin/python3
import requests
from shared import *

url = 'https://en.wikipedia.org/wiki/United_States'
filename = geturlfilename(url,'./')
getURL(url,filename)
