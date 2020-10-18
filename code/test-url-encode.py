import urllib

url = "http://en.wikipedia.org/wiki/United_States"
print(urllib.parse.quote_plus(url))