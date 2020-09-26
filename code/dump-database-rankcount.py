# dump-database-rankcount.py

from shared import *

### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
dbfilename = datadir + "indexer.db"
dbtable = 'pages'

# iterate them
print("Opening:",dbfilename,"Table:",dbtable)
print("---------------------------")

for i in range(0,5):
    rank = i+1
    print("Rank %d - Total: %06d (Unprocessed: %06d)" % (rank,getNumRecordsByRank(rank),getNumUnprocessedRecordsByRank(rank)))
    #print("Rank " + str(rank) + " - Total:",str(getNumRecordsByRank(rank)),"(Unprocessed:",str(getNumUnprocessedRecordsByRank(rank)) + ")")

