// Text Separators
// TODO: When this module is generalized, make this customizable
var SEPS = [
    "ft ",
    "-",
    "/",
    "in"
];

// MODE: true = sep before, false = sep after
var MODE = false;

$(document).ready(function () {
    measureit_rebind();
});

function isundefined(ref) { return typeof ref === "undefined"; };

function measureit_rebind() {
    /* A function for manually rebinding measureit inputs (automatically fires on document load) */
    // console.log($(".measureit[type='text']"));
    let measures = $(".measureit[type='text']");
    measures.prop("spellcheck", false);
    measures.click(selectit_event).focusin(selectit_event).keydown(handleit).keyup(selectit_event)
    measures.each(function () {
        if (!$(this).val()) { $(this).val(`0ft 0-0/1in`) }
    });
};

var [BS,ENT,DEL,TAB,LEFT,UP,RIGHT,DOWN,ESC,ANDROID] = [8,13,46,9,37,38,39,40,27,229];
var VALIDKEYS = [
    BS, // Backspace
    ENT, // Enter
    DEL, // Delete
    TAB, // Tab
    LEFT, // Left Arrow
    UP, // Up Arrow
    RIGHT, // Right Arrow
    DOWN, // Down Arrow
    ESC, // Escape
];

// Flag for rewriting vs appending letters
var MODIFYING = 0;

function selectit_event(e) {
    /* selectit event wrapper */
    selectit(e.target);
};

function selectit(ele) {
    /* Sets Selection Range of the Widget */
    let [firstsep, lastsep] = getSepIndices(ele.value, ele.selectionStart)
    let [start, stop] = getRange(ele.value,firstsep,lastsep);
    ele.setSelectionRange(start, stop);
};

function getRange(text,firstsep,lastsep) {
    /* Interprets Sep indices */
    let start, end
    // firstsep -1 == start of string
    if (firstsep == -1) { start = 0; }
    // Otherwise, get index of sep, adjust to exclude sep
    else { start = text.indexOf(SEPS[firstsep]) + SEPS[firstsep].length; };

    // lastsep -1 == end of string
    if (lastsep == -1) {
        // With !MODE, go to end of string
        if (!MODE) { end = text.length; }
        // Otherwise, stop before last sep
        else { end = text.length - SEPS[SEPS.length - 1].length; };        
    }
    // Otherwise, get index of sep
    else { end = text.indexOf(SEPS[lastsep]); };

    return [start, end];
};

function moveSelect(ele, selectrange, seps, increment) {
    /* Moves the current selection left and right, depending if the increment is negative or positive (respectively) */
    //console.log(ele, selectrange, seps, increment);
    let text = ele.value;
    if (increment == 0) { throw "Invalid Increment"; };
    let [start, stop] = selectrange;
    let [prevsep, nextsep] = seps;

    let newcaret;

    // Can't move scenarios (Wrap Arround)
    if (increment > 0 && ( // Move Right (end of string error)
        (MODE && nextsep == -1) || // Sep comes before and no Sep after
        (!MODE && stop + SEPS[nextsep].length >= text.length) // Sep comes after, and sep is at end of string
    )) {
        // Move to start of string
        newcaret = 0;
    } else
        if(increment < 0 && ( // Move Left (start of string error)
            (!MODE && prevsep == -1) || // Sep comes After and no Sep before
            (MODE && start - SEPS[prevsep].length <= 0) // Sep comes Before and Sep starts at start of string
        )) {
            // Move to end of string
            newcaret = text.length;
        } else
            if (increment > 0) { // Move Right
            if (MODE) {
                // If Mode, we can just step the selectstart one right
                newcaret = stop + 1;
            } else {
                // Otherwise, we add the separator
                newcaret = stop + SEPS[nextsep].length;
                };
            } else { // Move Left
                if (MODE) {
                    // If Mode, we need to subtract the Sep Length
                    newcaret = start - SEPS[prevsep].length;
                } else {
                    // Otherwise, we just need to step one left
                    newcaret = start - 1;
                }
            };

    ele.setSelectionRange(newcaret, newcaret);
    // Set Selection
    selectit(ele);
};

