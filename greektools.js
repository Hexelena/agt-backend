"use strict";

var GREEK_TO_ASCII_ROUGH = {
    "α": "a",
    "β": "b",
    "γ": "g",
    "δ": "d",
    "ε": "e",
    "ζ": "z",
    "η": "e",
    "θ": "t",
    "ι": "i",
    "κ": "k",
    "λ": "l",
    "μ": "m",
    "ν": "n",
    "ξ": "x",
    "ο": "o",
    "π": "p",
    "ρ": "r",
    "σ": "s",
    "τ": "t",
    "υ": "y",
    "φ": "f",
    "χ": "ch",
    "ψ": "ps",
    "ω": "o",
    " ": " "    // mark as "known" letter
};

var GREEK_TO_ASCII_PRECISE = {
    "α": "a",
    "β": "b",
    "γ": "g",
    "δ": "d",
    "ε": "e",
    "ζ": "z",
    "η": "ä",   // ä <> e
    "θ": "th",  // th <> t
    "ι": "i",
    "κ": "k",
    "λ": "l",
    "μ": "m",
    "ν": "n",
    "ξ": "x",
    "ο": "o",
    "π": "p",
    "ρ": "r",
    "σ": "s",
    "τ": "t",
    "υ": "y",
    "φ": "ph",  // ph <> f
    "χ": "ch",
    "ψ": "ps",
    "ω": "oo",  // oo <> o
    " ": " "    // mark as "known" letter
};

