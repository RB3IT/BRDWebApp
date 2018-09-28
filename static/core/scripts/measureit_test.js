// THIS FIRST SECTION WILL BE MOVED TO ANOTHER MODULE
/*                         UnitTest Module

Code in this module is largely based off of Python unittest format.

Module Usage:
    > Create Functions that run tests and throw exceptions on failures.
        *A number of assert{X} functions are available in this module to raise generic exceptions.
    > Set TESTS equal to an array of test Functions to be run.
    > This module automatically runs all Functions in TESTS on document.ready.
*/

// Validation Functions
function assertEqual(a, b, exception) {
    /* Tests Equality

    Accepts up to three arguments:
    First and second arguments are values to compare (per a==b).
    Third arguement is a custom string to be thrown (will be appended with ": ${a}, ${b}")
    */
    if (!(a == b)) {
        if (typeof exception === "undefined") {
            throw new Error(`EqualityError: ${a} != ${b}`);
        } else {
            throw new Error(`${exception}: ${a}, ${b}`);
        };
    };
};

function assertError(f, args) {
    /* Tests that the given function with the given arguments throws an Error

    Accepts two arguments:
    First argument is the function to be run.
    Second are arguments to be passed to the function.
    */
    try {
        f.apply(null, args);
    } catch (e) {
        return true;
    };
    // At this point, we have not thrown an error
    throw new Error(`NoThrowError: ${f}(${args})`);
};

function assertFalse(value, exception) {
    /* Tests that the value is False

    Accepts up to two arguments:
    First is the value to compare to false (using identity ===).
    Second arguement is a custom string to be thrown (will be appended with ": ${value}")
    */
    if (!(value === false)) {
        if (typeof exception === "undefined") {
            throw new Error(`IdentityError: ${value} is not false.`);
        } else {
            throw new Error(`${exception}: ${a}, ${b}`);
        };
    };
};

function assertTrue(value, exception) {
    /* Tests that the value is True

    Accepts up to two arguments:
    First is the value to compare to true (using identity ===).
    Second arguement is a custom string to be thrown (will be appended with ": ${value}")
    */
    if (!(value === true)) {
        if (typeof exception === "undefined") {
            throw new Error(`IdentityError: ${value} is not false.`);
        } else {
            throw new Error(`${exception}: ${a}, ${b}`);
        };
    };
};

// Runtime Function
$(document).ready(function () {
    console.log("Running Tests");
    let success = 0;
    for (test of TESTS) {
        console.log(".");
        try {
            test()
            success++;
        }
        catch (e) {
            console.log(e);
            console.log(e.stack);
        };
    };
    console.log(`${success} Tests Successful out of ${TESTS.length} (${TESTS.length - success} failed)`);
});

// Module Self-Testing
function test_assertError() {
    /* Various tests to make sure assertError is working correctly */
    // Should not Fail
    try {
        assertError(function () { throw 'Error' });
    } catch (e) {
        throw 'assertError threw an unexpected Error: Pass 1';
    }
    // Should Fail
    let tryelse = true
    try {
        assertError(function (a) { return; }, [1]);
    } catch (e) {
        tryelse = false;
        /* This is supposed to raise an Error */
    };
    if (tryelse) {
        throw 'assertError did not throw an Error: Fail 1';
    };
};

function test_assertEqual() {
    /* Various tests to make sure assertTrue is working correctly */
    // Should not Fail
    assertEqual(1, 1);
    assertEqual("a", "a");
    //Should Fail
    for (let args of [[1, 2], ["a", "b"], [[], []]]) {
        // each of these sets of args should fail
        assertError(assertEqual, args);
    };
};

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Actual code for measureit_test

function runTest(options) {
    /* Reusable way to run tests

    Accepts Options:
        inputelement: element to be added to the body
        test: function to be tested
        args: arguments for the function
    */
    let inputelement = options.inputelement;
    let test = options.test;
    let args = options.args;
    // Insert test element into body
    setBody(inputelement);
    // run test
    return test.apply(null, args);
};

