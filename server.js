"use strict";
var express = require("express");
var request = require("request");
var cheerio = require("cheerio");

var greek = require("./greek");

var app = express();

var PORT = 8081;

var operoneurl = "http://localhost/web/phayax/agt/res/operone/altspr/wadinhalt.html";
var operonebaseurl = "http://localhost/web/phayax/agt/res/operone/altspr/";

var pageDict = [];
var pageContent = [];

// ROOT

app.get("/", function (req, res) {
    res.send("root of the agt-backend");
});

// DICTIONARY ROOT
app.get("/dict", function (req, res) {
    console.log("request for dict main page");

    if (pageDict.length > 0) {
        res.send(pageDict);
    } else {
        res.send("An Error occured. index scraping was unsuccesful!");
    }

});

// DICTIONARY QUERY
app.get("/dict/:query", function (req, res) {
    console.log("incoming dict request for '" + req.params.query + "'. Processing as " + greek.normalizeGreek(req.params.query) + "'.");
    //res.send("received request for '" + req.params.query + "'. Searching for '" + greek.normalizeGreek(req.params.query) + "'.\nResult is possibly on page " + findPageLink(req.params.query));
    var result = {
        "origSearch" : req.params.query,
        "convertedSearch" : greek.normalizeGreek(req.params.query),
        "page" : findPageLink(req.params.query),
        "pageContent" : ""
    }
    res.json(result);
});

function generatePageDict() {

    var tempPageDict = [];

    request(operoneurl, function (error, response, html) {
        if (!error) {


            var $ = cheerio.load(html);
            var relevantData = $("li a");

            for (var i = 0; i < relevantData.length; i++) {
                var link = relevantData[i].attribs.href;
                var part = relevantData[i].children[0].data;

                // small fix because operone starts with αλφα as first entry!
                if (i === 0) {
                    part = "α";
                }

                part = greek.normalizeGreek(part);

                var newObject = {
                    "begin" : part,
                    "link" : link
                };

                tempPageDict.push(newObject);
            }
            pageDict = tempPageDict;
            
        }
    });
}

function findPageLink(query) {
    var index = 0;

    // iterate to find the page in which to search the query string
    // proceed by increasing until it is one step too far. Then go back once and return the value.
    while(index < pageDict.length && greek.isAfter(query, pageDict[index].begin)) {
        index++;
    }

    index--;

    return pageDict[index].link;
}

function getPageContent(pageLink) {
    request(pageLink, function(error, response, html) {
        if (!error) {
            var $ = cheerio.load(html);

            var relevantData = $("ul li");

        }
    });
}


app.listen(PORT);


console.log("agt-backend started on port " + PORT);

console.log("generating page dict");
generatePageDict();