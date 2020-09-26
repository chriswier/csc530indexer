Script explaination:

End-user facing programs:
initial-populate.py - takes in a filename with a list of URLs one-per line.  Populates into the SQLite database as rank 1 URLs.

Support scripts:
shared.py - all the shared functions needed for this all to work together.

Test scripts:
dump-database.py - dumps the SQLite database to the console.
dump-database-rankcount.py - dumps rank count statistics to the console.
test.py - tests the shared.py file functions
test-dataset.py - initial attempt at using module dataset
test-requests.py - initial attempt at using module requests

Other files:
test.db - test db file for test.py
United_States - wikipedia article for United_States, used in test.py
