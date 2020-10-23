# shared.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  shared functions for all Python scripts for the CSC530 Indexer proj
# Date: 2020-09-25

import base64, requests, os, re, dataset, pathlib, sys, subprocess, mimetypes, time, pysolr, urllib, json
import urllib.robotparser
from bs4 import BeautifulSoup
from langdetect import detect
from urllib.parse import urlparse


### # # # # #
# Global variables
datadir = "/home/cwieri39/csc530/data/"
pagedir = datadir + "pages/"
robotsdir = datadir + "robots/"
defaultextension = '.html'
dbtable = 'pages'
robotstable = 'robots'
dltable = 'downloads'
useragent = 'Mozilla/5.0 (csc530-indexer-edu-bot 0.0.2)'
solrdir = '/opt/solr/'
solrcollection = 'csc530'
solrbaseurl = 'http://localhost:8983/solr/'

### # # # # #
# SUBROUTINES

# # # # # # # # # # # # # # # # # # # # # # # # 
# # # # Encoding and Decoding Routines  # # # #
# # # # # # # # # # # # # # # # # # # # # # # # 

def encodeurl(url):
    ''' 
    Encodes a URL to a file-system and database safe string
    Receives in: plain URL string
    Returns: base64 safe-encoded URL string
    '''

    msg = url.encode('ascii')
    encmsg = base64.urlsafe_b64encode(msg)
    return encmsg.decode('ascii')

def decodeurl(b64string):
    '''
    Decoes an encoded URL back to the original URL
    Receives in: base64 safe-encoded URL string
    Returns: plain URL string
    '''

    msg = base64.urlsafe_b64decode(b64string)
    return msg.decode('ascii')

def geturlfilename(url,dir=pagedir,ext=defaultextension):
    '''
    Generates a encoded URL filename
    Receives in: 
      url - plain URL string
      dir - the base directory string
      ext - the standard filename extension string (with a .)
    Returns: the appropriate filename
    '''

    encfilename = encodeurl(url)
    filepath = dir + str(encfilename) + ext
    return filepath

def getencfilename(encname,dir=pagedir,ext=defaultextension):
    '''
    Generates a encoded URL filename from encoded URL
    Receives in: 
      encname - encoded URL string
      dir - the base directory string
      ext - the standard filename extension string (with a .)
    Returns: the appropriate filename
    '''

    filepath = dir + str(encname) + ext
    return filepath

def decodefilename(filename):
    '''
    Decodes a encoded URL filename back to the original URL
    Receives in: 
      file - full path to encoded URL filename
    Returns: the appropriate decoded URL string
    '''
    return decodeurl(pathlib.Path(filename).stem)

# # # # # # # # # # # # # # # # # # # # 
# # # # HTTP Download functions # # # #
# # # # # # # # # # # # # # # # # # # # 

def fixupURL(url):
    '''
    Fixes up URLs to strip out anchor tags # 
    Receives in: url string
    Returns: potentially modifed URL string
    '''

    # check to see if the URL has a # in it
    m = re.search('^(.+)\#',url)
    if m:
        #print("type:",m.group(1))
        url = m.group(1)
    
    # return out
    return url
    
    
def getURLContentType(url):
    ''' 
    Downloads a URL to retrieve the Content-Type of the URL.  This is used
    to detect if I have an HTML page, image, or something else.
    Receives: url - plain URL string
    Returns: content-type string or "error"
    '''

    # use wget
    wgetcmd = 'wget --server-response --spider %s -q -T 2 --read-timeout=2 --dns-timeout=2 --connect-timeout=2 -t 1 --no-dns-cache -U %s --no-cache' % (url,useragent)
    wgetcmd = wgetcmd.split()
    #print(wgetcmd)
    result = subprocess.run(wgetcmd, capture_output=True, text=True)
    #print(result)
    #print("Result stdout:",result.stdout)
    #print("Result stderr:",result.stderr)
    
    contenttype = ''
    for line in result.stderr.splitlines():
        m = re.search('Content-Type:\s(.+)$',line)
        if m:
            #print("type:",m.group(1))
            return m.group(1)

    # no match; bomb out
    return "error"

