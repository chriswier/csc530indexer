# dump-database.py

import dataset
from shared import *

### # # # # #
# Global variables
dbtable = 'pages'
robotstable = 'robots'

# get db lock and db object
# (no longer needed with mysql)
#lockfile = getDBLock(dbfilename)
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
#releaseDBLock(lockfile)
