#! /usr/bin/env python3

import os   # deleting the db
import sys  # output redirection
import html # unescape naugty html codes
import urllib.request 
import sqlite3  # db access
import datetime
import logging
# graphical interface imports
import tkinter as tk
import tkinter.ttk as ttk

# installed modules
from bs4 import BeautifulSoup

# local files
from fixer import ALL_FIX_DICT, VOCAB_FIX_DICT
from greektools import greek_simplify, greek_to_ascii


operoneUrl = 'http://localhost/web/phayax/agt/res/operone/altspr/wadinhalt.html'
operoneBaseUrl = "http://localhost/web/phayax/agt/res/operone/altspr/"

DB_NAME = 'agt.sqlite'

#operoneUrl = 'http://www.operone.de/altspr/wadinhalt.html'
#operoneBaseUrl = "http://www.operone.de/altspr/"


unknown_set = {""}
problematic_list = {""}

class StdoutRedirector:
    '''
    Eine Klasse um Output zu einem Text-Widget umzuleiten.
    Wird hauptsächlich für stdout verwendet.
    stderr hat eine eigene Klasse mit Highlighting.
    '''
    def __init__(self, textitem):
        # Die Klasse braucht ein Handle auf das Text-Widget, 
        # um dorthin zu schreiben
        self.texthandle = textitem

    def write(self, string):
        self.texthandle.insert(tk.END, string)

    def flush(self):
        self.texthandle.update()

class App(tk.Tk):

    def __init__(self, cursor):
        tk.Tk.__init__(self)
        self.initialize()
        self.dbHandle = cursor

    def initialize(self):
        self.title('Operone -> Database Parser')
        self.grid()
        self.minsize(800,600)

        self.grid_columnconfigure(1, weight=1)

        self.infoText = tk.Label(self, text="Huhu")
        self.infoText.grid(row=0, column=1, padx=5, pady=5)

        self.startButton = tk.Button(self, text='Start Parsing', command=self.startParsing)
        self.startButton.grid(row = 2, column = 1, padx=5, pady=5)
        self.quitButton = tk.Button(self, text='Close',fg='red', command=self.quit)
        self.quitButton.grid(row=3, column = 1, padx=5, pady=5)


        self.progress = tk.DoubleVar()
        self.progress.set(0)
        
        self.progressBar = ttk.Progressbar(self, orient="horizontal", maximum=266, length=500, mode="determinate", variable=self.progress)
        self.progressBar.grid(row = 1, column = 1, sticky="WE", padx=5, pady=5)

        #self.barstarted = False
        yScrollbar = tk.Scrollbar(self, orient='vertical')
        yScrollbar.grid(row=4, column=2, sticky='NSE')
        xScrollbar = tk.Scrollbar(self, orient='horizontal')
        xScrollbar.grid(row=5, column=1, sticky='WE')

        self.output = tk.Text(self,wrap=tk.NONE, height = 4, width=50, yscrollcommand=yScrollbar.set, xscrollcommand=xScrollbar.set)
        self.output.grid(row=4, column=1, sticky='NSWE', padx=5, pady=5)
        yScrollbar.config(command=self.output.yview)
        xScrollbar.config(command=self.output.xview)


        self.grid_rowconfigure(4, weight=1)

        self.entriesParsed = 0

        # backup stdout
        self.origstdout = sys.stdout
        # reroute stdout to application text widget
        sys.stdout = StdoutRedirector(self.output)


    def quit(self):
        # restore original stdout
        sys.stdout = self.origstdout
        self.destroy()

    def startParsing(self):
        startTime = datetime.datetime.now()
        self.progress.set(0)
        pages = parseIndex(self.dbHandle)
        for idx, page in enumerate(pages):
            self.infoText.configure(text='Parsing page {}'.format(page))
            self.entriesParsed += parsePage(self.dbHandle, page, idx)
            self.progress.set(self.progress.get() + 1.0)
            self.progressBar.update()
        endTime = datetime.datetime.now()
        timepassed = (endTime - startTime).total_seconds()
        self.infoText.configure(text='Finished Parsing: {} entries processed in {:.1f} seconds'.format(self.entriesParsed, timepassed))


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
    logging.info("[Created table 'pageindex']")
    
    # Create a table of the content of all pages.
    #connection.execute('CREATE TABLE IF NOT EXISTS pagecontent(pagenum INTEGER, word TEXT, alternateWords TEXT, translation TEXT);')
    connection.execute('CREATE TABLE IF NOT EXISTS pagecontent(roughword TEXT, preciseword TEXT, greek TEXT, alternategreek TEXT, translation TEXT);')
    logging.info("[Created table 'pagecontent']")


