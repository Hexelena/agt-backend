"use strict";

var express = require("express");
var Sequelize = require("sequelize");

var sequelize = new Sequelize(undefined, undefined, undefined, {
    'dialect': 'sqlite',
    'storgae': 'agt-dummy.sqlite'
});

var greek = require("./greektools");

var app = express();

var PORT = 8081;

//var operoneurl = "http://localhost/web/phayax/agt/res/operone/altspr/wadinhalt.html";
//var operonebaseurl = "http://localhost/web/phayax/agt/res/operone/altspr/";

//var pageDict = [];
//var pageContent = [];

// ROOT

app.get("/", function (req, res) {
    res.send("root of the agt-backend");
});

// DICTIONARY ROOT
app.get("/dict", function (req, res) {
    console.log("request for dict main page");

    //if (pageDict.length > 0) {
    //    res.send(pageDict);
    //} else {
    //    res.send("An Error occured. index scraping was unsuccesful!");
    //}
    res.send('root of the dict lookup.')
});

// DICTIONARY QUERY
app.get("/dict/:query", function (req, res) {
    console.log("incoming dict request for '" + req.params.query + "'. Processing as " + greek.normalizeGreek(req.params.query) + "'.");
    //res.send("received request for '" + req.params.query + "'. Searching for '" + greek.normalizeGreek(req.params.query) + "'.\nResult is possibly on page " + findPageLink(req.params.query));
    // var result = {
    //     "origSearch" : req.params.query,
    //     "convertedSearch" : greek.normalizeGreek(req.params.query),
    //     "page" : findPageLink(req.params.query),
    //     "pageContent" : ""
    // }
    res.status(501).json({'error':'not implemented'});
});

app.listen(PORT);

console.log("agt-backend started on port " + PORT);

//console.log("generating page dict");
//generatePageDict();