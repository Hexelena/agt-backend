#! /usr/bin/env python3

import urllib.request
import html
import sqlite3
import os # deleting the db
from bs4 import BeautifulSoup

os.remove('agt.db')
print('[Removed old database]')

operoneUrl = 'http://localhost/web/phayax/agt/res/operone/altspr/wadinhalt.html'
operoneBaseUrl = "http://localhost/web/phayax/agt/res/operone/altspr/"


def getLinks(soup):
	# get all li's
	lis = soup.find_all('li')
	# get all a's that are inside the captured li's.
	lis = [el.find('a') for el in lis if len(el.find_all('a')) > 0]
	return lis

def fixShittyHtml(source):
	print(source)

# sqlite setup
conn = sqlite3.connect('agt.db')
print('[Created new database]')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS pageindex(idx INTEGER PRIMARY KEY, page TEXT, link TEXT);')
print("[Created table 'pageindex']")
c.execute('CREATE TABLE IF NOT EXISTS pagecontent(pagenum INTEGER, word TEXT, translation TEXT);')
print("[Created table 'pagecontent']")

source = urllib.request.urlopen(urllib.request.Request(operoneUrl)).read() #(chapterUrl, headers={'User-Agent': AGENT_NAME + ' Browser'})).read()
source = str(source)
source = html.unescape(source)
#source = '\n'.join(source)

soup = BeautifulSoup(source, 'html.parser')

pages = getLinks(soup)

for idx, entry in enumerate(pages):
	page = entry.get_text(strip=True)
	link = entry.get('href')
	params = (idx + 1, page, link,)
	c.execute('INSERT INTO pageindex VALUES(?, ?, ?);', params)

for idx, entry in enumerate(pages):
	page = urllib.request.urlopen(urllib.request.Request(operoneBaseUrl + entry.get('href'))).read()
	page = str(page) # cast to string (from stream)
	page = html.unescape(page) # unescape greek letters

	pageSoup = BeautifulSoup(page, 'html.parser')


conn.commit()
print('[Changes commited]')
conn.close()
print('[Database closed]')