def parseExceptions(line):
    if type(line) != str:
        raise TypeError('type str expected. found {}'.format(type(line)))

    # detect if there was a missing </span> tag that got wrongly autocorrected by beautifulsoup
    # this is done by checking if there is anything between the closing li tag and the closing span tag.
    closeSpan = line.find('</span>')
    closeSpan += len('</span>')
    closeLi = line.find('</li>')
    if len(line[closeSpan:closeLi].strip()) == 0:
        logging.info('-----------------------------------------------------------------------')
        logging.info('[Warning] Possible problem in the following line.:\n\t{}'.format(line))
        # remove the wrongly placed closing span
        line = line[:line.find('</span>')] + line[line.find('</li>'):]
        # add the closing span at the first space after the greek word
        # this is not failproof but the problem will be reported and can be checked
        insertIdx = line.find('<span class="hel">')
        # note the trailing space - there is "always"(ha!) a space between the tag and the word.
        # so we are setting the index right before the beginning of the word
        # if not it is placed in the word which is just fine
        insertIdx += len('<span class="hel"> ')
        # look for the first whitespace starting from the previously
        # determined index.
        insertIdx = line.find(' ', insertIdx)
        # insert the closing span tag plus a comma for separation since
        # the later part expects the word to be divided from the translation by a comma
        # if we introduce a comma too much that is not a problem since the later part will
        # filter out commas.
        line = line[:insertIdx] + ', </span>' + line[insertIdx:]
        logging.info('\t\t Attempting to fix the mentioned problem. Please check:\n\t\t{}'.format(line))

    # apply fix dict for whole lines
    for element in ALL_FIX_DICT:
        line = line.replace(element, ALL_FIX_DICT[element])

    return line


def parseIndex(c):    

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

    return pages

def parsePage(c, page, idx):
    """
    Parses a single page of the operone dictionary:
    Gets the page source:
    fixes problematic html tags(not closed or wrongly placed mostly)
    for every entry on the page:
        runs parseExceptions on the line
        takes the different parts of the line.
        simplifies and copys the transformed versions.
        writes the entry to the database
    """
    page = urllib.request.urlopen(urllib.request.Request(operoneBaseUrl + page.get('href'))).read()
    page = page.decode('ISO-8859-1') # encoding of the operone pages
    page = html.unescape(page)
    #page = str(page) # cast to string (from stream)
    #page = html.unescape(page) # unescape greek letters
    page = fixBadHtml(page)

    # this automatically adds closing span tags at the end of a line if none are present
    pageSoup = BeautifulSoup(page, 'html.parser')
    lis = pageSoup.find_all('li')

    for element in lis:
        #print(element)
        # ok, we are getting additional translations or variations that belong to the word
        # for now we will be ignoring them by using only the first child.

        correctedLine = parseExceptions(str(element))
        element = BeautifulSoup(correctedLine, 'html.parser')

        # get_text can strip whitespaces but since we need the comma stripped as well
        # it makes more sense to put both into one context.
        # vocab is the raw string of the entry
        vocab = element.findChild().findChild().get_text().strip(', ')

        # apply fix dict for vocab part
        for entry in VOCAB_FIX_DICT:
            vocab = vocab.replace(entry, VOCAB_FIX_DICT[entry])

        # versions is a list of the different lookup words of the entry
        versions = [version.strip() for version in vocab.split(',')]
        # main is the first version - we will just assume that this is what we want ...
        main = versions[0]
        # alternate are all other versions concatenated by commas.
        alternate = ",".join(versions[1:])
        # start index behind the first span. used to separate
        # the lookup word from the translation since there can be 
        # greek letters and tags in the translation (otherwise we could just the text with recursive=False to eliminate text in tags)
        tlStartIndex = str(element).find('</span>')
        tlStartIndex += len('</span>')

        # ok, so here we take off the first part of the entry which
        # contains the greek word. Then we feed the remaining string into 
        # a new BeautifulSoup instance and strip remaining tags in the translation
        # with the get_text() method.
        subText = BeautifulSoup((str(element))[tlStartIndex:], 'html.parser')
        translation = str(subText.get_text()).strip()
        #pageNum = idx
        rough = greek_to_ascii(greek_simplify(main), False)
        precise = greek_to_ascii(greek_simplify(main), True)
        c.execute('INSERT INTO pagecontent VALUES(?, ?, ?, ?, ?)',(rough, precise, main, alternate, translation,))
        #print(translation)

    return len(lis)


def main():
    
    logging.basicConfig(filename='dbgen.log', filemode='w', level=logging.WARNING)
    # remove old db file
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print('[Removed old database]')

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # sqlite setup
    conn = sqlite3.connect(DB_NAME)
    print('[Created new database]')
    c = conn.cursor()

    createTables(c)


    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # tkinter related
    app = App(c)
    app.mainloop()

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # create db indices
    conn.execute('CREATE INDEX roughindex ON pagecontent (roughword)')
    print('[Created index for rough lookup]')
    conn.execute('CREATE INDEX preciseindex ON pagecontent (preciseword)')
    print('[Created index for precise lookup]')
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # sqlite cleanup
    conn.commit()
    print('[Changes commited]')
    conn.close()
    print('[Database closed]')

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # Debugging operone data
    logging.debug(unknown_set)
    probs = []
    logging.debug('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    logging.debug('problematic elements that could not easily be converted')
    for el in problematic_list:
        logging.debug(el)

if __name__ == '__main__':
    main()

