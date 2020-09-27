# reset-rank-notindexed
# Author: Chris Wieringa <chris@wieringafamily.com>
# Date: 2020-09-26
# Purpose: reset a givenrank to not indexed

from shared import *
import os, sys, argparse, re

### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
dbfilename = datadir + "indexer.db"
dbtable = 'pages'

def main():
    
    # deal with the initial argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("rank", help="rank number to reset")
    args = parser.parse_args()
    rank = int(args.rank)
    nextrank = rank + 1
    
    print("Rank Processed Reset:",rank)
    print("**************************************************") 
    
    # pull down all unprocessed (crawled) sites at specified rank
    records = getRecordsByRank(rank)
    
    # loop them
    count = 1
    for r in records:
        print(" -- %s " % r)
        updateRecordParsed(r,0)
    
if __name__ == "__main__":
   main()
