# shared.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  shared functions for all Python scripts for the CSC530 Indexer proj
# Date: 2020-09-25

import base64, requests, os, re, dataset, pathlib, sys, subprocess, mimetypes, time
import urllib.robotparser
from bs4 import BeautifulSoup
from langdetect import detect
from filelock import Timeout, FileLock
from urllib.parse import urlparse


### # # # # #
# Global variables
datadir = "/home/cwieri39/csc530/data/"
pagedir = datadir + "pages/"
robotsdir = datadir + "robots/"
defaultextension = '.html'
dbfilename = datadir + "indexer.db"
dbtable = 'pages'
robotstable = 'robots'
useragent = 'Mozilla/5.0 (csc530-indexer-edu-bot 0.0.2)'

### # # # # #
# SUBROUTINES

# url encoding
def encodeurl(url):
    msg = url.encode('ascii')
    encmsg = base64.urlsafe_b64encode(msg)
    return encmsg.decode('ascii')

def decodeurl(b64string):
    msg = base64.urlsafe_b64decode(b64string)
    return msg.decode('ascii')

# convert url to a filename either using encname or the full URL
def geturlfilename(url,dir=pagedir,ext=defaultextension):
    encfilename = encodeurl(url)
    filepath = dir + str(encfilename) + ext
    return filepath

def getencfilename(encname,dir=pagedir,ext=defaultextension):
    filepath = dir + str(encname) + ext
    return filepath

# convert filename back to URL
def decodefilename(filename):
    return decodeurl(pathlib.Path(filename).stem)

def fixupURL(url):
    # check to see if the URL has a # in it
    m = re.search('^(.+)\#',url)
    if m:
        #print("type:",m.group(1))
        url = m.group(1)
    
    # return out
    return url
    
    
# HTTP download functions
def getURLContentType(url):
    
    # use wget
    wgetcmd = 'wget --server-response --spider %s -q -T 10 --read-timeout=15 -t 1 --no-dns-cache -U %s --no-cache' % (url,useragent)
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
    
    # first check to make sure directory is created
    basedir = os.path.dirname(filename)
    if(not(os.path.isdir(basedir))):
        pathlib.Path(basedir).mkdir(parents=True, exist_ok=True)
        
    # check URL type; only process text; bail otherwise
    urltype = getURLContentType(url)
    if(not(re.search('text',urltype))):
       return False
    
    # use wget
    wgetcmd = 'wget "%s" -O "%s" -q -T 10 --read-timeout=15 -t 2 -U "%s" --no-dns-cache --no-cache --convert-links' % (url,filename,useragent)

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


# robots.txt processing
def getRobotsURL(url):
    netloc = urlparse(url).netloc
    scheme = urlparse(url).scheme
    return scheme + '://' + netloc + '/robots.txt'

# # convert url to a filename either using encname or the full URL
# def getRobotsURLfilename(url,dir=pagedir,ext='.txt'):
#     encfilename = encodeurl(url)
#     filepath = dir + str(encfilename) + ext
#     return filepath

def downloadRobotsURL(robotsUrl,filename,db,rtable=robotstable):
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
    
    if(id == None):
        print("downloadRobotsURL insert Error!")
        #os.remove(filename)
        return False
    else:
        return True
    
def getRobotsDatabaseEntry(robotsUrl,db,rtable=robotstable):
    # check to see if it is in the database
    table = db[rtable]
    return table.find_one(site=robotsUrl)

def checkUrlAllowedRobots(url,dbEntry,db,rtable=robotstable,useragent='*'):
    ''' assumes url is a page url, db is the pre-made db object, and dbEntry is the robots table dbentry for the page, gotten by getRobotsDatabaseEntry '''
    
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

# html page processing
def getLinks(filename):
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

# DB subroutines
# # # # # # # # #

# db file locking
def getDBLock(dbfile=dbfilename):
    lock = FileLock("%s.lock" % dbfile,)
    try:
        with lock.acquire(timeout=10):
            return lock
    except Timeout:
        print("getDBLock - failed with timeout")
        return None

def releaseDBLock(lock):
    lock.release()

def getDB(dbfile=dbfilename):
#def getDB(dbfile=dbfilename):
    # check the db directory; file will be autocreated if it doesn't exist
    #basedir = os.path.dirname(dbfile)
    #if(not(os.path.isdir(basedir))):
    #    pathlib.Path(basedir).mkdir(parents=True, exist_ok=True)
        
    # make connection
    #db = dataset.connect('sqlite:///' + dbfile)
    db = dataset.connect('mysql://csc530:csc530-indexer@localhost/csc530')
    if(db):
        return db
    else:
        print("getDB: failed to create db object")

# drop the table
def dropTable(db,tablename):
    # drop the table given
    table = db[tablename]
    table.drop()

