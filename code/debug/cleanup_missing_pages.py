# cleanup_missing_pages.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  cleanup missing pages from the database
# Date: 2020-10-02

from shared import *
import re, time, os, dataset

### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
mytable = 'pages'
useragent = 'Mozilla/5.0 (csc530-indeexer-edu-bot 0.0.1)'


# # # # # # #
# DEBUG

DEBUG = 1

# get db object
mydb = getDB()
table = mydb[mytable]

# query it
records = []
rows = table.find()

for row in rows:
    # check if file exists
    encsite = row['site']
    filename = getencfilename(encsite)
    url = decodeurl(encsite)
    
    if(os.path.exists(filename) and os.path.isfile(filename)):
        pass
    else:
        print("Missing - fetching",url,filename)
        
        fetch = getURL(url,filename)
        if(fetch):
            print("-- success")
        else:
            print("-- failure")

# close db object
mydb = None
