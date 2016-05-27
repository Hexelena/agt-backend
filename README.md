# agt-backend
Backend REST-API for an Ancient Greek Translator.

## What works
The "Alpha" version works. You can make requests and use both precise and rough mode. Currently it is still limited to ascii words. 

## TODO
Transform incoming requests to the internal ascii representation. That includes greek inputs.
Maybe some small changes on the internal representation are necessary (e.g. ch -> c).
Some frontend would be nice >.<.

## How it works
The website [operone.de](http://operone.de) has a [section](http://operone.de/altspr/wadinhalt.html) with an ancient greek dictionary.  
[dbgen.py](dbgen/dbgen.py) scrapes all the entries and writes them into a sqlite database.  
The node server then accesses the database and provides a REST-API.
A rough scheme of how this is works:  
<img src="concept/concept.png" width=700px>


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
| roughword      | The greek word transformed with the rough-dictionary |
| preciseword    | The greek word transformed with the precise dictionary |
| word           | The primary lookup word.                           |
| alternatewords | All alternate words joined by commas               |
| translation    | The translation. This is still entirely unformatted|
  
