# index-rank.py
# Author: Chris Wieringa <chris@wieringafamily.com>
# Date: 2020-10-18
# Purpose: reset a givenrank to not indexed

from shared import *
import os, sys, argparse, re

### # # # # #
# Global variables

def main():
    
    # deal with the initial argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("rank", help="rank number to reset")
    args = parser.parse_args()
    rank = int(args.rank)
    
    print("Index Rank:",rank)
    print("**************************************************") 

    # make the db connection
    db = getDB()
    
    # pull down all unprocessed (crawled) sites at specified rank
    records = getUnindexedRecordsByRank(rank,db)
    numrecords = len(records)
    
    # loop them
    count = 1
    for r in records:
        print(" -- %s of %s: %s" % (count,numrecords,r))
        result = solrIndexURL(r,db)
        if(result == False):
            print(" -- ******* ERROR indexing! ")

        count += 1
    
if __name__ == "__main__":
   main()