# createRecord
def createRecord(mysite,myrank,myparsed,myindexed,db,mytable=dbtable):
           
    #print("DEBUG",mysite,myrank,myparsed,dbfile,mytable)
    
    # make connection
    table = db[mytable]
    
    # make the insert
    id = table.insert(dict(site=mysite,rank=myrank,parsed=myparsed,indexed=myindexed))
    #print("createRecord:",id)
    db.commit()
    
    if(id == None):
        print("createRecord Error!")
        return False
    else:
        return True

def updateRecordParsed(mysite,myparsed,db,mytable=dbtable):
    
    # make connection
    table = db[mytable]
    
    # make the update
    id = table.update(dict(site=mysite,parsed=myparsed),['site'])
    db.commit()
    
    if(id == None):
        print("updateRecordParsed error!")
        return False
    else:
        return True


def updateRecordIndexed(mysite,myindexed,db,mytable=dbtable):
    
    # make connection
    table = db[mytable]
    
    # make the update
    id = table.update(dict(site=mysite,indexed=myindexed),['site'])
    db.commit()
    
    if(id == None):
        print("updateRecordIndexed error!")
        return False
    else:
        return True

def getNumRecordsByRank(myrank,db,mytable=dbtable):
    
    # make connection
    table = db[mytable]
    
    # use a sqlalchemy query here
    #result = db.query("SELECT COUNT(*) c FROM " + mytable + " WHERE rank = '" + str(myrank) + "'")
    #count = 0
    #for row in result:
    #    count = row['c']
    return table.count(rank=myrank)

def getNumUnprocessedRecordsByRank(myrank,db,mytable=dbtable):
    # make connection
    table = db[mytable]
    
    # use a sqlalchemy query here
    #result = db.query("SELECT COUNT(*) c FROM " + mytable + " WHERE rank = '" + str(myrank) + "' AND parsed='0'")
    #count = 0
    #for row in result:
    #    count = row['c']
    
    # return it out
    return table.count(rank=myrank,parsed=0)

def getNumUnindexedRecordsByRank(myrank,db,mytable=dbtable):
    # make connection
    table = db[mytable]
    
    # use a sqlalchemy query here
    #result = db.query("SELECT COUNT(*) c FROM " + mytable + " WHERE rank = '" + str(myrank) + "' AND indexed='0'")
    #count = 0
    #for row in result:
    #    count = row['c']
    
    # return it out
    return table.count(rank=myrank,indexed=0)

def getUnprocessedRecordsByRank(myrank,db,mytable=dbtable):
    # make connection
    table = db[mytable]
    
    # query it
    records = []
    for row in table.find(rank=myrank,parsed=0):
        records.append(str(row['site']))
    
    # return it out
    return records

def getUnindexedRecordsByRank(myrank,db,mytable=dbtable):
    # make connection
    table = db[mytable]
    
    # query it
    records = []
    for row in table.find(rank=myrank,indexed=0):
        records.append(str(row['site']))
    
    # return it out
    return records

def getRecordsByRank(myrank,db,mytable=dbtable):
    # make connection
    table = db[mytable]

    # query it
    records = []
    for row in table.find(rank=myrank):
        records.append(str(row['site']))

    # return it out
    return records


def checkSiteExists(mysite,db,mytable=dbtable):
    # make connection
    table = db[mytable]
    
    # use a sqlalchemy query here
    #result = db.query("SELECT COUNT(*) c FROM " + mytable + " WHERE site = '" + mysite + "'")
    #count = 0
    #for row in result:
    #    count = row['c']
    count = table.count(site=mysite)
    
    # return it out
    if(count == 1):
        return True
    else:
        return False
    

# # # # # #
# commands to process a new URL
def processURL(url,rank,db,mytable=dbtable,mypagedir=pagedir,rtable=robotstable,rdir=robotsdir):
    
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
        print("  processURL: URL %s already exists! Skipping!" % (url))
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

        while(i < 3):
            robotsdownload = downloadRobotsURL(robotsurl,rfile,db,rtable)
            if(robotsdownload):
                success = 1
                i = 10
            else:
                i += 1
                time.sleep(1)

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
    print("  processURL: getting URL",url,"to",filename)
    
    # run getURL
    if(getURL(url,filename)):
        print("  --> downloaded successfully.")
    else:
        print("  --> FAILED download. Skipping!")
        return False
    
    # add to the database
    if(createRecord(encname,rank,0,0,db,mytable)):
        print("  --> added to database.")
        return True
    else:
        print("  --> FAILED to add to database.  Removing downloaded file and skipping!")
        os.remove(filename)
        return False

# # # # #
# functions that shouldn't be needed much

def removeURL(url,db,mytable=dbtable,dir=pagedir,ext=defaultextension):
    # danger will robinson!  This will remove it from the database and filesystem
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
