# dump-database.py

import dataset
from shared import *

### # # # # #
# Global variables
dbtable = 'pages'
robotstable = 'robots'

# get db object
mydb = getDB()

# make a table
table = mydb[dbtable]

# iterate them
print("Opening:",dbfilename,"Table:",dbtable)
print("---------------------------")
print("All rows:")
for row in table.all():
    print(row)
    
# close db object
mydb = None