def getURL(url,filename):
    ''' 
    Retrieves the URL page and saves it to a file. 
    Receives in:
      url - a plain URL
      filename - a filename to save the URL to
    Returns:
      True, if successful
      False, if any error
    '''
    
    # first check to make sure directory is created
    basedir = os.path.dirname(filename)
    if(not(os.path.isdir(basedir))):
        pathlib.Path(basedir).mkdir(parents=True, exist_ok=True)
        
    # check URL type; only process text; bail otherwise
    urltype = getURLContentType(url)
    if(not(re.search('text',urltype))):
       return False
    
    # use wget
    wgetcmd = 'wget "%s" -O "%s" -q -T 2 --read-timeout=2 --dns-timeout=2 --connect-timeout=2 -t 2 -U "%s" --no-dns-cache --no-cache --convert-links' % (url,filename,useragent)

    stream = os.popen(wgetcmd)
    output = stream.read()
    #print(output)

    # check to make sure the file exists
    if(os.path.exists(filename) and os.path.isfile(filename) and
           os.stat(filename).st_size > 0):
        
        # also check document type
        if(not(re.search("text",str(mimetypes.guess_type(filename)[0])))):
            os.remove(filename)
            return False
        
        # check to make sure the language is english
        # parse with BeautifulSoup 
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        with open(filename) as fp:
            try:
                soup = BeautifulSoup(fp,'html5lib')
            except:
                os.remove(filename)
                return False
            
            # check to make sure I have a body
            if(soup.body != None):
                body_text = soup.body.get_text()
                try:
                    lang = detect(body_text)
            
                except:
                    os.remove(filename)
                    return False
            
                # only want english
                if(lang != "en"):
                    os.remove(filename)
                    return False
            
            # error; kill out
            else:
                os.remove(filename)
                return False
        
        # default return true if the file exists
        return True
    
    # bad download = fail
    else:
        return False

# # # # # # # # # # # # # # # # # # # # # # # # 
# # # # robots.txt processing routines  # # # #
# # # # # # # # # # # # # # # # # # # # # # # # 

def getRobotsURL(url):
    '''
    Generates the appropriate robots.txt URL from a given URL
    Takes in: url - plain URL string
    Returns: the url to the robots.txt file for that domain name
    '''

    netloc = urlparse(url).netloc
    scheme = urlparse(url).scheme
    return scheme + '://' + netloc + '/robots.txt'

def downloadRobotsURL(robotsUrl,filename,db,rtable=robotstable):
    '''
    Downloads a given robots.txt file, saves it to the local filesystem
    and updates the database with basic information that it has been
    retrieved.
    Takes in:
      robotsURL - the plain URL string for the robots.txt file
      filename - the filename to store the robots.txt downloaded file
      db - the db object
      rtable - the robots table in the database
    Returns:
      True - if successful
      False - if any error
    '''

    # do the download
    downloadResult = getURL(robotsUrl,filename)
    #print("downloadRobotsURL: ",robotsUrl,downloadResult)
    
    # make sure it is in the database, whether it exists or not
    # add to the database
    table = db[rtable]
    # make the insert
    id = table.insert(dict(site=robotsUrl,file=filename,exists=downloadResult))
    #print("createRecord:",id)
    db.commit()

    # close table
    table = None
    
    if(id == None):
        print("downloadRobotsURL insert Error!")
        #os.remove(filename)
        return False
    else:
        return True
    
def getRobotsDatabaseEntry(robotsUrl,db,rtable=robotstable):
    '''
    Checks to see if a robots.txt has already been downloaded according
    to the database entries.
    Takes in:
      robotsURL - a plain robots.txt url
      db - the db oject
      rtable - the robots table in the database
    Returns:
      rbentry - the dataset db table entry for the url or None if doesn't exist
    '''

    # check to see if it is in the database
    table = db[rtable]
    rbentry = table.find_one(site=robotsUrl)
    table = None
    return rbentry

def checkUrlAllowedRobots(url,dbEntry,db,rtable=robotstable,useragent='*'):
    ''' 
    Checks to make sure a URL is allowed to be accessed according to a robots.txt file.
    Takes in:
      url - plain URL string
      dbEntry - robots table dbentry for the page from getRobotsDatabaseEntry()
      db - db object
      rtable - robots db table
      useragent - the user-agent string to check
    Returns:
        True if OK
        False if not OK
    '''
    
    # check to see if it is in the database
    table = db[rtable]
    robotsfilename = dbEntry['file']
    robotsexists = dbEntry['exists']
    robotssite = dbEntry['site']
    
    # if it is there, use the pre-existing robots.txt
    if(robotsexists and os.path.exists(robotsfilename) and os.path.isfile(robotsfilename)):
        with open(robotsfilename) as f:
            lines = f.read().splitlines()
        
        #print(lines)
        # make a urllib parser
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robotssite)
        rp.parse(lines)
        #print(rp)
        #print(rp.site_maps())
        # check the url
        return rp.can_fetch(useragent,url)
    
    # if the robots.txt file doesn't exists, assume yes
    elif(robotsexists == False):
        return True
    
    else:
        return False    