function getSepIndices(text,pos,seps) {
    /* Returns the Start and End Indices of the Seps.
     
     Returns an array of [firstindex, secondindex].
     -1 indicates start and end of string for firstindex and secondindex, respectively.

    Examples (Pipe = Caret)-
        1|2ft 0in   => 0,2 (|12|: Found on first Sep)
        2ft 1|1in   => 4,6 (|11|: Found on fourth Sep)
        8ft |1in    => 4,5 (|1|: The index before the character belongs to it )
        3684        => 0,4 (|3684|: Can't find any seps, regardless of where caret is)
        4ft 3|58    => 4,5 (|358|: Couldn't find a SEP after first)
     */
    if (isNaN(pos) || pos < 0 || pos > text.length) {
        throw "Invalid Caret Position";
    };
    if (!MODE && pos == text.length && text.length > 0) {
        // This is to handle the fact that the index belongs to the character after it
        return getSepIndices(text, pos - 1, seps);
    };
    if (isundefined(seps)) { seps = SEPS; };
    // Get Seps that appear before the caret pos
    // If !MODE, caret can be inside sep
    let previous = seps.filter(sep => text.indexOf(sep)+(!MODE?sep.length:0) <= pos && text.indexOf(sep) > -1);
    // Get Seps that appear after the caret pos
    // If !MODE, caret cannot be inside sep
    let next = seps.filter(sep => text.indexOf(sep)+(!MODE?sep.length:0) > pos && text.indexOf(sep) > -1);
    if (previous.length == 0) {
        // If no previous, return -1
        previous = -1;
    } else {
        // Otherwise, return index of the last found sep
        previous = seps.indexOf(previous[previous.length - 1]);
    };
    // As above, but reverse with next
    if (next.length == 0) {
        // If no next, return -1
        next = -1;
    } else {
        // Otherwise, return index of the first found sep
        next = seps.indexOf(next[0]);
    };
    return [previous, next];
};

function segmentText(text, seps) {
    /* Splits the text per the provided separators (default SEPS), returning
       a nested array where the inner array contains the sep split upon and
       the accompanying segment of text.

       If MODE is true, the separator is accompanied by the text that appeared
       after it. Otherwise, it will be paired with the text preceeding it.
    */
    if (isundefined(seps)) { seps = SEPS; };
    let out = [];
    let segment;
    if (MODE) {
        // For mode, we'll have to look ahead
        // Before we start itertating, we'll parse off anything before the first sep
        // (We may establish protocol for handling it later, but it shouldn't be here)
        let trash
        [trash, text] = text.split(seps[0], 2);
        for (i = 0; i < seps.length; i++) {
            let sep = seps[i];
            // Before the last sep, we need to split up-to the next sep
            if (i < seps.length - 1) {
                let nextsep = seps[i + 1];
                // Split on the next separator
                [segment, text] = text.split(nextsep, 2);
            } else {
                // On last sep, the rest is the segment
                segment = text;
            };
            out.push([sep, segment]);
        };
    } else {
        // For not mode, we can split on sep and then just add it
        for (sep of seps) {
            if (text.indexOf(sep) > -1) {
                [segment, text] = text.split(sep, 2);
                // Splitting completely removes the characters split on
                out.push([sep,segment]);
            };
        };
    };
    return out;
};

function replaceselection(text,start, end, value) {
    /* Return the text with the given value between start and end */
    return text.substring(0, start) + value + text.substring(end);
};

function getSelectedValue(text, start, end) {
    return text.slice(start, end);
};

function myNaN(keycode) {
    return keycode < 48 || keycode > 105 || (keycode > 57 && keycode < 96);
};

