// Text Separators
// TODO: When this module is generalized, make this customizable
var SEPS = [
    "ft ",
    "-",
    "/",
    "in"
]

$(document).ready(function () {
    measureit_rebind();
});

function measureit_rebind() {
    /* A function for manually rebinding measureit inputs (automatically fires on document load) */
    // console.log($(".measureit[type='text']"));
    $(".measureit[type='text']").click(selectit).keydown(handleit).val(`0ft 0in`);
};

var [BS,ENT,DEL,TAB,LEFT,UP,RIGHT,DOWN] = [8,13,46,9,37,38,39,40];
var VALIDKEYS = [
    BS, // Backspace
    ENT, // Enter
    DEL, // Delete
    TAB, // Tab
    LEFT, // Left Arrow
    UP, // Up Arrow
    RIGHT, // Right Arrow
    DOWN, // Down Arrow
];

// Flag for rewriting vs appending letters
var MODIFYING = 0;

function selectit(e) {
    /* Sets Selection Range of the Widget */
    let [firstsep, lastsep] = getSepIndices(e.target.value, e.target.selectionStart)
    let [start, stop] = getRange(firstsep,lastsep);
    e.target.setSelectionRange(start, stop);
};

function getRange(firstsep,lastsep) {
    /* Interprets Sep indices */
    let start, end
    // firstsep -1 == start of string
    if (firstsep == -1) { start = 0; }
    // Otherwise, get index of sep, adjust to exclude sep
    else { start = text.indexOf(SEPS[firstsep]) + SEPS[firstsep].length;};

    // lastsep -1 == end of string
    if (lastsep == -1) { end = text.length; }
    // Otherwise, get index of sep
    else { end = text.indexOf(SEPS[lastsep]);};

    return [start, end];
};

function stepSep(index, increment, seps) {
    /* Returns the SEP index relative to the provided index per the increment */
    // Use SEPS by default
    if (typeof seps === undefined) { seps = SEPS; };
    index = (index + increment) % seps.length;
    // For negative indices/movement, need to roll backwards from max index
    if (index < 0) { index = seps.length + index; };
    return index;
};

function moveSelect(ele, index, increment) {
    /* Moves the current selection a number of increments based on available seps in the given element */
    let available = [];
    let text = ele.value;
    // Get available indices to move by
    for (let index of SEPS) {
        if (text.indexOf(SEPS[index]) >= 0) { available.push(index); };
    };
    // If we don't have any seps, we can't move anywhere
    if (available.length < 1) { return; };
    let newindex;
};

function getSepIndices(text,pos) {
    /* Returns the Start and End Indices of the Seps.
     
     Returns an array of [firstindex, secondindex].
     -1 indicates start and end of string for firstindex and secondindex, respectively.

    Examples (Pipe = Caret)-
        1|2ft 0in   => 0,2 (|12|: Found on first Sep)
        2ft 1|1in   => 4,6 (|11|: Found on fourth Sep)
        3684        => 0,4 (|3684|: Couldn't find any seps)
        4ft 3|58    => 4,5 (|358|: Couldn't find a SEP after first)
     */
    let length = text.length;
    // Iterate through Separators
    // Set variables up here so that we can conserve them between loops
    let start = 0; // Substring Start Index (0 by default, last found sep when available)
    let end = 0; // Substring End Index (Location of current Sep)
    let firstsep = -1; // Sep before Caret
    let lastsep = -1; // Sep after Caret
    let sep = null;
    //console.log(`Pos is ${pos}`);
    for (let lastsep = 0; lastsep < SEPS.length; lastsep++) {
        //console.log("start:", start);
        let sep = SEPS[lastsep];
        end = text.indexOf(sep);
        //console.log(`New End is ${end}`);
        // If Caret is between start and end (including separator, but excluding the index directly after the sep), return range
        if (start < end && start <= pos && pos <= end + sep.length - 1) {
            //console.log(`Successful Endpoint: ${start} < ${end}; ${start} <= ${pos}; ${pos} <= ${end+sep.length-1}`)
            //console.log("returning end:", end);
            return [firstsep, lastsep];
        } else {
            // If sep was found but caret is not between start and end
            if (end >= 0) {
                /* Set new start as end + length of sep
                (so we dont match against the sep on the next iteration) */
                start = end + sep.length;
                firstsep = lastsep;
            } else {
                //console.log(`Could not find ${sep} in ${text}`);
            };
        };
    };
    //console.log("returning last confirmed sep to end of string");
    // Return -1 for end of string
    return [firstsep,-1];
}

function handleit(e) {
    let key = String.fromCharCode(e.keyCode);
    let keycode = e.which;
    if (isNaN(key) && VALIDKEYS.indexOf(keycode) < 0) {
        // Anything invalid, stop it from being entered
        e.preventDefault();
        return false;
    } else
        if (keycode == ENT) {
            // We just pass Enter On
            return 
    };
    let ele = e.target;
    // Last Sep is the section we're in
    let [firstsep, lastsep] = getSepIndices(ele.value, ele.selectionStart);
    let [start, end] = getRange(firstsep, lastsep);
    let movement;
    if ([UP, RIGHT, TAB].indexOf(keycode) > -1) {
        // Traverse Right
        moveSelect(ele, lastsep, +1);
        // Prevent propogation
        e.preventDefault();
        return false;
    } else
        if ([DOWN, LEFT].indexOf(keycode) > -1) {
            // Traverse Left
            moveSelect(ele, lastsep, -1);
            // Prevent propogation
            e.preventDefault();
            return false;
        } else
            if (keycode == DEL) {
                // Clear and reset insert point

            } else {
                // For the rest, we should unselect and place cursor at end
                ele.setSelectionRange(end, end);

            };
};