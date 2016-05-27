"use strict";


var simplerDict = {

    // standard accents for Alpha
    "ὰ": "α",
    "ά": "α",
    "ᾶ": "α",
    // spiriti for Alpha
    "ἀ": "α",
    "ἁ": "α",
    // spiriti and accents for Alpha
    "ἄ": "α",
    "ἅ": "α",
    "ἂ": "α",
    "ἃ": "α",
    "ἇ": "α",
    "ἆ": "α",

    // Alpha with whateverthe****
    // TODO: figure out what this is.
    // Maybe it's long/short sign...
    "ᾱ": "α",
    "ᾰ": "α",

    // standard accents for Epsilon
    "ὲ": "ε",
    "έ": "ε",
    // spiriti for Epsilon
    "ἑ": "ε",
    "ἐ": "ε",
    // spiriti and accents for Epsilon
    "ἓ": "ε",
    "ἕ": "ε",
    "ἒ": "ε",
    "ἔ": "ε",

    // standard accents for Eta
    "ὴ": "η",
    "ή": "η",
    "ῆ": "η",
    // spiriti for Eta
    "ἠ": "η",
    "ἡ": "η",
    // spiriti and accents for Eta
    "ἣ": "η",
    "ἥ": "η",
    "ἢ": "η",
    "ἤ": "η",
    "ἧ": "η",
    "ἦ": "η",

    // accents for Iota
    "ὶ": "ι",
    "ί": "ι",
    "ῖ": "ι",
    // spiriti for Iota
    "ἱ": "ι",
    "ἰ": "ι",
    // spiriti and accents for Iota
    "ἳ": "ι",
    "ἵ": "ι",
    "ἲ": "ι",
    "ἴ": "ι",
    "ἷ": "ι",
    "ἶ": "ι",

    // accents for Omikron
    "ὸ": "ο",
    "ό": "ο",
    // spiriti for Omikron
    "ὁ": "ο",
    "ὀ": "ο",
    // spiriti and accents for Omikron
    "ὃ": "ο",
    "ὅ": "ο",
    "ὂ": "ο",
    "ὄ": "ο",


    // spiriti for Rho
    "ῤ": "ρ",
    "ῥ": "ρ",

    // standard accents for Ypsilon
    "ύ": "υ",
    "ὺ": "υ",
    "ῦ": "υ",
    // spiriti for Ypsilon
    "ὐ": "υ",
    "ὑ": "υ",
    // spiriti and accents for Ypsilon
    "ὓ": "υ",
    "ὕ": "υ",
    "ὒ": "υ",
    "ὔ": "υ",
    "ὗ": "υ",
    "ὖ": "υ",

    // accents for Omega
    "ὼ": "ω",
    "ώ": "ω",
    "ῶ": "ω",
    // spiriti for Omega
    "ὡ": "ω",
    "ὠ": "ω",
    // spiriti and accents for Omega
    "ὣ": "ω",
    "ὥ": "ω",
    "ὢ": "ω",
    "ὤ": "ω",
    "ὧ": "ω",
    "ὦ": "ω",

    // #######################
    // special simpilfications
    // #######################

    // hyphens are not needed
    "-": "",
    // strip whitespaces
    " ": "",

    // unify Sigmas
    "ς": "σ"
};

var abc = "αβγδεζηϑικλμνξοπρστυφχψω";

function normalizeGreek(inputString) {
    var newString = "";

    for (var i = 0; i < inputString.length; i++) {
        if (inputString[i] in simplerDict) {
            newString += simplerDict[inputString[i]];
        } else {
            newString += inputString[i];
        }
    }
    return newString;
}

function greekToAscii(inputString, precise) {
    if (typeof(precise) != 'boolean') {
        throw new TypeError('type of precise is not boolean but <' + typeof(precise) + '>');
    }
    

}

function isAfter(string, reference) {
    var search = normalizeGreek(string);
    var ref = normalizeGreek(reference);

    if (search === ref) {
        //console.log("the strings are equal");
        return true;
    }

    var i = 0;
    while (true) {
        //console.log("Entering Iteration No." + i + " of isAfter: (" + abc.indexOf(search[i]) + " vs " + abc.indexOf(ref[i]) + ").");
        if (abc.indexOf(search[i]) > abc.indexOf(ref[i])) {
            //console.log("'" + search + "' comes after '" + ref + "' | -> true");
            return true;
        } else if (abc.indexOf(search[i]) < abc.indexOf(ref[i])) {
            //console.log("'" + search + "' comes before '" + ref + "' | -> false");
            return false;
        } else { // equal
            i++;
        }
    }
}

module.exports = {
    abc             : abc,
    isAfter         : isAfter,
    normalizeGreek  : normalizeGreek
};