# dump-database.py

import dataset


### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
dbfilename = datadir + "indexer.db"
dbtable = 'pages'

# make connection
db = dataset.connect('sqlite:///' + dbfilename)

# make a table
table = db[dbtable]

# iterate them
print("Opening:",dbfilename,"Table:",dbtable)
print("---------------------------")
print("All rows:")
for row in table.all():
    print(row)