# # # # # # # # # # # # # # # # # # # # # # # 
# # # # HTML page processing routines # # # #
# # # # # # # # # # # # # # # # # # # # # # # 

def getLinks(filename):
    ''' 
    Parse a downloaded HTML file for all links
    Takes in: filename, the filename to parse
    Returns: list of all links in the document
    '''

    links = []

    # check the filename
    if(os.path.exists(filename) and os.path.isfile(filename)):
        pass
    else:
        print("file not found",filename)
        return links

    # parse with BeautifulSoup 
    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    with open(filename) as fp:
        soup = BeautifulSoup(fp,'html5lib')
        #soup = BeautifulSoup(fp,'html.parser')
    #print(soup)
    
    # parse for links, skipping a bunch
    badextensions = ['jpg','jpeg','gif','svg','png','mp3','mp4','avi','mkv','docx','xlsx','pdf','doc']
    badchars = ['[',']']
    
    for link in soup.find_all('a'):
        href = link.get('href')
        
        # make sure I have an href to follow
        if(href is None):
            #print("skip")
            continue
        
        # need to rule out a number of links
        # 0.  Rule out bad extensions and char
        foundbadext = 0
        for ext in badextensions:
            if(foundbadext or re.search("%s$" % (re.escape(ext)),href)):
                #print("bad ext:",ext,href)
                foundbadext = 1
        if(foundbadext):
            continue
        
        foundbadchar = 0
        for char in badchars:
            if(foundbadchar or re.search("%s" % (re.escape(char)),href)):
                foundbadchar = 1
        if(foundbadchar):
            continue
        
        # 1. Rule out not having http/https in it
        if(not(re.search("http",href))):
           #print("bad url",href)
           continue
        
        # 2. rule out wikipedia foreign languages
        if(re.search("wikipedia.org",href)
           and not(re.search("en.*wikipedia.org",href) or re.search("www.*wikipedia.org",href))):
            #print("skip",href)
            continue
        
        # 3. book searchs by ISBN skip
        if(re.search(r"wikipedia.*BookSources",href)):
            #print("skip booksource:",href)
            continue
        
        # lastly, add it to the links list if it isn't there already
        if(not(href in links)):
            links.append(href)
        else:
            #print("duplicate link:",href)
            pass
    
    # return out
    return links

# # # # # # # # # # # # # # # # 
# # # # DB subroutines  # # # # 
# # # # # # # # # # # # # # # # 

def getDB():
    '''
    Makes a database connection to the default mySQL database using the Python
    dataset module, and returns the database dataset object
    Takes in: nothing
    Returns: db, the dataset database connection
    '''
        
    # make connection
    db = dataset.connect('mysql://csc530:csc530-indexer@localhost/csc530')
    if(db):
        return db
    else:
        print("getDB: failed to create db object")

def dropTable(db,tablename):
    '''
    Drop a given table from the database.
    Takes in:
      db - db object
      tablename - target tablename string
    Returns: None
    '''
    # drop the table given
    table = db[tablename]
    table.drop()

# # # # # # # # # # # # # # # # # # # #
# # # # Database Misc functions # # # #
# # # # # # # # # # # # # # # # # # # #

def createDownloadAttempt(mysite,mysuccess,db,mytable=dltable):
    '''
    Adds a download attempt for a site to the database
    Takes in:
      mysite - the encoded url string for the site
      mysuccess - 0 or 1 on whether or not the download succeeded
      db - db object
      mytable - database table to use
    Returns:
      True if OK
      False if not OK
    '''

    # make connection
    table = db[mytable]

    # make the insert
    id = table.insert(dict(site=mysite,success=mysuccess))
    db.commit()

    # clear the table
    table = None

    # return out
    if(id == None):
        print("createDownloadAttempt error!")
        return False
    else:
        return True

