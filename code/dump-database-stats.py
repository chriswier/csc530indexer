# dump-database-rankcount.py

from shared import *

### # # # # #
# Global variables
dbtable = 'pages'

# iterate them
print("Opening DB Table:",dbtable)
print("---------------------------")

# make the db object
mydb = getDB()
table = mydb[dbtable]

indexednumrecords = table.count(indexed=1)
notindexednumrecords = table.count(indexed=0)
crawlednumrecords = table.count(parsed=1)
notcrawlednumrecords = table.count(parsed=0)
totalrecords = table.count()

# print it out
print("    Crawled pages: %07d" % crawlednumrecords)
print("Not crawled pages: %07d" % notcrawlednumrecords)
print("    Indexed pages: %07d" % indexednumrecords)
print("Not Indexed pages: %07d" % notindexednumrecords)
print("    Total records: %07d" % totalrecords)

# finish connection
mydb = None
