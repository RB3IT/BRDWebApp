let TESTREGEXES = [/abc/, /(\d+)ft (\d+)-(\d+)\/(\d+)in/, /n(es(te)d)regex/, /(?<couple>\d+)(?<named>\w+) groups/];

function Source(assert) {
    /* Test that 'source' was inheritted */
    let EXPECTED = ["abc", "(\\d+)ft (\\d+)-(\\d+)\\/(\\d+)in", "n(es(te)d)regex", "(?<couple>\\d+)(?<named>\\w+) groups"];
    let regobj;
    for (let i = 0; i < EXPECTED.length; i++) {
        regobj = new BetteRegExp(TESTREGEXES[i]);
        assert.equal(regobj.source, EXPECTED[i], "Not equal");
    }
}

function Tokens(assert) {
    /* Tests the Tokenizer Results */
    let EXPECTED = [
        [new BREToken("String Literal", "abc")],
        [
            new BREToken("Open Group", "("), new BREToken("Builtin Class", "\\d"), new BREToken("Quantifier", "+"), new BREToken("Close Group", ")"), new BREToken("String Literal", "ft "),
            new BREToken("Open Group", "("), new BREToken("Builtin Class", "\\d"), new BREToken("Quantifier", "+"), new BREToken("Close Group", ")"), new BREToken("String Literal", "-"),
            new BREToken("Open Group", "("), new BREToken("Builtin Class", "\\d"), new BREToken("Quantifier", "+"), new BREToken("Close Group", ")"), new BREToken("String Literal", "\\/"),
            new BREToken("Open Group", "("), new BREToken("Builtin Class", "\\d"), new BREToken("Quantifier", "+"), new BREToken("Close Group", ")"), new BREToken("String Literal", "in")
        ],
        [new BREToken("String Literal", "n"), new BREToken("Open Group", "("), new BREToken("String Literal", "es"), new BREToken("Open Group", "("), new BREToken("String Literal", "te"), new BREToken("Close Group", ")"), new BREToken("String Literal", "d"), new BREToken("Close Group", ")"), new BREToken("String Literal", "regex")],
        [new BREToken("Open Group", "("), new BREToken("Named Group", "?<couple>"), new BREToken("Builtin Class", "\\d"), new BREToken("Quantifier", "+"), new BREToken("Close Group", ")"),
        new BREToken("Open Group", "("), new BREToken("Named Group", "?<named>"), new BREToken("Builtin Class", "\\w"), new BREToken("Quantifier", "+"), new BREToken("Close Group", ")"),
        new BREToken("String Literal", " groups")]
    ];
    for (let i = 0; i < EXPECTED.length; i++) {
        let tokens = _parseSource(RegExp(TESTREGEXES[i]).source);
        assert.deepEqual(tokens, EXPECTED[i]);
    }
}

function BREToken_toString(assert) {
    /* Tests that BREToken.toString functions as expected */
    let TOKENS = [
        new BREToken("String Literal", "abc"),
        new BREToken("Builtin Class", "\d", new BREToken("Quantifier", "+")),
        new BREToken("Character Class", "[fobar]", new BREToken("Quantified Quantifier", "{6}"))
    ];
    let EXPECTED = [
        "abc",
        "\d+",
        "[fobar]{6}"
    ];
    for (let i = 0; i < EXPECTED.length; i++) {
        assert.equal(TOKENS[i].toString(), EXPECTED[i]);
    }
}

function Format(assert) {
    /*  Tests that tokens are properly consolidated into Groups */
    let EXPECTED = [
        [new BREToken("String Literal", "abc")],
        [
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))]), new BREToken("String Literal", "ft "),
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))]), new BREToken("String Literal", "-"),
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))]), new BREToken("String Literal", "\\/"),
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))]), new BREToken("String Literal", "in")
        ],
        [new BREToken("String Literal", "n"), new BREGroup([new BREToken("String Literal", "es"), new BREGroup([new BREToken("String Literal", "te")]), new BREToken("String Literal", "d")]), new BREToken("String Literal", "regex")],
        [new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))], "couple"),
        new BREGroup([new BREToken("Builtin Class", "\\w", new BREToken("Quantifier", "+"))], "named"),
        new BREToken("String Literal", " groups")]
    ];
    for (let i = 0; i < EXPECTED.length; i++) {
        let format = new BetteRegExp(TESTREGEXES[i]).format;
        assert.deepEqual(format, EXPECTED[i]);
    }
}