def createRecord(mysite,myrank,myparsed,myindexed,db,mytable=dbtable):
    '''
    Adds a plain site record to the database.
    Takes in:
      mysite - the encoded url string for the site
      myrank - the crawl rank for the site
      myparsed - 0 or 1 if it has been parsed/crawled
      myindexed - 0 or 1 if it has been indexed
      db - db object
      mytable - database table to use
    Returns:
      True if OK
      False if not OK
    '''
           
    #print("DEBUG",mysite,myrank,myparsed,dbfile,mytable)
    
    # make connection
    table = db[mytable]
    
    # make the insert
    id = table.insert(dict(site=mysite,rank=myrank,parsed=myparsed,indexed=myindexed))
    #print("createRecord:",id)
    db.commit()

    # close table
    table = None
    
    if(id == None):
        print("createRecord Error!")
        return False
    else:
        return True

def updateRecordParsed(mysite,myparsed,db,mytable=dbtable):
    '''
    Updates a record's parsed/crawled state
    Takes in:
      mysite - the encoded url string for the site
      myparsed - 0 or 1 if it has been parsed/crawled
      db - db object
      mytable - database table to use
    Returns:
      True if OK
      False if not OK
    '''
    
    # make connection
    table = db[mytable]
    
    # make the update
    id = table.update(dict(site=mysite,parsed=myparsed),['site'])
    db.commit()

    # close table
    table = None
    
    if(id == None):
        print("updateRecordParsed error!")
        return False
    else:
        return True


def updateRecordIndexed(mysite,myindexed,db,mytable=dbtable):
    '''
    Updates a record's indexed state
    Takes in:
      mysite - the encoded url string for the site
      myindexed - 0 or 1 if it has been parsed/crawled
      db - db object
      mytable - database table to use
    Returns:
      True if OK
      False if not OK
    '''
    
    # make connection
    table = db[mytable]
    
    # make the update
    id = table.update(dict(site=mysite,indexed=myindexed),['site'])
    db.commit()

    # close table
    table = None
    
    if(id == None):
        print("updateRecordIndexed error!")
        return False
    else:
        return True

def getNumRecordsByRank(myrank,db,mytable=dbtable):
    '''
    Get the count of the number of records in a rank
    Takes in:
      myrank - integer number of the rank to count
      db - db object
      mytable - database table to use
    Returns: number of matching sites
    '''
    
    # make connection
    table = db[mytable]
    
    # return
    return table.count(rank=myrank)

def getNumUnprocessedRecordsByRank(myrank,db,mytable=dbtable):
    '''
    Get the count of the number of unprocessed or uncrawled sites in a rank
    Takes in:
      myrank - integer number of the rank to count
      db - db object
      mytable - database table to use
    Returns: number of matching sites
    '''
    # make connection
    table = db[mytable]
    
    # return it out
    return table.count(rank=myrank,parsed=0)

def getNumUnindexedRecordsByRank(myrank,db,mytable=dbtable):
    '''
    Get the count of the number of unindexed sites in a rank
    Takes in:
      myrank - integer number of the rank to count
      db - db object
      mytable - database table to use
    Returns: number of matching sites
    '''

    # make connection
    table = db[mytable]
    
    # return it out
    return table.count(rank=myrank,indexed=0)

def getUnprocessedRecordsByRank(myrank,db,mytable=dbtable):
    '''
    Get a list of site db ojbects of unprocessed / uncrawled sites for a rank
    Takes in:
      myrank - integer number of the rank to count
      db - db object
      mytable - database table to use
    Returns: list of matching dataset site db objects
    '''
    # make connection
    table = db[mytable]
    
    # query it
    records = []
    for row in table.find(rank=myrank,parsed=0):
        records.append(str(row['site']))

    # close table
    table = None
    
    # return it out
    return records

def getUnindexedRecordsByRank(myrank,db,mytable=dbtable):
    '''
    Get a list of site db ojbects of unindexed sites for a rank
    Takes in:
      myrank - integer number of the rank to count
      db - db object
      mytable - database table to use
    Returns: list of matching dataset site db objects
    '''
    # make connection
    table = db[mytable]
    
    # query it
    records = []
    for row in table.find(rank=myrank,indexed=0):
        records.append(str(row['site']))

    # close table
    table = None
    
    # return it out
    return records

def getRecordsByRank(myrank,db,mytable=dbtable):
    '''
    Get a list of site db ojbects of sites at a rank
    Takes in:
      myrank - integer number of the rank to count
      db - db object
      mytable - database table to use
    Returns: list of matching dataset site db objects
    '''
    # make connection
    table = db[mytable]

    # query it
    records = []
    for row in table.find(rank=myrank):
        records.append(str(row['site']))

    # close table
    table = None

    # return it out
    return records


