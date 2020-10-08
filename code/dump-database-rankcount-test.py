# dump-database-rankcount.py

from shared import *

### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
dbfilename = datadir + "indexer-test.db"
dbtable = 'pages'


# get db lock and db object
lockfile = getDBLock(dbfilename)
mydb = getDB(dbfilename)

# iterate them
print("Opening:",dbfilename,"Table:",dbtable)
print("---------------------------")

for i in range(0,5):
    rank = i+1
    print("Rank %d - Total: %06d (Unprocessed: %06d, Unindexed: %06d)" %
          (rank,getNumRecordsByRank(rank,mydb),getNumUnprocessedRecordsByRank(rank,mydb),
           getNumUnindexedRecordsByRank(rank,mydb)))
    #print("Rank " + str(rank) + " - Total:",str(getNumRecordsByRank(rank)),"(Unprocessed:",str(getNumUnprocessedRecordsByRank(rank)) + ")")

# close db lock and db object
mydb = None
releaseDBLock(lockfile)