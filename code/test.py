# test.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  test functions
# Date: 2020-09-25

from shared import *
import re, time, os, dataset

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
    for l in mylinks:
        print(l)

## test database functions
# variables
dbfile = 'test.db'
dbtable = 'testpages'
testurl1 = 'http://slashdot.org'
testurl2 = 'http://reddit.com'
testurl3 = 'http://npr.org'
testurl4 = 'http://cnn.com'
testurl5 = 'http://umflint.edu'

# make a clean db, remove old one if exists
if(os.path.exists(dbfile)):
    os.remove(dbfile)

if(DEBUG):
    print("**** Testing database routines ****")

try:
    assert createRecord(encodeurl(testurl1),1,0,0,dbfile,dbtable)
    assert getNumRecordsByRank(1,dbfile,dbtable) == 1
    assert checkSiteExists(encodeurl(testurl1),dbfile,dbtable)
    assert createRecord(encodeurl(testurl2),1,1,1,dbfile,dbtable)
    assert getNumRecordsByRank(1,dbfile,dbtable) == 2
    assert checkSiteExists(encodeurl(testurl2),dbfile,dbtable)
    assert createRecord(encodeurl(testurl3),2,0,0,dbfile,dbtable)
    assert getNumRecordsByRank(2,dbfile,dbtable) == 1
    assert getNumUnprocessedRecordsByRank(1,dbfile,dbtable) == 1
    assert getNumUnprocessedRecordsByRank(2,dbfile,dbtable) == 1
    assert getNumUnindexedRecordsByRank(1,dbfile,dbtable) == 1
    assert getNumUnindexedRecordsByRank(2,dbfile,dbtable) == 1
    assert updateRecordParsed(encodeurl(testurl3),1,dbfile,dbtable)
    assert updateRecordIndexed(encodeurl(testurl3),1,dbfile,dbtable)
    assert getNumUnprocessedRecordsByRank(2,dbfile,dbtable) == 0
    assert getNumUnindexedRecordsByRank(2,dbfile,dbtable) == 0
    assert createRecord(encodeurl(testurl4),1,0,0,dbfile,dbtable)
    assert createRecord(encodeurl(testurl5),1,0,0,dbfile,dbtable)
    records = getUnprocessedRecordsByRank(1,dbfile,dbtable)
    assert len(records) == 3
    
    if(DEBUG):
        print("  --> Unprocessed rows in rank 1")
        for row in records:
            print("     " + row + " - " + decodeurl(row))
            
except AssertionError as ae:
    print("DB Error:",ae)
    db = dataset.connect('sqlite:///' + dbfile)
    table = db[dbtable]

    for row in table.all():
        print(row)

