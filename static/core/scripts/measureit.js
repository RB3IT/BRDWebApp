class MeasureIt {
    constructor(options) {
        this.options = { inputs: [], regex: /(?<feet>\d*)ft (?<inches>\d*)-(?<numerator>\d*)\/(?<denominator>\d*)in/ };
        if (options !== undefined) {
            if (options.regex !== undefined) this.options.regex = options.regex;
            if (options.inputs !== undefined) { this.inputs = Array.prototype.slice.call(options.inputs); }
        }
        if (this.inputs === undefined) this.inputs = Array.prototype.slice.call(document.querySelectorAll("input.measureit"));
        this.regex = new BetteRegExp(this.options.regex);
        this.handlers = [];
        this.handlers.push(document.addEventListener("keydown", this.delegateEvent.bind(this)));
        this.handlers.push(document.addEventListener("keyup", this.delegateEvent.bind(this)));
        this.handlers.push(document.addEventListener("focusin", this.delegateEvent.bind(this)));
        this.handlers.push(document.addEventListener("mouseup", this.delegateEvent.bind(this)));

        this.rebind();
    }
    rebind() {
        /* Checks all inputs in this.inputs to ensure that they adhere to this.regex */
        let values = [];
        for (let replacement of this.regex.tokens.filter(token => token.token === "Builtin Class" || token.token === "Character Class")) {
            values.push(0);
        }
        let value = this.regex.constructString.apply(this.regex, [0, 0, 0, 1]);
        for (let input of this.inputs) {
            if (!this.regex.test(input.value)) this.setValue(input, [0, 0, 0, 1]);
            // While we're at it, disable spellchecking
            input.setAttribute("spellcheck", false);
        }
    }
    rebind_all() {
        /* Adds inputs to this.inputs and then calls this.rebind.
         
           inputs should be <input> elements with the "measureit" class.
           If no inputs are provided, the document will be queried and all "input.measureit" elements will be added.
         */
        if (arguments.length) {
            for (let input of arguments) {
                if (!input.tagname === "input" || !input.classList.contains("measureit")) throw new Error('Inputs for MeasureIt should be <input> elements and should have the "measureit" class');
            }
            this.inputs = arguments.slice();
        }
        else { this.inputs = Array.prototype.slice.call(document.querySelectorAll("input.measureit")) }
        this.rebind();
    }

    checkEvent(event) {
        return this.inputs.indexOf(event.target) >= 0;
    }
    delegateEvent(event) {
        /* Overarching event delegation for MeasureIt */
        if (!this.checkEvent(event)) return;
        if (event.type === "keydown") return this._handlekeydown(event);
        if (event.type === "keyup") return this._handlekeyup(event);
        if (event.type === "focusin" || event.type === "mouseup") return this._handlefocus(event);
    }

    _handlekeydown(event) {
        /* Event Handler for Keydown events */
        // Alphabeticals are invalid
        if (MeasureIt.ALPHABET.test(event.key)) {
            event.preventDefault();
            return false;
        }
        // Selection fix
        /* If a selection ends outside the box, mouseup will not be captured because the mouseup.target
           is not the input. Therefore, we need to makes sure that we have a proper selection before we
           do anything else */
        event.target.setSelectionRange(event.target.selectionStart, event.target.selectionStart);
        this.setSelectionToNearest(event.target);

        let val = this.parseValue(event.target);
        let key = event.key.toLowerCase();
        if (MeasureIt.NOBUBBLE.has(key)) {
            // These Keys do not continue propogating
            try {
                if (MeasureIt.MOVEMENT.has(key)) {
                    if (key === "arrowup" || key === "end") {
                        this.setSelectByGroup(event.target, val.groups[val.length - 1]);
                    }
                    else if (key === "arrowdown" || key === "home") {
                        this.setSelectByGroup(event.target, val.groups[1]);
                    }
                    else {
                        let selectgroup = this.getNearestGroup(event.target);
                        let newindex = key === "arrowleft" ? selectgroup.name - 1 : selectgroup.name + 1;
                        // bounding
                        newindex = Math.min(Math.max(1, newindex), val.length - 1);
                        this.setSelectByGroup(event.target, val.groups[newindex]);
                    }
                }
            }
            catch (err) { throw err; }
            finally { event.preventDefault(); return false; }
        }
        // These keys propogate

        let [start, end] = [event.target.selectionStart, event.target.selectionEnd];
        // For any Numeric keys, check for 0, otherwise don't overwrite it
        if (MeasureIt.NUMERIC.test(event.key)) {
            let value = event.target.value.substring(start, end);
            // Only overwite if value is 0
            if (parseInt(value) !== 0) event.target.setSelectionRange(end, end);
            return;
        }

        // Don't overwrite on backspace
        if (key === "backspace") {
            event.target.setSelectionRange(end, end);
            return;
        }

    }

    _handlekeyup(event) {
        if (!MeasureIt.KEYUP.test(event.key)) return;
        let key = event.key.toLowerCase();
        let ele = event.target;

        // Escape key blurs
        if (key === "escape") {
            ele.blur();
            return;
        }

        // After a key is pressed, the index moves to the end, which is after the group
        // This means that we need to back up to capture the current group
        // Need to stop the lower bound
        ele.setSelectionRange(Math.max(0, ele.selectionStart - 1), Math.max(0, ele.selectionStart - 1));

        let group = this.getNearestGroup(ele);

        // No value ("") should be replaced by "0"
        if (!group.value) {
            let group = this.getNearestGroup(ele);
            let value = ele.value;
            value = value.substring(0, group.index) + 0 + value.substring(group.index);
            ele.value = value;
            ele.setSelectionRange(group.index, group.index + 1);
            return;
        }
        // Validate Measurement
        // Change flag- if changes were made, recreate string   
        let [feet, inc, num, den] = this.getValue(event.target);
        let [feetstr, incstr, numstr, denstr] = [feet, inc, num, den].map(String);

        while (inc >= 12) {
            incstr = incstr.substring(1) ? incstr.substring(1) : 0;
            inc = parseInt(incstr, 10);
        }

        if (den <= 0) [denstr, den] = [1, 1];

        while (num > den) {
            numstr = numstr.substring(1) ? numstr.substring(1) : 0;
            num = parseInt(numstr, 10);
        }
        if (num === den) [numstr, num] = [0, 0];

        this.setValue(ele, [feet, inc, num, den]);
        let result = this.parseValue(event.target);
        group = result.groups[group.name];
        this.setSelectByGroup(ele, group);
    }

    _handlefocus(event) {
        /* Event Handler for Focus Events */
        this.setSelectionToNearest(event.target);
        event.preventDefault(); return false;
    }

    setSelectionToNearest(ele) {
        this.setSelectByGroup(ele, this.getNearestGroup(ele));
    }

    getNearestGroup(ele) {
        let result = this.regex.exec(ele.value).groupAt(ele.selectionStart, "fuzzy");
        return result;
    }

    setSelectByGroup(ele, group) {
        ele.setSelectionRange(group.index, group.index + group.value.length);
    }

    parseValue(ele) {
        return this.regex.exec(ele.value);
    }

    getValue(ele) {
        let result = this.parseValue(ele);
        return [result.groups.feet.value,
        result.groups.inches.value,
        result.groups.numerator.value,
        result.groups.denominator.value].map(size => parseInt(size, 10));
    }

    setValue(ele, values) {
        let value = this.regex.constructString(...values);
        ele.value = value;
    }

    static KEYUP = /[0-9]|backspace|delete|escape/i;
    static KEYDOWN = /arrow.+|home|end/i;
    static NUMERIC = /[0-9]/i;
    static ALPHABET = /^[a-z]$/i;
    static MOVEMENT = new Set(["arrowup", "arrowright", "arrowdown", "arrowleft", "home", "end"]);
    static NOBUBBLE = new Set([...MeasureIt.MOVEMENT]);
}