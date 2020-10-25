# initial-populate.py
# Author: Chris Wieringa <chris@wieringafamily.com>
# Date: 2020-09-26
# Purpose: populate initial rank 1 pages

from shared import *
import os, sys, argparse, re

### # # # # #
# Global variables
dbtable = 'pages'
robotstable = 'robots'

def main():
    
    # deal with the initial argument parsing
    
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="text file with initial list of URLs, one per line")
    args = parser.parse_args()
    filename = args.inputfile
          
    # check for the file
    if(os.path.exists(filename) and os.path.isfile(filename) and
       os.stat(filename).st_size > 0):
        with open(filename) as fp:
            urllist = fp.readlines()
    else:
        print('Cannot find file:',filename)
        sys.exit(2)

    # intialize db connection
    db = getDB()

    # check to make sure the user really wants to override the database
    overwrite = input("Overwrite database to do initial populate.  Confirm overwrite? (y/N) : ")
    if(overwrite in ("y","Y","yes","YES")):
        dropTable(db,dbtable)
        dropTable(db,robotstable)

    else:
        print("Not replacing existing database.")
        sys.exit(2)
    
    # iterate through the list
    for line in urllist:
        line = line.rstrip()
        if(re.search('^#',line) or re.search('^ ',line)):
            continue
        elif(re.search('^http',line)):
            print("Processing:",line)
            assert processURL(line,1,db)
            
        else:
            print("Error on line: ",line)
            continue

if __name__ == "__main__":
   main()
