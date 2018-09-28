/*
  For listening:
    $(".toggle~input[type=checkbox]").change(function(){
        if(this.checked){
            // Do something
        };
    });
*/

function generateToggle(options, elements) {
    /* Dynamically Generates a toggle based on the given selector and with the given options.

        options is an object with any of the following keys:
            on: Text to accompany the widget when it is in the "on" position (checked).
                The default value is "On".
            off: Text to accompany the widget when it is in the "off" position (unchecked).
                The default value is "Off".
            callback: Sets the callback for the widgets, based on .change(). Default null (no callback).
            checked: Marks the toggle as checked

        These options are overwritten by the following on-element attributes (option : attribute) :
            on : data-on
            off : data-off
            callback : data-callback
            checked : data-checked

        elements should be a JQuery array of elements. If null, $(".toggle:not(:has(>input))")
        is used to find the elements. Only selected elements with class ".toggle" will be processed.
    */
    if (!elements || typeof elements == "undefined") {
        elements = $(".toggle:not(:has(input))");
    }
    else {
        elements = elements.filter(".toggle");
    };
    if (!elements) { return; };
    let opts = { on: "On", off: "Off", callback: null };
    if (typeof options != "undefined" || options != null) {
        for (let k in opts) {
            if (options.hasOwnProperty(k)) {
                opts[k] = options[k];
            };
        };
    };
    elements.each(function (index) {
        let eleopts = {};
        for (let attr of ['on', 'off', 'callback']) {
            if ($(this).attr(`data-${attr}`) == null) { eleopts[attr] = opts[attr]; } else { eleopts[attr] = $(this).attr(`data-${attr}`); };
        };
        // Convert Function strings to references
        if (typeof eleopts.callback == "string") {
            let callback = window[eleopts.callback];
            if (!callback) {
                let cb = eleopts.callback
                callback = function () { eval(cb) };
            };
            eleopts.callback = callback;
        };
        if (                                                                        // Checked if:
            (typeof $(this).attr('data-checked') != "undefined" || opts.checked)    // On-Element data-checked or defaults is truthy
            && $(this).attr('data-checked') != "false")                             // And On-Element data-checked is not "false"
        { eleopts.checked = "checked"; }
        else { eleopts.checked = ""; };                                                // Not Checked if: data-checked not set and default is false || data-checked == false
        $(this).append(`
<div>
    <input type="checkbox" ${eleopts.checked}/>
    <div></div>
    <span data-off="${eleopts.off}" data-on="${eleopts.on}"></span>
</div>
`);
        if (eleopts.callback) {
            $(this).find("input[type=checkbox]").change(eleopts.callback);
        };
    }
    );
};

function getToggle(element) {
    /* Returns a reference to the toggle's toplevel element (the first parent with the "toggle" class) */
    return $(element).parents(".toggle").first();
};

function getInput(element) {
    /* Returns the .toggle's input element */
    return $(element).find("input");
};

function getToggleValue(element) {
    /* Returns the data-on/data-off value of the Toggle based on its state.
     * 
     * Requires the top-level label element, rather than the auto-generated input element.
     * If the relevant property is undefined, returns the checked boolean.
     * */
    element = $(element);
    let input = element.find("input")[0];
    let attr;
    if (input.checked) {
        // Get data-on value
        attr = "data-on";
    } else {
        // Get data-off value
        attr = "data-off";
    }
    // If prop is not defined, return bool
    if (typeof element.attr(attr) === "null") { return input.checked; };
    return element.attr(attr);

};

function setToggle(element, value) {
    /* Sets the toggle state/checked property of a toggle element via it's toplevel parent */
    if (value !== true && value !== false) {
        throw new Error(`Invalid truth value for Toggle: ${value}`);
    };
    element.find("input").prop("checked", value);
};