function Groups(assert) {
    /* Checks the BetteRegExp.groups attribute */
    let EXPECTED = [
        [],
        [
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))]),
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))]),
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))]),
            new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))])
        ],
        [new BREGroup([new BREToken("String Literal", "es"), new BREGroup([new BREToken("String Literal", "te")]), new BREToken("String Literal", "d")]), new BREGroup([new BREToken("String Literal", "te")])],
        [new BREGroup([new BREToken("Builtin Class", "\\d", new BREToken("Quantifier", "+"))], "couple"),
        new BREGroup([new BREToken("Builtin Class", "\\w", new BREToken("Quantifier", "+"))], "named")]
    ];
    for (let i = 0; i < EXPECTED.length; i++) {
        let groups = new BetteRegExp(TESTREGEXES[i]).groups;
        assert.deepEqual(groups, EXPECTED[i]);
    }
}

function BREGroup_toString(assert) {
    /* Tests the BREGroup's toString method */
    let GROUPS = [
        new BREGroup([new BREToken("String Literal", "abc")]),
        new BREGroup([new BREToken("Builtin Class", "\d", new BREToken("Quantifier", "+"))])
    ];
    let EXPECTED = ["abc", "\d+"];

    for (let i = 0; i < EXPECTED.length; i++) {
        assert.equal(GROUPS[i].toString(), EXPECTED[i]);
    }
}

function ConstructString(assert) {
    /* Tests some basic uses of BetteRegExp.constructString */
    let EXPECTED = [
        "abc", "0ft 1-23/45in", "nestedregex", "2unique groups"
    ];
    let VALUES = [
        [],
        ["0", "1", "23", "45"],
        [],
        ["2", "unique"]
    ];
    for (let i = 0; i < Math.min(EXPECTED.length, VALUES.length); i++) {
        let output = new BetteRegExp(TESTREGEXES[i]).constructString(...VALUES[i]);
        assert.equal(output, EXPECTED[i]);
    }
}

function BREResultArray_exec(assert) {
/* Tests that calling BRE.exec returns a special Array object (BREResultArray) with all the original properties, plus additional properties from BRE 
    
    TEST NOTE: The .groups property is tested separately, as its structure needs to be specifically tested.
*/
    let EXPECTED = [
        ["abc"],
        ["1ft 2-3/4in", "1", "2", "3", "4"],
        ["nestedregex", "ested", "te"],
        ["2named groups", "2", "named"]
    ];
    Object.assign(EXPECTED[0], { index: 0, input: "abc"});
    Object.assign(EXPECTED[1], { index: 0, input: "1ft 2-3/4in" });
    Object.assign(EXPECTED[2], { index: 0, input: "nestedregex" });
    Object.assign(EXPECTED[3], { index: 0, input: "2named groups" });
    let VALUES = [
        "abc",
        "1ft 2-3/4in",
        "nestedregex",
        "2named groups"
    ];
    // (Assumedly) Because the returntype of exec() is an Array, QUnit only
    // deepEquals() Array indicies, so we have to test properties individually
    // Also, see docstring note on groups
    let ATTRS = ['index', 'input'];
    for (let i = 0; i < Math.min(EXPECTED.length, VALUES.length); i++) {
        let regex = new BetteRegExp(TESTREGEXES[i]);
        let output = regex.exec(VALUES[i]);
        assert.deepEqual(output, EXPECTED[i]);
        assert.equal(output.parent, regex);
        for (let attr of ATTRS) {
            assert.deepEqual(output[attr], EXPECTED[i][attr]);
        }
    }
}

function Exec_reset(assert){
/* Tests that the reset argument of BetteRegExp.exec functions as expected */
    EXPECTED = [3, 7, 17]
    let regex = new BetteRegExp("cat","g");
    let input = "cat cat not a cat ever";
    for (let i = 0; i < EXPECTED.length; i++) {
        regex.exec(input);
        assert.equal(regex.lastIndex, EXPECTED[i]);
    }
    for (let i = 0; i < EXPECTED.length; i++) {
        regex.exec(input,true);
        assert.equal(regex.lastIndex, 3);
    }
}

