# shared.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  shared functions for all Python scripts for the CSC530 Indexer proj
# Date: 2020-09-25

import base64
import requests
import os

# url encoding
def encodeurl(url):
	msg = url.encode('ascii')
	encmsg = base64.urlsafe_b64encode(msg)
	return encmsg.decode('ascii')

def decodeurl(b64string):
	msg = base64.urlsafe_b64decode(b64string)
	return msg.decode('ascii')

# convert url to a filename either using encname or the full URL
def geturlfilename(url,dir='../crawledpages/',ext='.html'):
	encfilename = encodeurl(url)
	filepath = dir + str(encfilename) + ext
	return filepath

def getencfilename(encname,dir='../crawledpages/',ext='.html'):
	filepath = dir + str(encname) + ext
	return filepath

# HTTP download functions
def getURLContentType(url):
	headers = {'user-agent': 'csc530-umflint-edu-bot/0.0.1'}
	s = requests.Session()
	head = s.head(url,headers=headers)
	return head.headers['content-type']

def getURL(url,filename):
	# use wget
	wgetcmd = 'wget "%s" -O "%s" -q -T 10 -U "csc530-umflint-edu-bot/0.0.1" --no-cache --convert-links' % (url,filename)

	stream = os.popen(wgetcmd)
	output = stream.read()
	print(output)

	# check to make sure the file exists
	if(os.path.exists(filename) and os.path.isfile(filename) and
           os.stat(filename).st_size > 0):
		return True
	else:
		return False	

