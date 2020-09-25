# test.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  test functions
# Date: 2020-09-25

from shared import *
import re
import time
import os

# # # # # # #
# DEBUG

DEBUG = 1

# # # # test encodeurl/decodeurl
test = 'https://en.wikipedia.org/wiki/United_States'
testenc = encodeurl(test)
testdec = decodeurl(testenc)

if(DEBUG):
    print("**** encodeurl/decodeurl ****")
    print("URL:",test)
    print("URL Encoded:",testenc)
    print("URL Decoded:",testdec)
assert test == testdec


# # # test geturlfilename / getencfilename
test = 'https://en.wikipedia.org/wiki/United_States'
testurlfilename = geturlfilename(test)
testenc = encodeurl(test)
testencfilename = getencfilename(testenc)

if(DEBUG):
    print("**** geturlfilename/getencfilename ****")
    print("URL:",test)
    print("URL filename:",testurlfilename)
    print("Enc filename:",testencfilename)
assert testurlfilename == testencfilename

# # # test getURLContentType/getURL
test = 'https://en.wikipedia.org/wiki/United_States'
testurlfilename = geturlfilename(test,'./','.htm')

testhead = getURLContentType(test)
if(DEBUG):
    print("**** getURLContentType ****")
    print("URL:",test)
    print("Content-Type:",testhead)
assert re.search("text\/html",testhead)

testfile = str(int(time.time())) + ".html"
result = getURL(test,testfile)
assert result
assert os.path.exists(testfile)
assert os.stat(testfile).st_size > 1000
if(DEBUG):
    print("**** getURL ****")
    print("URL:",test)
    print("Test file:",testfile)
    print("Test file size:",os.stat(testfile).st_size)
os.remove(testfile)

# # # test getLinks
testfile = 'United_states'
mylinks = getLinks(testfile)
assert len(mylinks) > 2000
if(DEBUG):
    print("**** getLinks ****")
    print("Test file:",testfile)
    print("Num links:",len(mylinks))

