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
mytable = 'pages'
useragent = 'Mozilla/5.0 (csc530-indeexer-edu-bot 0.0.1)'


# # # # # # #
# DEBUG

DEBUG = 1

# get db object
mydb = getDB()
table = mydb[mytable]

# loop through all files
for filename in os.listdir(pagedir):
    url = decodefilename(filename)

    # check to see if this URL exists in the database
    if(checkSiteExists(encodeurl(url),mydb,mytable) == False):
            
        print(filename,url,"-- Need to remove!")
        os.remove(pagedir + filename)


# close db object
mydb = None
