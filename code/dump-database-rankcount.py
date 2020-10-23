# dump-database-rankcount.py

from shared import *

### # # # # #
# Global variables
dbtable = 'pages'
mydb = getDB()

# iterate them
print("Opening db Table:",dbtable)
print("---------------------------")

for i in range(0,5):
    rank = i+1
    print("Rank %d - Total: %07d (Unprocessed: %07d, Unindexed: %07d)" %
          (rank,getNumRecordsByRank(rank,mydb),getNumUnprocessedRecordsByRank(rank,mydb),
           getNumUnindexedRecordsByRank(rank,mydb)))
    #print("Rank " + str(rank) + " - Total:",str(getNumRecordsByRank(rank)),"(Unprocessed:",str(getNumUnprocessedRecordsByRank(rank)) + ")")

# close db lock and db object
mydb = None
#releaseDBLock(lockfile)
