"use strict";

var express = require("express");
var sqlite3 = require("sqlite3");

var greek = require("./greektools");

var app = express();

var PORT = 8081;

// open db connection
var db = new sqlite3.Database('agt.sqlite');

// ROOT

app.get("/", function (req, res) {
    console.log("GET / - root of the agt-backend")
    res.send("root of the agt-backend");
});

// DICTIONARY ROOT
app.get("/dict", function (req, res) {
    console.log("GET /dict - dict main page");
    db.get('SELECT COUNT(*) FROM operonedict;', function(err, rows) {
        res.json({
            'info': {
                'description': 'root of the dict lookup.',
                'entries': rows['COUNT(*)'],
                'lookup-modes': ['precise','rough'],
                'lookup-url': '/dict/<mode>/<query>'
        }
            })
    });
});

// DICTIONARY QUERY
app.get("/dict/:mode/:query", function (req, res) {
    // logging
    console.log("GET /dict/"+ req.params.mode + "/" + req.params.query + " -> Processing as " + greek.normalizeGreek(req.params.query) + "'.");

    // parameter error handling
    // FIXME: somehow write that if expression better.
    var mode = req.params.mode;
    if (!(mode === 'precise' || mode == 'rough')) {
        res.status(400).json({'error': "unknown mode + '" + req.params.mode + "'' !"});
        return;
    }
    // processing the request
    // the query searches for a word starting with the query 
    // then orders them by length (assuming that words that have a more similar length to the query are more relevant)
    // then limits them (for now)
    if (req.params.mode === "rough") {
        db.all('SELECT greek, alternategreek, translation FROM operonedict WHERE roughword LIKE ? ORDER BY LENGTH(greek) ASC LIMIT 10;',[req.params.query + '%'], function(err, rows) {
            if (err) {
                console.log('error: ' + err);
            }
            res.json(rows)
        });
    } else if (req.params.mode === "precise") {
        db.all('SELECT greek, alternategreek, translation FROM operonedict WHERE preciseword LIKE ? ORDER BY LENGTH(greek) ASC LIMIT 10;',[req.params.query + '%'], function(err, rows) {
            if (err) {
                console.log('error: ' + err);
            }
            res.json(rows)
        });
    }
});

// off we go!
app.listen(PORT);

console.log("agt-backend started on port " + PORT);