function setBody(ele) {
    /* Helper Function that sets the document's Body to only contain the given element */
    $("body").html(ele);
};

function getInputEle() {
    /* Helper Function for creating measureit Inputs and rebinding them */
    let ele = $('<input type="text" class="measureit"/>');
    return ele;
};

function newSetup() {
    /* Helper Function combining getInputEle and setBody and returns a reference to that element */
    setBody(getInputEle());
    measureit_rebind();
    return $("body>input")[0];
};

function setValueCaret(ele, value, caret) {
    /* Helper function that sets the value and the caret position for an input */
    ele.value = value;
    ele.setSelectionRange(caret, caret);
};

function test_runTest() {
    /* Double Checks that runTest works correctly using a trivial example */
    // Before starting, make sure that there is no paragraph in our document already
    assertEqual($("p").length, 0);

    let ele = $("<p>Hello World</p>");
    let output = null;
    let f = function (arg1, arg2) { output = arg1 + arg2 };
    let [arg1, arg2] = [1,2];
    let result = runTest({
        inputelement: ele,
        test: f,
        args: [arg1, arg2]
    });
    // Make sure there is a paragraph in the body
    assertEqual($("p")[0], ele[0]);
    // Make sure that f ran (setting output)
    // with the correct parameters (total should be 3)
    assertEqual(output, 3);
};

function test_repeatableSetup() {
    /* Tests that repeatably calling newSetup only results in 1 new input element returned. */
    for (let i = 0; i < 4; i++) {
        newSetup();
    };
    // Double check that there really is only one ele in the body
    assertEqual($("body>input").length, 1);
};

var RANGINGTESTS = [
    ["12ft 10in", // Test String
        [
            [0, 2, 0, 5], // start2, end2, caretstart, caretend
            [5, 7, 5, -1],
        ]
    ],
    ["1ft 9-16/100in",
        [
            [0, 1, 0, 4],
            [4, 5, 4, 6],
            [6, 8, 6, 9],
            [9, 12, 9, -1],
        ]
    ],
    ["5/8",
        [
            [0, 1, 0, 2],
            [2, 3, 2, -1],
        ]
    ],
];



function test_getRange() {
    /* Tests getRange */
    let test = function (value, caret, start2, end2) {
        /* The test for getRange (separate for easier iteration) */
        let ele = newSetup();
        let [firstsep,lastsep] = getSepIndices(value, caret);
        let [start1, end1] = getRange(value, firstsep, lastsep);
        //console.log(`${[value.slice(0, caret), "|", value.slice(caret)].join('')}: (${start1},${end1}), (${start2},${end2})`);
        assertEqual(start1, start2);
        assertEqual(end1, end2);
    };

    for (let [value, args] of RANGINGTESTS) {
        // For each test string
        for (let [start2, end2, caretstart, caretend] of args) {
            /* For each sep-segment of the test string,
            for caretstart->caretend => results start2,end2 */
            if (caretend < 0) { caretend = value.length+1; };
            for (let caret = caretstart; caret < caretend; caret++) {
                /* Test for correct result at each caret position in segment */
                test(value, caret, start2, end2);
            };
        };
    };
};

function test_selectit() {
    /* Tests that selectit accurately selects the text (does not test event propogation) */
    let test = function (value, caret, start2, end2) {
        /* The test for selectit */
        let ele = newSetup();
        setValueCaret(ele, value, caret);
        // Calling selectit modifies the selectionrange on the element
        selectit(ele);
        let [start1, end1] = [ele.selectionStart, ele.selectionEnd];
        console.log(`${[value.slice(0, caret), "|", value.slice(caret)].join('')}: (${start1},${end1}), (${start2},${end2})`);
        assertEqual(start1, start2);
        assertEqual(end1, end2);
    };

    for (let [value, args] of RANGINGTESTS) {
        // For each test string
        for (let [start2, end2, caretstart, caretend] of args) {
            /* For each sep-segment of the test string,
            for caretstart->caretend => results start2,end2 */
            if (caretend < 0) { caretend = value.length+1; };
            for (let caret = caretstart; caret < caretend; caret++) {
                /* Test for correct result at each caret position in segment */
                test(value, caret, start2, end2);
            };
        };
    };
};