function to_number(keycode) {
    /* Returns the Number Key of the keycode

       If the keycode is not a Number Key, return false
    */
    // Keypad is at 96 - 105
    if (keycode >= 96) {
        // Keypad numbers are 48 above Keyboard Numbers
        keycode -= 48
    };
    /* Keyboard numbers are between 48 and 57, in order,
       so subtracting 48 gives the actual number */
    let number = keycode - 48;
    // Numbers should be accurate now
    if (number >= 0 && number <= 9) {
        return number;
    };
    // Ergo, not a number
    return false;
}

function handleit(e) {
    let keycode = e.which;
    let number = to_number(keycode);
    if (number === false && VALIDKEYS.indexOf(keycode) < 0) {
        // Anything invalid, stop it from being entered

        // Don't prevent keystrokes for Ctrl+R
        if (e.ctrlKey && keycode == 82) { return; };
        e.preventDefault();
        return false;
    } else
        if (keycode == ENT) {
            // We just pass Enter On
            return 
    };
    let ele = e.target;
    // Last Sep is the section we're in
    let text = ele.value;
    let [firstsep, lastsep] = getSepIndices(text, ele.selectionStart);
    let [start, end] = getRange(text,firstsep, lastsep);
    let movement;
    if (keycode == ESC) {
        // Lose Focus
        ele.blur();
    } else
        if ([RIGHT, TAB, LEFT].indexOf(keycode) > -1) {
            /* Movement Keys */
            let increment;
            if ([RIGHT, TAB].indexOf(keycode) > -1) {
                // Check if shift key is down
                console.log(e.shiftKey);
                if (e.shiftKey) {
                    // Focus next instead
                    let nextele;
                    ele = $(ele);
                    i = 0;
                    while (!nextele && ele[0] != window, i<10) {
                        console.log(nextele, ele[0], window, ele[0] != window);
                        console.log(ele.next("input"), Boolean(ele.next("input")), ele.parent(), ele.parent()[0] != window);
                        nextele = ele.next("input")
                        if (nextele.length == 0) { nextele = false; };
                        if (nextele) {
                            nextele.focus()
                        }
                        ele = ele.parent();
                        i++;
                    }
                    
                    return false;
                };
                // Traverse Right
                increment = +1;
            } else {
                // Traverse Left
                increment = -1;
            };
            // Move
            moveSelect(ele, [start, end], [firstsep,lastsep], increment);
            // Prevent propogation
            e.preventDefault();
            return false;
        } else
        if (keycode == DEL || (keycode == BS && end - start == 1)) {
            /* For both Delete and when Backspacing the last Character
               we replace the text with "0" instead */
            text = replaceselection(text, start, end, "0");
            ele.value = text;
            // Reset caret to start before returning (so selectit is accurate)
            ele.setSelectionRange(start, start)
            // Prevent propogation
            e.preventDefault();
            return false;
        } else
            if (keycode == UP || keycode == DOWN){
                /* Incrementing/Decrementing Value */
                // Get Value as int
                let value = Number(getSelectedValue(text, start, end));
                // Update value
                if (keycode == UP) { value++; }
                else { value--; };
                if (value <= 0) { value = 0; };
                // Set value
                text = replaceselection(text, start, end, value);
                ele.value = text;
                // Reset caret to start before returning (so selectit is accurate)
                ele.setSelectionRange(start, start)
                // Prevent propogation
                e.preventDefault();
                return false;
            } else {
                /* The rest are numbers to be entered */
                if (Number(getSelectedValue(text, start, end)) == 0) {
                    // If value is currently 0, remove it so that we don't end up with leading 0's
                    text = replaceselection(text, start, end, "");
                    ele.value = text;
                    // Set cursor at start
                    ele.setSelectionRange(start, start);
                }
                else {
                    // Otherwise, just set cursor at end
                    ele.setSelectionRange(end, end);
                };
                    // Just let the keys do the rest
            };
};