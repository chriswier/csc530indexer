# crawl-rank-process.py
# Author: Chris Wieringa <chris@wieringafamily.com>
# Date: 2020-09-26
# Purpose: crawl all pages in rank (already downloaded),
#   parse links, and process all new pages to the next rank

# Sources:
# https://realpython.com/intro-to-python-threading/#using-a-threadpoolexecutor
# https://docs.python.org/3/library/concurrent.futures.html

from shared import *
import os, sys, argparse, re, logging, threading, time
import concurrent.futures

### # # # # #
# Global variables

def processLink(link,nextrank,mydb):
    logging.info("processLink: %s Nextrank: %s" % (link,nextrank))
    mythreaddb = getDB()
    #myprocesslink = processURL(link,nextrank,mydb)
    myprocesslink = processURL(link,nextrank,mythreaddb)
    mythreaddb = None

def main():
    
    # deal with the initial argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("rank", help="rank number to crawl")
    args = parser.parse_args()
    rank = int(args.rank)
    nextrank = rank + 1
   
    # basic logging
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main        : Crawl Rank: %s" % rank)

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
        logging.info("Processing URL (%d of %d): %s" % (count,numtoprocess,url))
        #print("  File: %s" % (file))
        mylinks = getLinks(file)
        totallinks = len(mylinks)
        logging.info("  --> Total links to process: %s " % totallinks)
        
        #linkcount =1
        #for link in mylinks:
        #    print("  - Link %s of %s: %s" % (linkcount,totallinks,link))
        #    myprocesslink = processURL(link,nextrank,db)
        #    linkcount += 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            future_links = {executor.submit(processLink,link,nextrank,db): link for link in mylinks}
            #future_links = {executor.map(processLink,(link,nextrank,db),timeout=15): link for link in mylinks}

            try:
                for future in concurrent.futures.as_completed(future_links,timeout=5):
                    link = future_links[future]
                    data = future.result()
            except Exception as exc:
                logging.info('%r generated an exception: %s' % (link,exc))
            else:
                #logging.info('-- %r processed' % link)
                pass
        
        # update the record to be processed
        assert updateRecordParsed(r,1,db)
        count += 1
    
if __name__ == "__main__":
   main()
