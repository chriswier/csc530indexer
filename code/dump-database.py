# dump-database.py

import dataset
from shared import *

### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
dbfilename = datadir + "indexer.db"
dbtable = 'pages'

# get db lock and db object
lockfile = getDBLock(dbfilename)
mydb = getDB(dbfilename)


# make a table
table = mydb[dbtable]

# iterate them
print("Opening:",dbfilename,"Table:",dbtable)
print("---------------------------")
print("All rows:")
for row in table.all():
    print(row)
    
# close db lock and db object
mydb = None
releaseDBLock(lockfile)