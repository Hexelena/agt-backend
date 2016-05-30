#! /usr/bin/env python3
"""
Tool to parse all greek dictionary entries of the website operone.de.
The tool is tailored to this website. Some parts of it might be considered hacky, but then the website is so
inconsistent it can't be helped.
[USE]
To run the tool just run this script and click the start button on the tkinter interface.
Dependencies:
- python standard library (including tkinter)
- BeautifulSoup 4
"""
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


OPERONE_URL = 'http://localhost/web/phayax/agt/res/operone/altspr/wadinhalt.html'
OPERONE_BASE_URL = "http://localhost/web/phayax/agt/res/operone/altspr/"

DB_NAME = 'agt.sqlite'

#OPERONE_URL = 'http://www.operone.de/altspr/wadinhalt.html'
#OPERONE_BASE_URL = "http://www.operone.de/altspr/"

class StdoutRedirector:
    '''
    A class that implements the same functionality as a textiowrapper.
    Used to redirect stdout to a text-widget.
    '''
    def __init__(self, text_widget):
        self.text_handle = text_widget

    def write(self, string):
        """
        Append the text to the text-widget.
        """
        self.text_handle.insert(tk.END, string)

    def flush(self):
        """
        Method of the original textiowrapper.
        It is rarely called but can cause weird problems.
        """
        self.text_handle.update()

