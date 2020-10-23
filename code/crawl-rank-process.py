# crawl-rank-process.py
# Author: Chris Wieringa <chris@wieringafamily.com>
# Date: 2020-09-26
# Purpose: crawl all pages in rank (already downloaded),
#   parse links, and process all new pages to the next rank
#   NOTE: single-threaded

from shared import *
import os, sys, argparse, re

### # # # # #
# Global variables

def main():
    
    # deal with the initial argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("rank", help="rank number to crawl")
    args = parser.parse_args()
    rank = int(args.rank)
    nextrank = rank + 1
    
    print("Crawl Rank:",rank)
    print("**************************************************") 

    # open the database connection
    db = getDB()
    
    # pull down all unprocessed (crawled) sites at specified rank
    numtoprocess = getNumUnprocessedRecordsByRank(rank,db)
    records = getUnprocessedRecordsByRank(rank,db)
    
    # loop them
    count = 1
    for r in records:
        url = decodeurl(r)
        file = getencfilename(r)
        print("Processing URL (%d of %d): %s" % (count,numtoprocess,url))
        print("  File: %s" % (file))
        mylinks = getLinks(file)
        totallinks = len(mylinks)
        
        linkcount = 1
        for link in mylinks:
            print("  - Link %s of %s: %s" % (linkcount,totallinks,link))
            myprocesslink = processURL(link,nextrank,db)
            linkcount += 1
        
        # update the record to be processed
        assert updateRecordParsed(r,1,db)
        count += 1
    
if __name__ == "__main__":
   main()
