# search.py
# Author: Chris Wieringa <chris@wieringafamily.com>
# Date: 2020-10-18
# Purpose: search solr

from shared import *
import os, sys, argparse, re

### # # # # #
# Global variables

def main():
    
    # deal with the initial argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="solr query term")
    args = parser.parse_args()
    query = args.query
    
    print("Results:",query)
    print("**************************************************") 

    # make the db connection
    db = getDB()
    
    # pull down the search results
    records = solrSearchCollection(query)
    numrecords = len(records)
    
    # loop them
    count = 1
    for r in records:
        print(" -- %s of %s:\n%s" % (count,numrecords,r['id']))
        count += 1
    
if __name__ == "__main__":
   main()
