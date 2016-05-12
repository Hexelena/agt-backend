# agt-backend
Backend REST-API for an Ancient Greek Translator.
  

## How it works
The website operone.de has a section with an ancient greek dictionary.  
[generatedb.py](generatedb.py) scrapes all the entries and writes them into a sqlite database.  
The node server shall then access the database and provide data via a REST-API.

## Data Model:
Currently there are two tables in the database:
pageindex and pagecontent

#### Index
| field | descrption |
|-------|------------|
| idx   | index of the page <br> (starting with 1 like the page urls) 
| page  | The first entry on this page |
| link  | The url of this page |

#### Entries
For now the data is stored very simply. In the future this will likely be extended.
Every entry has the following fields:

|    field       |   description                                      |
|----------------|----------------------------------------------------|
| pagenum        | The number of the page on which the word is listed |
| word           | The primary lookup word.                           |
| alternatewords | All alternate words joined by commas               |
| translation    | The translation. This is still entirely unformatted|
  
