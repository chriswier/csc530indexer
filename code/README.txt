To use these scripts, you will need to have the appropriate Python virtualenv setup before attempting to use the scripts.  Please see https://github.com/chriswier/csc530indexer/blob/master/python3-venv.txt for information on creating the virtualenv and correctly activating it before using these scripts.

End-user facing programs and scripts:
-----------------------------
initial-populate.py - takes in a filename with a list of URLs one-per line.  Populates into the SQLite database as rank 1 URLs.
crawl-rank-process.py - takes in a rank number.  Starts the crawling process for unprocessed/uncrawled sites at the given rank.
crawl-rank-process-threaded.py - identical to crawl-rank-process.py but threaded for faster crawling; used to start the crawling  process for unprocessed/uncrawled sites at the given rank.
index-rank.py - takes in a rank number.  Indexes all unindexed sites at the given rank to Apache Solr.

Support scripts:
---------------------------
shared.py - all the shared functions needed for this all to work together used by almost all of the python scripts.

Testing and Statistics scripts:
--------------------------
dump-database.py - dumps the database to the console.
dump-database-rankcount.py - dumps rank count statistics to the console.
dump-database-stats.py - dumps total site counts to the console.
test.py - tests the shared.py file functions

Debug scripts:
--------------------------
debug/cleanup_files.py - goes through files on the file system to clean up files that don't exist in the database (misdownloads)
debug/cleanup_missing_pages.py - goes through the database to cleanup sites that didn't download correctly
debug/cleanup_urls.py - goes through the database to cleanp old downloaded urls with bad targets in the links # 

Other files:
--------------------------
initial-pages.txt - the initial URL page list used for population of rank 1
United_States - wikipedia article for United_States, used in test.py
United_states.html - symlink to the United_States file used in test.py
