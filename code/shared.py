# shared.py
# Author: Chris Wieringa chris@wieringafamily.com
# Purpose:  shared functions for all Python scripts for the CSC530 Indexer proj
# Date: 2020-09-25

import base64, requests, os, re, dataset, pathlib
from bs4 import BeautifulSoup
from langdetect import detect

### # # # # #
# Global variables
datadir = "../data/"
pagedir = datadir + "pages/"
defaultextension = '.html'
dbfilename = datadir + "indexer.db"
dbtable = 'pages'

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

# HTTP download functions
def getURLContentType(url):
    headers = {'user-agent': 'csc530-umflint-edu-bot/0.0.1'}
    s = requests.Session()
    head = s.head(url,headers=headers)
    return head.headers['content-type'].rstrip()

def getURL(url,filename):
    
    # first check to make sure directory is created
    basedir = os.path.dirname(filename)
    if(not(os.path.isdir(basedir))):
        pathlib.Path(basedir).mkdir(parents=True, exist_ok=True)
    
    # use wget
    wgetcmd = 'wget "%s" -O "%s" -q -T 10 -U "csc530-umflint-edu-bot/0.0.1" --no-cache --convert-links' % (url,filename)

    stream = os.popen(wgetcmd)
    output = stream.read()
    #print(output)

    # check to make sure the file exists
    if(os.path.exists(filename) and os.path.isfile(filename) and
           os.stat(filename).st_size > 0):
        
        # check to make sure the language is english
        # parse with BeautifulSoup 
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        with open(filename) as fp:
            soup = BeautifulSoup(fp,'html5lib')
            body_text = soup.body.get_text()
            lang = detect(body_text)
            
            # only want english
            if(lang != "en"):
                os.remove(filename)
                return False
        
        # default return true if the file exists
        return True
    
    # bad download = fail
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
    badextensions = ['.jpg','.jpeg','.gif','.svg','.png','.mp3','.mp4','.avi','.mkv','.docx','.xlsx']
    
    for link in soup.find_all('a'):
        href = link.get('href')
        
        # make sure I have an href to follow
        if(href is None):
            #print("skip")
            continue
        
        # need to rule out a number of links
        # 0.  Rule out bad extensions
        for ext in badextensions:
            if(re.search(r"%s$" % re.escape(ext),href)):
                #print("bad ext:",ext,href)
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

# createRecord
def createRecord(mysite,myrank,myparsed,dbfile=dbfilename,mytable=dbtable):
    # check the db directory; file will be autocreated if it doesn't exist
    basedir = os.path.dirname(dbfile)
    if(not(os.path.isdir(basedir))):
        pathlib.Path(basedir).mkdir(parents=True, exist_ok=True)
        
    #print("DEBUG",mysite,myrank,myparsed,dbfile,mytable)
    
    # make connection
    db = dataset.connect('sqlite:///' + dbfile)
    table = db[mytable]
    
    # make the insert
    db.begin()
    try:
        id = table.insert(dict(site=mysite,rank=myrank,parsed=myparsed))
        db.commit()
    except:
        db.rollback()
        db = None
        print("createRecord Error!")
        return False
    
    # return True
    db = None
    return True

def updateRecordParsed(mysite,myparsed,dbfile=dbfilename,mytable=dbtable):
    # check the db filepath
    if(not(os.path.exists(dbfile))):
        return False
    
    # make connection
    db = dataset.connect('sqlite:///' + dbfile)
    table = db[mytable]
    
    # make the update
    db.begin()
    try:
        table.update(dict(site=mysite,parsed=myparsed),['site'])
        db.commit()
    except:
        db.rollback()
        db = None
        return False
    
    # return True
    db = None
    return True

def getNumRecordsByRank(myrank,dbfile=dbfilename,mytable=dbtable):
    # check the db filepath
    if(not(os.path.exists(dbfile))):
        print("getNumRecordsByRank - file not found " + dbfile)
        return 0
    
    # make connection
    db = dataset.connect('sqlite:///' + dbfile)
    table = db[mytable]
    
    # use a sqlalchemy query here
    result = db.query("SELECT COUNT(*) c FROM " + mytable + " WHERE rank = '" + str(myrank) + "'")
    count = 0
    for row in result:
        count = row['c']
    
    # return it out
    db = None
    return count

def getNumUnprocessedRecordsByRank(myrank,dbfile=dbfilename,mytable=dbtable):
    # check the db filepath
    if(not(os.path.exists(dbfile))):
        print("getNumUnprocessedRecordsByRank - file not found " + dbfile)
        return 0
    
    # make connection
    db = dataset.connect('sqlite:///' + dbfile)
    table = db[mytable]
    
    # use a sqlalchemy query here
    result = db.query("SELECT COUNT(*) c FROM " + mytable + " WHERE rank = '" + str(myrank) + "' AND parsed='0'")
    count = 0
    for row in result:
        count = row['c']
    
    # return it out
    db = None
    return count    

def getUnprocessedRecordsByRank(myrank,dbfile=dbfilename,mytable=dbtable):
    # check the db filepath
    if(not(os.path.exists(dbfile))):
        print("getUnprocessedRecordsByRank - file not found " + dbfile)
        return []
    
    # make connection
    db = dataset.connect('sqlite:///' + dbfile)
    table = db[mytable]
    
    # query it
    records = []
    for row in table.find(rank=myrank,parsed=0):
        records.append(str(row['site']))
    
    # return it out
    db = None
    return records

# # # # # #
# commands to process a new URL
def processURL(url,rank,dbfile=dbfilename,mytable=dbtable,mypagedir=pagedir):
    
    # first, get the encoded name
    encname = encodeurl(url)
    filename = geturlfilename(url,mypagedir)
    
    # output
    print("  processURL: getting URL",url,"to",filename)
    
    # run getURL
    if(getURL(url,filename)):
        print("  --> downloaded successfully.")
    else:
        print("  --> FAILED download. Skipping!")
        return False
    
    # add to the database
    if(createRecord(encname,rank,0,dbfile,mytable)):
        print("  --> added to database.")
        return True
    else:
        print("  --> FAILED to add to database.  Removing downloaded file and skipping!")
        os.remove(filename)
        return False