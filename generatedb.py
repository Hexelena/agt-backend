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


def getListLinks(soup):
	"""
	Takes all "li > a" tags and returns them.
	The correct selector is probably "li > a:firstChild".
	"""
	# get all li's
	lis = soup.find_all('li')
	# get all a's that are inside the captured li's.
	lis = [el.find('a') for el in lis if len(el.find_all('a')) > 0]

	return lis

def fixBadHtml(source):
	"""
	Takes bad html lists and puts closing tags on the end of each line
	with a list tag and no closing tag.
	"""
	# process each line on it's own
	source = source.split('\n')

	newSource = []
	
	for line in source:
		line = line.strip()
		# check if its a relevant line
		# we know that only entries are li's
		if '<li>' in line:
			if not '</li>' in line:
				line += '</li>'

		newSource.append(line)

	newSource = '\n'.join(newSource)
	return newSource


def createTables(connection):

	# Create a table as an index of all pages.
	connection.execute('CREATE TABLE IF NOT EXISTS pageindex(idx INTEGER PRIMARY KEY, page TEXT, link TEXT);')
	print("[Created table 'pageindex']")
	
	# Create a table of the content of all pages.
	connection.execute('CREATE TABLE IF NOT EXISTS pagecontent(pagenum INTEGER, word TEXT, translation TEXT);')
	print("[Created table 'pagecontent']")

	
# sqlite setup
conn = sqlite3.connect('agt.db')
print('[Created new database]')
c = conn.cursor()

createTables(c)



# get source of index page
source = urllib.request.urlopen(urllib.request.Request(operoneUrl)).read() #(chapterUrl, headers={'User-Agent': AGENT_NAME + ' Browser'})).read()
source = str(source)
source = html.unescape(source)

soup = BeautifulSoup(source, 'html.parser')

pages = getListLinks(soup)

for idx, entry in enumerate(pages):
	page = entry.get_text(strip=True)
	link = entry.get('href')
	params = (idx + 1, page, link,)
	c.execute('INSERT INTO pageindex VALUES(?, ?, ?);', params)

for idx, entry in enumerate(pages[:1]):
	page = urllib.request.urlopen(urllib.request.Request(operoneBaseUrl + entry.get('href'))).read()
	page = page.decode('ISO-8859-1') # encoding of the operone pages
	page = html.unescape(page)
	#page = str(page) # cast to string (from stream)
	#page = html.unescape(page) # unescape greek letters
	page = fixBadHtml(page)

	pageSoup = BeautifulSoup(page, 'html.parser')
	lis = pageSoup.find_all('li')
	for element in lis:
		print(element.findChildren())

conn.commit()
print('[Changes commited]')
conn.close()
print('[Database closed]')