def checkSiteExists(mysite,db,mytable=dbtable):
    '''
    Checks to see if a site exists in the database
    Takes in:
      mysite - encoded URL string of the site to check
      db - db object
      mytable - database table to use
    Returns: 
      True if it exists
      False if not
    '''
    # make connection
    table = db[mytable]
    
    count = table.count(site=mysite)

    # close table
    table = None
    
    # return it out
    if(count == 1):
        return True
    else:
        return False

def checkSiteDownloaded(mysite,db,mytable=dltable):
    '''
    Checks to see if a site has been downloaded in the database
    Takes in:
      mysite - encoded URL string of the site to check
      db - db object
      mytable - database table to use
    Returns: 
      True if it has been downloaded
      False if not
    '''
    # make connection
    table = db[mytable]
        # make connection
    table = db[mytable]
    count = table.count(site=mysite)

    # close table
    table = None

    # return it out
    if(count == 1):
        return True
    else:
        return False


# # # # # # # # # # # # # # # # # # # # # # # # #
# # # # Subroutines to process a new URL  # # # #
# # # # # # # # # # # # # # # # # # # # # # # # #

def processURL(url,rank,db,mytable=dbtable,mypagedir=pagedir,rtable=robotstable,rdir=robotsdir,mydltable=dltable):
    '''
    Process a URL. Check to see if it already exists, if not download it and add it to the appropriate database tables.
    Takes in:
      url - a plain URL
      rank - the crawl rank for this page
      db - db object
      mytable - the sites db table
      mypagedir - the download file directory
      rtable - the robots db table
      rdir - the download file directory for robots files
      mydltable - the downloads db table
    Returns:
      True if OK
      False if not OK
    '''
    
    # first, get the encoded name
    try:
        encname = encodeurl(url)
        filename = geturlfilename(url,mypagedir)

    # if I get a failure here, just bomb out on this one
    except:
        return False
    
    # check to see if this one exists already
    exists = checkSiteExists(encname,db,mytable)
    if(exists):
        #print("  processURL: URL %s already exists! Skipping!" % (url))
        return False

    # check to see if I've attempted to download this before
    dlexists = checkSiteDownloaded(url,db,mydltable)
    if(exists):
        #print("  processURL: URL %s has been downloaded already!  Skipping!" % (url))
        return False

    # deal with URLs that always timeout for wget
    # (note: not needed anymore
    skipurls = ['usnews.com','mediawiki.org','wikimediafoundation.org','wikimedia.org',
                'cbc.ca','nationalgeographic.com','jstor.org','questia.com','wikimediafoundation.org',
                'stats.wikimedia.org','3m.com','archive.org',
               ]
    for surls in skipurls:
       if(re.search(surls,url)):
           print("  --> skipping due to skip url:",surls,skipurls)
           return False
   
    # check robots file
    robotsurl = getRobotsURL(url)
    robj = getRobotsDatabaseEntry(robotsurl,db,rtable)
    rfile = geturlfilename(robotsurl,robotsdir,'.txt')

    # robots - existing robots not in database
    # so download it if it exists
    if(robj == None):

        # try three times
        i = 0
        success = 0

        robotsdownload = downloadRobotsURL(robotsurl,rfile,db,rtable)
        if(robotsdownload):
           success = 1

        # if this failed, then return false
        if(success == 0):
            return False

        # assume I'm good now; re-get the robj
        robj = getRobotsDatabaseEntry(robotsurl,db,rtable)

    # next, check the URL against the robots.txt file; fail (return False) on being
    # disallowed by the robots.txt file
    robotscancheck = checkUrlAllowedRobots(url,robj,db,rtable)
    if(robotscancheck == False):
        return False

    # output
    #print("  processURL: getting URL",url,"to",filename)
    
    # run getURL
    if(getURL(url,filename)):
        #print("  --> downloaded successfully.")
        # need to add the download attempt into database
        rval = createDownloadAttempt(url,True,db,mydltable)
    else:
        #print("  --> FAILED download. Skipping!")
        rval = createDownloadAttempt(url,False,db,mydltable)
        return False
    
    # add to the database
    if(createRecord(encname,rank,0,0,db,mytable)):
        #print("  --> added to database.")
        return True
    else:
        #print("  --> FAILED to add to database.  Removing downloaded file and skipping!")
        os.remove(filename)
        return False

# # # # # # # # # # # # # # # # # # # # # #
# # # # Indexing and Solr functions # # # #
# # # # # # # # # # # # # # # # # # # # # #