// helpful link:
// http://www.utf8-chartable.de/unicode-utf8-table.pl?start=7936&number=128&names=-&utf8=string-literal
// upper part is taken from the above link
var GREEK_SIMPL_DICT = {
    // Alpha
    "ἀ": "α",
    "ἁ": "α",
    "ἂ": "α",
    "ἃ": "α",
    "ἄ": "α",
    "ἅ": "α",
    "ἆ": "α",
    "ἇ": "α",
    "Ἀ": "α",
    "Ἁ": "α",
    "Ἂ": "α",
    "Ἃ": "α",
    "Ἄ": "α",
    "Ἅ": "α",
    "Ἆ": "α",
    "Ἇ": "α",
    // Epsilon
    "ἐ": "ε",
    "ἑ": "ε",
    "ἒ": "ε",
    "ἓ": "ε",
    "ἔ": "ε",
    "ἕ": "ε",
    "Ἐ": "ε",
    "Ἑ": "ε",
    "Ἒ": "ε",
    "Ἓ": "ε",
    "Ἔ": "ε",
    "Ἕ": "ε",
    // Eta
    "ἠ": "η",
    "ἡ": "η",
    "ἢ": "η",
    "ἣ": "η",
    "ἤ": "η",
    "ἥ": "η",
    "ἦ": "η",
    "ἧ": "η",
    "Ἠ": "η",
    "Ἡ": "η",
    "Ἢ": "η",
    "Ἣ": "η",
    "Ἤ": "η",
    "Ἥ": "η",
    "Ἦ": "η",
    "Ἧ": "η",
    // Iota
    "ἰ": "ι",
    "ἱ": "ι",
    "ἲ": "ι",
    "ἳ": "ι",
    "ἴ": "ι",
    "ἵ": "ι",
    "ἶ": "ι",
    "ἷ": "ι",
    "Ἰ": "ι",
    "Ἱ": "ι",
    "Ἲ": "ι",
    "Ἳ": "ι",
    "Ἴ": "ι",
    "Ἵ": "ι",
    "Ἶ": "ι",
    "Ἷ": "ι",
    // Omikron
    "ὀ": "ο",
    "ὁ": "ο",
    "ὂ": "ο",
    "ὃ": "ο",
    "ὄ": "ο",
    "ὅ": "ο",
    "Ὀ": "ο",
    "Ὁ": "ο",
    "Ὂ": "ο",
    "Ὃ": "ο",
    "Ὄ": "ο",
    "Ὅ": "ο",
    // Ypsilon
    "ὐ": "υ",
    "ὑ": "υ",
    "ὒ": "υ",
    "ὓ": "υ",
    "ὔ": "υ",
    "ὕ": "υ",
    "ὖ": "υ",
    "ὗ": "υ",
    "Ὑ": "υ",
    "Ὓ": "υ",
    "Ὕ": "υ",
    "Ὗ": "υ",
    // Omega
    "ὠ": "ω",
    "ὡ": "ω",
    "ὢ": "ω",
    "ὣ": "ω",
    "ὤ": "ω",
    "ὥ": "ω",
    "ὦ": "ω",
    "ὧ": "ω",
    "Ὠ": "ω",
    "Ὡ": "ω",
    "Ὢ": "ω",
    "Ὣ": "ω",
    "Ὤ": "ω",
    "Ὥ": "ω",
    "Ὦ": "ω",
    "Ὧ": "ω",
    // all of the above again with acut and gravis but
    // for some reason this have other unicode values
    "ὰ": "α",
    "ά": "α",
    "ὲ": "ε",
    "έ": "ε",
    "ὴ": "η",
    "ή": "η",
    "ὶ": "ι",
    "ί": "ι",
    "ὸ": "ο",
    "ό": "ο",
    "ὺ": "υ",
    "ύ": "υ",
    "ὼ": "ω",
    "ώ": "ω",

    // necessary accent signs not defined in above link:

    "ά": "α",
    "ᾱ": "α",
    "ᾷ": "α",
    "ᾶ": "α",
    "ᾴ": "α",
    "ᾳ": "α",
    "ᾀ": "α",
    "ᾰ": "α",
    "ᾁ": "α",
    "ᾆ": "α",
    "ᾄ": "α",

    "έ": "ε",

    "ῃ": "η",
    "ῆ": "η",
    "ῄ": "η",
    "ή": "η",
    "ῇ": "η",

    "ῗ": "ι",
    "ῒ": "ι",
    "Ι": "ι",
    "ῖ": "ι",
    "ῐ": "ι",
    "ϊ": "ι",
    "ΐ": "ι",
    "ί": "ι",
    "ῑ": "ι",
    "ΐ": "ι",

    "ό": "ο",

    "ῤ": "ρ",
    "ῥ": "ρ",

    "ύ": "υ",
    "ΰ": "υ",
    "ῦ": "υ",
    "ῠ": "υ",
    "ῡ": "υ",
    "ΰ": "υ",
    "ϋ": "υ",

    "ώ" :"ω",
    "ᾤ" :"ω",
    "ᾠ" :"ω",
    "ῲ" :"ω",
    "ῴ" :"ω",
    "ῳ" :"ω",
    "ῷ" :"ω",
    "ῶ": "ω",

    // Capitals:
    
    // (with accents)
    "Ῥ": "ρ",
    "Έ": "ε",

    "Α": "α",
    "Β": "β",
    "Γ": "γ",
    "Δ": "δ",
    "Ε": "ε",
    "Ζ": "ζ",
    "Η": "η",
    "Θ": "θ",
    "Κ": "κ",
    "Λ": "λ",
    "Μ": "μ",
    "Ν": "ν",
    "Ξ": "ξ",
    "Ο": "ο",
    "Π": "π",
    "Ρ": "ρ",
    "Σ": "σ",
    "Τ": "τ",
    "Υ": "υ",
    "Φ": "φ",
    "Χ": "χ",
    "Ψ": "ψ",
    "Ω": "ω",

    // %%%%%%%%%%%%%%%%%%%%%%%
    // special simpilfications
    // %%%%%%%%%%%%%%%%%%%%%%%

    // hyphens are not needed
    "-": "",
    // strip whitespaces
    // don't do that it takes spaces between words
    // better strip manually
    //" ": "",

    // no apostrophs
    "'": "",

    // unify Rhos
    "ϱ": "ρ",
    // unify Sigmas
    "ς": "σ",
    // unify Thetas
    "ϑ": "θ"
};

var GREEK_ALPHABET = "αβγδεζηϑικλμνξοπρστυφχψω";


function normalizeGreek(inputString) {
    var newString = "";

    for (var i = 0; i < inputString.length; i++) {
        if (inputString[i] in GREEK_SIMPL_DICT) {
            newString += GREEK_SIMPL_DICT[inputString[i]];
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
        //console.log("Entering Iteration No." + i + " of isAfter: (" + GREEK_ALPHABET.indexOf(search[i]) + " vs " + GREEK_ALPHABET.indexOf(ref[i]) + ").");
        if (GREEK_ALPHABET.indexOf(search[i]) > GREEK_ALPHABET.indexOf(ref[i])) {
            //console.log("'" + search + "' comes after '" + ref + "' | -> true");
            return true;
        } else if (GREEK_ALPHABET.indexOf(search[i]) < GREEK_ALPHABET.indexOf(ref[i])) {
            //console.log("'" + search + "' comes before '" + ref + "' | -> false");
            return false;
        } else { // equal
            i++;
        }
    }
}

module.exports = {
    GREEK_ALPHABET  : GREEK_ALPHABET,
    isAfter         : isAfter,
    normalizeGreek  : normalizeGreek
};