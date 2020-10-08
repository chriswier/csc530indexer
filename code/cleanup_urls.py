# cleanup_urls.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  cleanup some bad urls with # in them
# Date: 2020-10-02

from shared import *
import re, time, os, dataset

### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
dbfile = datadir + "indexer.db"
mytable = 'pages'
useragent = 'Mozilla/5.0 (csc530-indeexer-edu-bot 0.0.1)'


# # # # # # #
# DEBUG

DEBUG = 1

# get db lock and db object
lockfile = getDBLock(dbfile)
mydb = getDB(dbfile)

table = mydb[mytable]

# query it
records = []
rows = table.find()

for row in rows:
    #print("URL:",decodeurl(row['site']))
    if(re.search('\#',decodeurl(row['site']))):
        myoldurl = decodeurl(row['site'])
        myfixupurl = fixupURL(myoldurl)
        print("Affected URL: ",myoldurl)
        print(" --> Fixed:",myfixupurl)
        
        # remove the bad one
        success = removeURL(myoldurl,mydb,mytable,pagedir,defaultextension)
        if(success):
            print(" --> Removed old successfully.")
        else:
            print(" --> Could not remove.")
        
        # check if I need to add this URL in
        if(checkSiteExists(encodeurl(myfixupurl),mydb,mytable) == False):
            
            # add the new fixed up one
            checkcreate = createRecord(encodeurl(myfixupurl),row['rank'],0,0,mydb,mytable)
            if(checkcreate):
                print(" --> Added new record")
            else:
                print(" --> Failed adding new record")
        
    #records.append(str(row['site']))


# close db lock and db object
mydb = None
releaseDBLock(lockfile)
