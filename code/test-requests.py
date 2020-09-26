import requests


url = 'https://en.wikipedia.org/wiki/United_States'

headers = {'user-agent': 'csc530-umflint-edu-bot/0.0.1'}
s = requests.Session()
page = s.head(url,headers=headers)