function BREResultArray_groups(assert) {
    /* Tests the .groups property of BREResutlArray to ensure it is accurate and properly formatted */
    let EXPECTED = [
        {},
        {
            1: { value: "1", index: 0, name: 1},
            2: { value: "2", index: 4, name: 2},
            3: { value: "3", index: 6, name: 3},
            4: { value: "4", index: 8, name: 4}
        },
        {
            1: { value: "ested", index: 1, name: 1},
            2: { value: "te", index: 3, name: 2}
        },
        {
            1: { value: "2", index: 0, name: 1},
            2: { value: "named", index: 1, name: 2},
            "couple": { "value": "2", "index": 0, name: "couple"},
            "named": { "value": "named", "index": 1, name: "named"}
        }
    ];
    let VALUES = [
        "abc",
        "1ft 2-3/4in",
        "nestedregex",
        "2named groups"
    ];

    for (let i = 0; i < Math.min(EXPECTED.length, VALUES.length); i++) {
        let output = new BetteRegExp(TESTREGEXES[i]).exec(VALUES[i]);
        assert.deepEqual(output.groups, EXPECTED[i]);
    }
}

function BREResultArray_groupAt(assert) {
/* Tests the functionality of BREResultArray_groupAt */
    let VALUES = [
        [],
        ["12ft 3-45/67in", 7],
        ["nestedregex", 4],
        ["100_new groups",0]
    ];
    let EXPECTED = [
        null,
        { value: "45", index: 7, name: 3 },
        { value: "te", index: 3, name: 2 },
        { value: "100", index: 0, name: 1 }
    ];
    for (let i = 0; i < Math.min(EXPECTED.length, VALUES.length); i++) {
        if (!EXPECTED[i]) continue;
        let output = new BetteRegExp(TESTREGEXES[i]).exec(VALUES[i][0]).groupAt(VALUES[i][1]);
        assert.deepEqual(output, EXPECTED[i]);
    }
}

function BREResultArray_groupAt_fuzzy(assert) {
    /* Tests the functionality of BREResultArray_groupAt in fuzzy mode */
    let TESTREGEX = new BetteRegExp("(group1) ((group3) group2) (gro(group5)up4)");
    let TESTSTRING = "group1 group3 group2 grogroup5up4";
    // Sanity Check
    assert.ok(TESTREGEX.test(TESTSTRING));
    let TESTRESULT = TESTREGEX.exec(TESTSTRING);

    let MODES = ["fuzzy", "fuzzy+", "fuzzy-"];
    let VALUES = [0, 6, 13, 20, 23];
    // Expected Group Numbers for modes ["fuzzy","fuzzy+","fuzzy-"] for each value
    let EXPECTED = [
        [1, 1, 1],
        [3, 3, 1],
        [2, 2, 2],
        [4, 4, 3],
        [4, 4, 4]
    ];
    let mode, result;
    for (let i = 0; i < Math.min(EXPECTED.length, VALUES.length); i++) {
        for (let m = 0; m < MODES.length; m++) {
            result = TESTRESULT.groupAt(VALUES[i], MODES[m]);
            assert.equal(result.name, EXPECTED[i][m],`Index ${VALUES[i]}; Mode ${MODES[m]}`);
        }
    }
}

let TESTS = [
    ["Source Test", Source],
    ["Token Test", Tokens],
    ["Token.toString Test", BREToken_toString],
    ["Format Test", Format],
    ["Groups Test", Groups],
    ['Groups.toString Test', BREGroup_toString],
    ["ConstructString Test", ConstructString],
    ["Exec Test", BREResultArray_exec],
    ["Exec Reset Test", Exec_reset],
    ["ResultGroups Test", BREResultArray_groups],
    ["ResultArray.groupAt Test", BREResultArray_groupAt],
    ["ResultArray.groupAt Fuzzy Test", BREResultArray_groupAt_fuzzy]
];
for (let [name, test] of TESTS) {
    console.log(name);
    QUnit.test(name, test);
}