# test-dataset.py

import dataset
from shared import *
import os

# variables
dbfile = 'test.db'
testurl1 = 'http://slashdot.org'
testurl2 = 'http://reddit.com'
testurl3 = 'http://npr.org'

# make a clean db, remove old one if exists
if(os.path.exists(dbfile)):
    os.remove(dbfile)

# make connection
db = dataset.connect('sqlite:///' + dbfile)

# make a table
table = db['pages']

# insert some records
table.insert(dict(site=encodeurl(testurl1), rank=1, parsed=0))
table.insert(dict(site=encodeurl(testurl2), rank=1, parsed=1))
table.insert(dict(site=encodeurl(testurl3), rank=2, parsed=0))

# iterate them
print("All rows:")
for row in table.all():
    print(row)

# find all rank 1s
print("All Rank 1s:")
for row in table.find(rank=1):
    print(row)

# find all rank 1s that aren't parsed
print("All Rank 1s with parsed=0:")
for row in table.find(rank=1,parsed=0):
    print(row)
    
# update one of them
print("Updating " + encodeurl(testurl1) + " with parsed=1")
print(" --> " + str(table.find_one(site=encodeurl(testurl1))))
table.update(dict(site=encodeurl(testurl1),parsed=1),['site'])
print(" --> Update done")
print(" --> " + str(table.find_one(site=encodeurl(testurl1))))

# query count
myrank = 1
result = db.query("SELECT COUNT(*) c FROM pages WHERE rank = '" + str(myrank) + "'")
count = 0
for row in result:
    count = row['c']
print("Count of rank " + str(myrank) + ":",str(count))

# delete one
print("Deleting " + encodeurl(testurl2))
table.delete(site=encodeurl(testurl2))
numresults = 0
for row in table.find(site=encodeurl(testurl2)):
    numresults += 1
print("Found",numresults,"results.")

# commit test
db.commit()
db = None

# remake connection
db2 = dataset.connect('sqlite:///' + dbfile)
print("Reopened database:")
table2 = db2['pages']
for row in table2.all():
    print(row)
db2 = None

# remove db
if(os.path.exists(dbfile)):
    os.remove(dbfile)