class App(tk.Tk):
    """
    Tkinter window class.
    Has a label, a progressbar, a start and quit button and a text widget for output.
    Redirects the stdout stream into the text widget during execution.
    """

    def __init__(self, cursor):
        tk.Tk.__init__(self)
        self.initialize()
        self.db_handle = cursor

    def initialize(self):
        """
        This method sets up all tkinter widgets and redirects the stdout stream.
        """
        self.title('Operone -> Database Parser')
        self.grid()
        self.minsize(800, 600)

        self.grid_columnconfigure(1, weight=1)

        self.info_text = tk.Label(self, text="Huhu")
        self.info_text.grid(row=0, column=1, padx=5, pady=5)

        start_button = tk.Button(self, text='Start Parsing', command=self.parse)
        start_button.grid(row=2, column=1, padx=5, pady=5)
        quit_button = tk.Button(self, text='Close', fg='red', command=self.quit)
        quit_button.grid(row=3, column=1, padx=5, pady=5)


        self.progress = tk.DoubleVar()
        self.progress.set(0)
        
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", maximum=266, length=500, mode="determinate", variable=self.progress)
        self.progress_bar.grid(row=1, column=1, sticky="WE", padx=5, pady=5)

        #self.barstarted = False
        y_scrollbar = tk.Scrollbar(self, orient='vertical')
        y_scrollbar.grid(row=4, column=2, sticky='NSE')
        x_scrollbar = tk.Scrollbar(self, orient='horizontal')
        x_scrollbar.grid(row=5, column=1, sticky='WE')

        self.output = tk.Text(self, wrap=tk.NONE, height=4, width=50, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.output.grid(row=4, column=1, sticky='NSWE', padx=5, pady=5)
        y_scrollbar.config(command=self.output.yview)
        x_scrollbar.config(command=self.output.xview)


        self.grid_rowconfigure(4, weight=1)

        self.entries_parsed = 0

        # backup stdout
        self.orig_stdout = sys.stdout
        # reroute stdout to application text widget
        sys.stdout = StdoutRedirector(self.output)


    def quit(self):
        """
        Restores the stdout-stream to it's original state and closes the window.
        """
        # restore original stdout
        sys.stdout = self.orig_stdout
        self.destroy()

    def parse(self):
        """
        Calls the methods to parse all entries and updates the progress_bar widget to provide visual feedback.
        First calls parse_index to get all page links. Then calls the parse_page method on all the links.
        Finally shows duration and parsed entry count when all pages are parsed.
        """
        # keep track of the time
        start_time = datetime.datetime.now()
        self.progress.set(0)
        pages = parse_index()
        for page in pages:
            # update the info text
            self.info_text.configure(text='Parsing page {}'.format(page))
            # count the number of entries parsed
            self.entries_parsed += parse_page(self.db_handle, page)
            # update the progress_bar value and update the widget
            self.progress.set(self.progress.get() + 1.0)
            self.progress_bar.update()
        end_time = datetime.datetime.now()
        time_passed = (end_time - start_time).total_seconds()
        # display total time and parsed entry count
        self.info_text.configure(text='Finished Parsing: {} entries processed in {:.1f} seconds'.format(self.entries_parsed, time_passed))

def get_list_links(soup):
    """
    Takes all "li > a" tags and returns them.
    The correct selector is probably "li > a:firstChild".
    """
    # get all li's
    lis = soup.find_all('li')
    # get all a's that are inside the captured li's.
    lis = [el.find('a') for el in lis if len(el.find_all('a')) > 0]

    return lis

def fix_bad_html(source):
    """
    Takes bad html lists and puts closing tags on the end of each line
    with a list tag and no closing tag.
    """
    # process each line on it's own
    source = source.split('\n')

    new_source = []
    
    for line in source:
        line = line.strip()
        # check if its a relevant line
        # we know that only entries are li's
        if '<li>' in line:
            if not '</li>' in line:
                line += '</li>'

        new_source.append(line)

    fixed_source = '\n'.join(new_source)
    return fixed_source


def create_tables(connection):
    """
    Currently only creates the table for the operone dictionary.
    """
    
    # Create a table of the content of all pages.
    connection.execute('CREATE TABLE IF NOT EXISTS operonedict(roughword TEXT, preciseword TEXT, greek TEXT, alternategreek TEXT, translation TEXT);')
    logging.info("[Created table 'operonedict']")


def parse_exceptions(line):
    """
    This method is used to fix problematic entries:
    It fixes misplaced closing span tags.
    It uses the imported ALL_FIX_DICT to fix problems that are too specific ore rare to write a parsing function.
    """
    # avoid weird errors with BeautifulSoup objects.
    if not isinstance(line, str):
        raise TypeError('type str expected. found {}'.format(type(line)))

    # detect if there was a missing </span> tag that got wrongly autocorrected by beautifulsoup
    # this is done by checking if there is anything between the closing li tag and the closing span tag.
    close_span = line.find('</span>')
    close_span += len('</span>')
    close_li = line.find('</li>')
    if len(line[close_span:close_li].strip()) == 0:
        logging.info('-----------------------------------------------------------------------')
        logging.info('[Warning] Possible problem in the following line.:\n\t%s', (line,))
        # remove the wrongly placed closing span
        line = line[:line.find('</span>')] + line[line.find('</li>'):]
        # add the closing span at the first space after the greek word
        # this is not failproof but the problem will be reported and can be checked
        insert_idx = line.find('<span class="hel">')
        # note the trailing space - there is "always"(ha!) a space between the tag and the word.
        # so we are setting the index right before the beginning of the word
        # if not it is placed in the word which is just fine
        insert_idx += len('<span class="hel"> ')
        # look for the first whitespace starting from the previously
        # determined index.
        insert_idx = line.find(' ', insert_idx)
        # insert the closing span tag plus a comma for separation since
        # the later part expects the word to be divided from the translation by a comma
        # if we introduce a comma too much that is not a problem since the later part will
        # filter out commas.
        line = line[:insert_idx] + ', </span>' + line[insert_idx:]
        logging.info('\t\t Attempting to fix the mentioned problem. Please check:\n\t\t%s', (line,))

    # apply fix dict for whole lines
    for element in ALL_FIX_DICT:
        line = line.replace(element, ALL_FIX_DICT[element])

    return line


def parse_index():
    """
    Downloads the index page of the operone dictionary and returns a list of links to the subpages.
    """
    # get source of index page
    source = urllib.request.urlopen(urllib.request.Request(OPERONE_URL)).read() #(chapterUrl, headers={'User-Agent': AGENT_NAME + ' Browser'})).read()
    source = str(source)
    source = html.unescape(source)

    soup = BeautifulSoup(source, 'html.parser')

    pages = get_list_links(soup)

    #for idx, entry in enumerate(pages):
    #    page = entry.get_text(strip=True)
    #    link = entry.get('href')
    #    params = (idx + 1, page, link,)
    #    cursor.execute('INSERT INTO pageindex VALUES(?, ?, ?);', params)

    return pages

def parse_page(cursor, page):
    """
    Parses a single page of the operone dictionary:
    Gets the page source:
    fixes problematic html tags(not closed or wrongly placed mostly)
    for every entry on the page:
        runs parse_exceptions on the line
        takes the different parts of the line.
        simplifies and copys the transformed versions.
        writes the entry to the database
    """
    page = urllib.request.urlopen(urllib.request.Request(OPERONE_BASE_URL + page.get('href'))).read()
    page = page.decode('ISO-8859-1') # encoding of the operone pages
    page = html.unescape(page)
    #page = str(page) # cast to string (from stream)
    #page = html.unescape(page) # unescape greek letters
    page = fix_bad_html(page)

    # this automatically adds closing span tags at the end of a line if none are present
    page_soup = BeautifulSoup(page, 'html.parser')
    lis = page_soup.find_all('li')

    for element in lis:
        #print(element)
        # ok, we are getting additional translations or variations that belong to the word
        # for now we will be ignoring them by using only the first child.

        corrected_line = parse_exceptions(str(element))
        element = BeautifulSoup(corrected_line, 'html.parser')

        # get_text can strip whitespaces but since we need the comma stripped as well
        # it makes more sense to put both into one context.
        # vocab is the raw string of the entry
        vocab = element.findChild().findChild().get_text().strip(', ')

        # apply fix dict for vocab part
        for entry in VOCAB_FIX_DICT:
            vocab = vocab.replace(entry, VOCAB_FIX_DICT[entry])

        # versions is a list of the different lookup words of the entry
        versions = [version.strip() for version in vocab.split(',')]
        # greek is the first version - we will just assume that this is what we want ...
        greek = versions[0]
        # alternate are all other versions concatenated by commas.
        alternate = ",".join(versions[1:])
        # start index behind the first span. used to separate
        # the lookup word from the translation since there can be
        # greek letters and tags in the translation (otherwise we could just the text with recursive=False to eliminate text in tags)
        tl_start_index = str(element).find('</span>')
        tl_start_index += len('</span>')

        # ok, so here we take off the first part of the entry which
        # contains the greek word. Then we feed the remaining string into
        # a new BeautifulSoup instance and strip remaining tags in the translation
        # with the get_text() method.
        sub_text = BeautifulSoup((str(element))[tl_start_index:], 'html.parser')
        translation = str(sub_text.get_text()).strip()

        rough = greek_to_ascii(greek_simplify(greek), False)
        precise = greek_to_ascii(greek_simplify(main), True)
        cursor.execute('INSERT INTO operonedict VALUES(?, ?, ?, ?, ?)', (rough, precise, main, alternate, translation,))
        #print(translation)

    return len(lis)


def main():
    """
    Removes the old db file.
    Creates new db and creates Tables.
    Then starts the window.
    After closing the window, the two indices are created.
    Then all changes are committed and the database is closed.
    """
    
    logging.basicConfig(filename='dbgen.log', filemode='w', level=logging.WARNING)
    # remove old db file
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print('[Removed old database]')

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # sqlite setup
    conn = sqlite3.connect(DB_NAME)
    print('[Created new database]')
    cursor = conn.cursor()

    create_tables(cursor)


    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # tkinter related
    app = App(cursor)
    app.mainloop()

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # create db indices
    conn.execute('CREATE INDEX roughindex ON operonedict (roughword)')
    print('[Created index for rough lookup]')
    conn.execute('CREATE INDEX preciseindex ON operonedict (preciseword)')
    print('[Created index for precise lookup]')
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # sqlite cleanup
    conn.commit()
    print('[Changes commited]')
    conn.close()
    print('[Database closed]')

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    # Debugging operone data
    logging.debug('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    logging.debug('problematic elements that could not easily be converted')

if __name__ == '__main__':
    main()