def indexFile(filename,myid,mycoll=solrcollection):
    '''
    Run the indexing of a file up to Solr.
    Takes in:
     filename - string of the filename
     myid - the id to set in solr
     mycoll - the Solr collection (optional)
    Return:
     True - success
     False - failure
    '''
    solrurl = solrbaseurl + mycoll + '/update/extract?literal.id=' + urllib.parse.quote_plus(myid) + '&commit=true'
    curlcmd = 'curl -s ' + solrurl + " -F myfile=@" + filename 
    #print(curlcmd)
    curlcmd = curlcmd.split()
    result = subprocess.run(curlcmd, capture_output=True, text=True)
    #print(result)

    # load result json into dictionary
    try:
        result = json.loads(result.stdout)

        # check for status = 0, that's good!
        if result['responseHeader']['status'] == 0:
            return True
        else:
            return False
    except Exception as e:
        print("indexFile - *** error decoding JSON result:",e,"****")
        return False


def solrIndexURL(encurl,mydb,mytable=dbtable,mycoll=solrcollection):
    '''  Processes an encurl and adds to solr
    Input:
      encurl - the encrypted url string from the sites table
      mydb - db object
      mytable - the database table to work on (optional)
      mycoll -  the solrcollection to add to (optional)
    Returns:
      True if OK
      False if not OK
    '''

    # figure out unencrypted URL and full filename
    url = decodeurl(encurl)
    filename = getencfilename(encurl)

    # check to make sure this is in the database and unindexed, and
    # the file is on the file system
    table = mydb[mytable]
    numrecords = table.count(site=encurl,indexed=0)
    if(numrecords != 1):
        print("** solrIndexURL - site %s (%s) already indexed! **" % (encurl,url))
        return False
     
    if(os.path.exists(filename) and os.path.isfile(filename)):
        pass
    else:
        print("** solrIndexURL - site %s file %s does not exist. **" % (encurl,filename))

    # assuming I'm good; add to Solr
    addresult = indexFile(filename,url,mycoll)
    if(addresult == False):
        print("** solrIndexURL - site %s could not be added to Solr. **" % encurl)
        return False

    # update the record
    updateresult = updateRecordIndexed(encurl,1,mydb,mytable)
    return updateresult


def solrSearchCollection(query,rows=10,start=0,mycoll=solrcollection):
    '''
    Searches Solr for a given query and returns the results.
    Input:
      query - a query
      rows - number of rows to return
      start - offset for the number of rows to return
      mycoll - a Solr collection name (optional)
    Return:
      results list from for pysolr
    '''
    solrurl = solrbaseurl + mycoll + '/'
    solr = pysolr.Solr(solrurl, always_commit=True, timeout=10)
    #solr.ping()
    #print(query,mycoll)
    results = solr.search(query, **{
        'rows': rows,
        'start': start,
    })
    #print('***',results,'***')
    return results

def solrClearCollection(mycoll=solrcollection):
    '''
    Resets a Solr collection back to nothing
    Input:
      mycoll, a Solr collection name
    Return: None
    '''
    solrurl = solrbaseurl + mycoll + '/'
    solr = pysolr.Solr(solrurl, always_commit=True, timeout=10)
    solr.delete(q='*:*')
    


# # # # # # # # # # # # # # # # # # # # # # 
# # # # Test and DEBUG subroutines  # # # # 
# # # # # # # # # # # # # # # # # # # # # # 

def removeURL(url,db,mytable=dbtable,dir=pagedir,ext=defaultextension):
    '''
    Removes a site url from the database and filesystem.  * Danger Will Robinson! *
    Takes in:
      url - a plain URL string
      db - db object
      mytable - the sites table
      dir - the downloaded base directory on the filesystem
      ext - the default file extension
    Returns:
      True if OK
      False if not OK
    '''

    print("removeURL",url,dir,ext,mytable)
    encurl = encodeurl(url)
    encfilename = geturlfilename(url,dir,ext)
    
    # check to see if it is in the database
    #exists = checkSiteExists(encurl,dbfile,mytable)
    exists = True
    if(exists):
        print("removeURL - site exists")
        
        # use passed in dbobject
        table = db[mytable]
    
        # use a sqlalchemy query here
        numrows = table.delete(site=encurl)

        # close table
        table = None
        
        # return it out
        if(numrows == 1):
            
            # need to remove the file from the drive
            os.remove(encfilename)
            
            # return true
            return True
        else:
            print("Failed to remove from database")
            return False

    else:
        print("Failed to remove; site not found in database")
        return False