// Some Keycodes that should not work
var BADKEYCODES = [A, SPACE, TILDA, F1, HYPHEN] = [65, 32, 192, 112, 189];

KEYTESTS = [
    // value, caret, keycode, result, defaultFlag, resultvalue, start, end
    ["12ft 10in", 0, 48, null, "12ft 10in", 0, 2], // 48 == Number 0, null = properly propogated, no change to text because not actually sending keys
    ["12ft 10in", 5, 48, null, "12ft 10in", 5, 7], // only change from above is caret position: other results should be the same here
    ["0/1", 0, 48, null, "/1", 0, 0], // Entering a number when number is currently 0 should result in the zero being stripped
    ["12ft 10in", 0, 96, null, "12ft 10in", 0, 2], // Testing with Keypad Numbers
    ["12ft 10in", 1, DEL, false, "0ft 10in", 0, 1], // Testing Delete result: Replaces current segment with 0
    ["12ft 10in", 5, DEL, false, "12ft 0in", 5, 6], // As above, in a different segment
    ["12ft 10in", 2, BS, null, "12ft 10in", 0, 2], // Backspace shouldn't change anything here due to previously cited limitations
    ["1ft 10in", 1, BS, false, "0ft 10in", 0, 1], // In this case, Backspace should function as DEL
    ["12ft 10in", 0, ENT, null, "12ft 10in", 0, 2], // Enter shouldn't do anything
    // TODO Movement Keys
    // Escape Requires a different test
]

function test_handleit() {
    /* Tests handleit with various keycodes at various selections

       This is a relatively incomplete test as keypresses cannot actually
       be sent in-browser; in theory Selenium would be used to properly
       test this.
    */
    let test = function (value, caret, keycode, result,resultvalue,start,end) {
        /* The test for handleit */
        let ele = newSetup();
        setValueCaret(ele, value, caret);
        selectit(ele);
        console.log(`(${value}, ${caret}, ${keycode}, ${result}, ${resultvalue}, ${start}, ${end})`);

        // To test that preventDefault was called
        let defaultFlag = false;
        // Try to pass keycode
        res = handleit({ target: ele, which: keycode, preventDefault: function () { defaultFlag = true; }});
        // selectit would be called automatically on keyup
        selectit(ele);
        text = ele.value;
        [start1, end1] = [ele.selectionStart, ele.selectionEnd];
        //console.log(`(${res},${defaultFlag},${text},${start1},${end1})`);
        assertEqual(res, result, "EqualityError- Result");
        // If the result is false, preventDefault is always called
        assertEqual(defaultFlag, res === false);
        assertEqual(text, resultvalue, "EqualityError- Value");
        assertEqual(start1, start, "EqualityError- Start");
        assertEqual(end1, end, "EqualityError- End");
    };

    for (let ktest of KEYTESTS) {
        test.apply(null,ktest);
    };

    // Escape Key Test
    let ele = newSetup();
    setValueCaret(ele, "12ft 10in", 0);
    selectit(ele);
    // Try to pass keycode
    res = handleit({ target: ele, which: ESC, preventDefault: function () { }});
    assertEqual(res, null);
    assertFalse(document.activeElement === ele);

    // Bad Keys
    function badtest(keycode) {
        let ele = newSetup();
        setValueCaret(ele, "12ft 10in", 0);
        selectit(ele);
        // Try to pass keycode
        let defaultFlag = false;
        res = handleit({ target: ele, which: keycode, preventDefault: function () { defaultFlag = true; }});
        assertFalse(res);
        assertTrue(defaultFlag)
        // Again, we cannot check that the text has changed with this method (unfortunately)
    };

    for (let badkey of BADKEYCODES) {
        badtest(badkey);
    };
};


var TESTS = [test_runTest, test_repeatableSetup, test_getRange, test_selectit, test_handleit];