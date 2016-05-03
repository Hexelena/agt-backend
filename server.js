var express = require("express");
var request = require("request");
var cheerio = require("cheerio");

var app = express();

var PORT = 8081;

var operoneurl = "http://localhost/web/phayax/agt/res/operone/altspr/wadinhalt.html";

var pageDict = [];

// ROOT

app.get("/", function(req, res) {
	res.send("root of the agt-backend");
});

// DICTIONARY
app.get("/dict", function(req, res) {
	console.log("incoming request");

	request(operoneurl, function(error, response, html) {
		if (!error) {
			var retmsg = "";
			var $ = cheerio.load(html);

			var relevantData = $("li a");
			for (var i = 0; i < relevantData.length; i++) {
				var link = relevantData[i].attribs.href;
				var part = relevantData[i].children[0].data;

				console.log(i + ". : " + part + " -> " + link);
				retmsg += i + ". : " + part + " -> " + link + "\n";

			}
			res.send(retmsg);
		} else {
			res.send("error receiving website");
		}
	})

});

function generatePageDict() {
	
	tempPageDict = [];
	
	request(operoneurl, function(error, response, html) {
		if (!error) {


			var $ = cheerio.load(html);

			var relevantData = $("li a");
			
			for (var i = 0; i < relevantData.length; i++) {
				var link = relevantData[i].attribs.href;
				var part = relevantData[i].children[0].data;
				var newObject = {
					"part" : part,
					"link" : link
				};
				//console.log(newObject);
				tempPageDict.push(newObject);
			}
			pageDict = tempPageDict;
		}
	});
}

app.listen(PORT);

console.log("agt-backend started on port " + PORT);

pageDict = generatePageDict();
console.log("generated page dict");
console.log(pageDict);
setTimeout(function() {
	console.log(pageDict);
}, 3000);