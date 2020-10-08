# test.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  test functions
# Date: 2020-09-25

from shared import *
import re, time, os, dataset

# # # # # # #
# DEBUG

DEBUG = 1



# # # # # test encodeurl/decodeurl
test = 'https://en.wikipedia.org/wiki/United_States'
testenc = encodeurl(test)
testdec = decodeurl(testenc)

if(DEBUG):
    print("**** encodeurl/decodeurl ****")
    print("URL:",test)
    print("URL Encoded:",testenc)
    print("URL Decoded:",testdec)
assert test == testdec

# # # #  test fixupURL
testurl = 'http://slashdot.org/abc/1.html#test'
testurlfixed = 'http://slashdot.org/abc/1.html'
assert fixupURL(testurl) == testurlfixed

# # # test geturlfilename / getencfilename
test = 'https://en.wikipedia.org/wiki/United_States'
testurlfilename = geturlfilename(test)
testenc = encodeurl(test)
testencfilename = getencfilename(testenc)
testdecodefilename = decodefilename(testencfilename)


if(DEBUG):
    print("**** geturlfilename/getencfilename ****")
    print("URL:",test)
    print("URL filename:",testurlfilename)
    print("Enc filename:",testencfilename)
    print("Dec filename:",testdecodefilename)
assert testurlfilename == testencfilename
assert testdecodefilename == test

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
    #for l in mylinks:
    #    print(l)

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

# get db lock and db object
lockfile = getDBLock(dbfile)
mydb = getDB(dbfile)

if(DEBUG):
    print("**** Testing database routines ****")

try:
    assert createRecord(encodeurl(testurl1),1,0,0,mydb,dbtable)
    assert getNumRecordsByRank(1,mydb,dbtable) == 1
    assert checkSiteExists(encodeurl(testurl1),mydb,dbtable)
    assert createRecord(encodeurl(testurl2),1,1,1,mydb,dbtable)
    assert getNumRecordsByRank(1,mydb,dbtable) == 2
    assert checkSiteExists(encodeurl(testurl2),mydb,dbtable)
    assert createRecord(encodeurl(testurl3),2,0,0,mydb,dbtable)
    assert getNumRecordsByRank(2,mydb,dbtable) == 1
    assert getNumUnprocessedRecordsByRank(1,mydb,dbtable) == 1
    assert getNumUnprocessedRecordsByRank(2,mydb,dbtable) == 1
    assert getNumUnindexedRecordsByRank(1,mydb,dbtable) == 1
    assert getNumUnindexedRecordsByRank(2,mydb,dbtable) == 1
    assert updateRecordParsed(encodeurl(testurl3),1,mydb,dbtable)
    assert updateRecordIndexed(encodeurl(testurl3),1,mydb,dbtable)
    assert getNumUnprocessedRecordsByRank(2,mydb,dbtable) == 0
    assert getNumUnindexedRecordsByRank(2,mydb,dbtable) == 0
    assert createRecord(encodeurl(testurl4),1,0,0,mydb,dbtable)
    assert createRecord(encodeurl(testurl5),1,0,0,mydb,dbtable)
    records = getUnprocessedRecordsByRank(1,mydb,dbtable)
    assert len(records) == 3
    
    if(DEBUG):
        print("  --> Unprocessed rows in rank 1")
        for row in records:
            print("     " + row + " - " + decodeurl(row))
            
except AssertionError as ae:
    print("DB Error:",ae)

    table = mydb[dbtable]

    for row in table.all():
        print(row)

# Robots testing
testurl6 = 'https://atlas.cs.calvin.edu/index.html'
testurl7 = 'https://en.wikipedia.org/wiki/United_States'
testurl6robots = getRobotsURL(testurl6)
testurl7robots = getRobotsURL(testurl7)
testurl6filename = geturlfilename(testurl6robots,'./','.txt')
testurl7filename = geturlfilename(testurl7robots,'./','.txt')

if(DEBUG):
    print("**** Testing robots routines ****")
    print("testurl6:",testurl6,testurl6robots,testurl6filename)
    print("testurl7:",testurl7,testurl7robots,testurl7filename)
    
try:
    
    print("  * robots urls *")
    assert testurl6robots == 'https://atlas.cs.calvin.edu/robots.txt'
    assert testurl7robots == 'https://en.wikipedia.org/robots.txt'
    print("  * blank db entries to start *")
    assert getRobotsDatabaseEntry(getRobotsURL(testurl6),mydb) == None
    assert getRobotsDatabaseEntry(getRobotsURL(testurl7),mydb) == None
    print("  * download robots urls *")
    testurl6dl = downloadRobotsURL(testurl6robots,testurl6filename,mydb)
    testurl7dl = downloadRobotsURL(testurl7robots,testurl7filename,mydb)
    assert testurl6dl
    assert testurl7dl
    print("  * get db entries *")
    testurl6dbobj = getRobotsDatabaseEntry(getRobotsURL(testurl6),mydb)
    testurl7dbobj = getRobotsDatabaseEntry(getRobotsURL(testurl7),mydb)
    assert testurl6dbobj['exists'] == False
    assert testurl7dbobj['exists'] == True
    print("  * check Urls allowed from robots *")
    assert checkUrlAllowedRobots(testurl6,mydb,testurl6dbobj)
    assert checkUrlAllowedRobots(testurl7,mydb,testurl7dbobj)
    assert checkUrlAllowedRobots(testurl7,mydb,testurl7dbobj,'Zealbot') == False
    
    
except AssertionError as ae:
    print("Robots error:",ae)
    
# get rid of downloaded robots files
os.remove(testurl6filename)
os.remove(testurl7filename)

# close db lock and db object
mydb = None
releaseDBLock(lockfile)
