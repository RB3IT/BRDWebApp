class BetteRegExp extends RegExp {
    constructor() {
        super(...arguments);
        this.tokens = _parseSource(this.source);
        this.format = _parseFormat(this.tokens);
    }

    constructString() {
        /* Given an Array of Values, construct and return a String that conforms with this BRE's regex, substituting the provided values for Regex Classes */
        /* TODO: This function is currently unsatisfactory:
        
            The working idea is to make this a non-class, recursive function in the following manner:
                arguments for this function should have each group as an array, with subgroups nested in args
            iterate over tokens until group
            slice off group.tokens and shift() arguments: apply (group.tokens, ...argument.shift()) recursively
            issue looks to be quntified groups.
            not sure if issue: a(\d(\d)?){2} => ...Arguments([1[]][2[]]); ...Arguments([1[2]][2[3]]); ...Arguments([1[]][2[3]])
        */
        let args = Array.prototype.slice.call(arguments);
        let output = "";
        let tokens = this.tokens.slice();


        function getQuantifier() {
            if (tokens.length && tokens[0].token === "Quantifier") return tokens.shift();
        }

        while (tokens.length) {
            let token = tokens.shift();
            switch (token.token) {
                case "Open Group":
                case "Group Type":
                case "Named Group":
                    break;
                case "Close Group":
                    getQuantifier();
                    break;
                case "Builtin Class":
                case "Character Class":
                    getQuantifier();
                    output += args.shift();
                    break;
                case "String Literal":
                    output += token.value.replace(/(?<!\\)\\/, "");
                    getQuantifier();
                    break;
                default:
                    throw new Error("Unexpected Token extracted in constructString");
            }
        }
        if (args.length) throw new Error("Too many arguments supplied to constructString.");
        if (!this.test(output)) throw new Error(`Invalid Regex: Constructed String does not match Regex: ${output}`);
        return output;
    }

    * groupsGen() {
        /* Generator Version of BRE.groups */
        yield* _getGroups(this.format);
    }

    get groups() {
        /* Returns a flattened list of groups, as they would be counted (not accounting for optional groups) */
        let output = [];
        for (let group of this.groupsGen()) output.push(group);
        return output;
    }

    exec(string, reset) {
        /* Functions as RegExp.exec, except as follows:
           
           Accepts a second positional argument: if truthy, will reset the BetteRegExp's lastIndex value to 0.
           Returns an BREResultArray object, which is an enhanced version of the regularly returned array (no properties of the original Array are lost; at most they are extended)
         */
        if (reset === undefined) reset = false;
        if (reset) this.lastIndex = 0;
        let result = super.exec(string);
        if (result === null) return null;
        return new BREResultArray(result, this);
    }

}

function* _getGroups(group) {
    /* Recursive Generator Function to return Groups and nested Groups from an Array */
    for (let element of group) {
        if (element instanceof BREGroup) {
            yield element;
            yield* element.groupsGen();
        }
    }
}

class BREToken {
    /* A basic Regex Token  class */
    constructor(token, value, quantifier) {
        this.token = token;
        this.value = value;
        this.quantifier = quantifier;
    }

    get index() {
        /* The Token's Type as a String */
        return REGPARSER_LOOKUP[this.token];
    }

    toString() {
        /* Returns a string representation of the BREToken */
        if (this.quantifier !== undefined) return this.value + this.quantifier.value;
        return this.value;
    }
}

class BREGroup {
    /* A basic Regex Group class */
    constructor(group, name, quantifier) {
        this.group = group;
        this.name = name;
        this.quantifier = quantifier;
    }

    * groupsGen() {
        /* Like BRE.groupsGen, a Generator version of BREGroup.groups */
        yield* _getGroups(this.group);
    }

    get groups() {
        /* Like BRE.groups, returns a flattened list of groups, as they would be counted (not accounting for optional groups) */
        let output = [];
        for (let group of this.groupsGen()) output.push(group);
        return output;
    }

    toString() {
        /* Converts the Group to a string */
        let output = [];
        this.group.forEach(token => output.push(token.toString()));
        return output.join("");
    }
}

class BREResultArray extends Array {
/* An Extension of the Array returned by normal RegExp */
    static FUZZYINDICES = ["exact", "fuzzy","fuzzy+","fuzzy-"];

    constructor(original, parent) {
        super(...original);
        let groups = original.groups === undefined ? {} : original.groups;
        this.groups = groups;
        this.index = original.index;
        this.input = original.input;
        this.parent = parent;
        for (let [group, value] of Object.entries(groups)) {
            this.groups[group] = { value: value, name:group };
        }
        for (let i = 1; i < original.length; i++) {
            this.groups[i] = { value: this[i], name:i };
        }
        let i = 1;
        let index = 0;
        let result = this;
        let input = this.input;
        let reg, match;
        function iterparse(arr) {
            for (let token of arr) {
                reg = RegExp("^" + token.toString());
                match = reg.exec(input)[0];
                if (token instanceof BREGroup) {
                    result.groups[i].index = index;
                    if (token.name) result.groups[token.name].index = index;
                    i++;
                    iterparse(token.group);
                }
                else {
                    input = input.replace(reg, "");
                    index += match.length;
                }
            }
        }
        iterparse(parent.format);
    }

    groupAt(index, mode) {
        /* Returns the BREGroup object at the given index. The second argument is the mode to determine which group to return (default is "exact").
            
           Modes:
           "exact": Return the group that contains the given index.
           "fuzzy": If no exact group, return the group with a start or stop index closest to the provided index.
           "fuzzy+": If no exact group, return the closest group with start index higher than the provided index.
           "fuzzy-": If no exact group, return the closest group with start index lower than the provided index.
           
           In all modes, the inner-most group is used, and if no group meets the qualifications, null is returned.
        */
        if (mode === undefined) mode = "exact";
        if (BREResultArray.FUZZYINDICES.indexOf(mode) === -1) throw new Error("Invalid groupAt mode");
        // Can't find groups if no groups exist
        if (!(this.length - 1)) return null;

        let groups = [];
        let group;
        for (let i = 1; i < this.length; i++) {
            group = this.groups[i];
            // Create list of all groups and relevant statistics
            // [Group Number, Start Offset, End Offset, Absolute Nearest Offset]
            groups.push([i,
                group.index - index, group.index + group.value.length-1 - index,
                Math.min(Math.abs(group.index - index), Math.abs(group.index + group.value.length-1 - index))
            ]);
        }

        let result = (function () {
            // [1]==> group start index is less than index
            // [2]==> group end index is greater than index
            let exact = groups.filter(group => group[1] <= 0 && group[2] >= 0);
            // Always return the exact match if available
            // Because of how groups are counted, the inner-most group will be the highest numbered group (i)
            if (exact.length) return exact[exact.length - 1];

            // Iterate/Reduce over groups, keeping the group with the smallest Absolute Nearest Offest. Return 
            if (mode === "fuzzy") return groups.reduce((prevmin, current) => prevmin[3] < current[3] ? prevmin : current);

            if (mode === "fuzzy+") {
                groups = groups.filter(group => group[1] >= 0);
                if (groups.length) {
                    // Because we always return innermost group, we need to make sure the first element is not nested
                    // Nested groups [i.e.- ((group2) group1)] will  resolve:
                    //  group1 is prevmin by default
                    //  group1 is not < group2 (they are equal) therefore group2 is new prevmin
                    return groups.reduce((prevmin, current) => prevmin[1] < current[1] ? prevmin : current);
                }
            }

            if (mode === "fuzzy-") {
                groups = groups.filter(group => group[1] <= 0);
                // Unlike fuzzy+, the last element will always be the innermost due to Group Numbering
                if (groups.length) return groups[groups.length-1]
            }

            // Default if no conditions met is null.
            return null;
        })();

        // Returned truthy result is an array of stats; first element is the Group Number
        if (result) return this.groups[result[0]];
        // Non-truthy results are null anyway
        return null;
    }

    slice() {
        /* Returns an Array matching this BREResultArray's indicies, given the provided start and stop arguments (functions per Array.slice). Note that this is a new Array object, and not a new BREResultArray; ergo, no other properties are inherited
    
    	DEV NOTE: This function could not be inheritted; calling this.slice() returns the length of the BRERA instead of the normal slice.
        */
        return Array.prototype.slice(this, ...arguments);
    }
}

let REGPARSER_LOOKUP = {
    1: "Capture",
    2: "Close Group",
    3: "Open Group",
    4: "Character Class",
    5: "Builtin Class",
    6: "Named Group",
    7: "Group Type",
    8: "Quantifier",
    9: "Quantified Quantifier",
    10: "String Literal"
};

for (let i in REGPARSER_LOOKUP) { REGPARSER_LOOKUP[REGPARSER_LOOKUP[i]] = i; }

let REGPARSER = /^((\))|(\()|(\[\^?.*\])|(\\[wdsb])|(\?<[_a-zA-Z]\S*?>)|(\?[:=!<](?:(?<=<)[=!])?)|([+*?](?:(?<!\?)\?)?)|(\{\d+(?:,\d+)?\})|(.))/;

let NAMEPARSER = /^\?<(.+)>$/;

function _parseSource(source) {
    let token, output;
    output = [];
    let lasttoken = null;
    while (source) {
        [source, token] = _tokenize(source);
        // Group String Literals
        if (token.token === "String Literal") {
            if (lasttoken === null) {
                lasttoken = token;
            } else {
                lasttoken.value += token.value;
            }
        } else {
            // Clear out lasttoken (String Literal) if it exists before continuing
            if (lasttoken !== null) {
                output.push(lasttoken);
                lasttoken = null;
            }
            output.push(token);
        }
    }
    // If the last token was a String Literal, it needs to be pushed to output manually
    if (lasttoken !== null) output.push(lasttoken);
    return output;
}

function _tokenize(str) {
    let result = REGPARSER.exec(str);
    let group, match, token;

    result.slice(2, REGPARSER_LOOKUP.length).forEach(function (res, i) {
        if (res) {
            group = i + 2;
            match = res;
            token = REGPARSER_LOOKUP[group];
        }
    });

    return [str.slice(match.length, str.length + 1), new BREToken(token, match)];
}

function _parseFormat(tokens) {
    /* Takes an array of tokens and returns an array with Group Tokens converted into Group objects */
    let output = [];
    let group, token;
    tokens = tokens.slice();
    while (tokens.length) {
        token = tokens.shift();
        // Use recursive function (in case of nesting) for Groups
        if (token.token === "Open Group") {
            [tokens, group] = _parseGroup(tokens);
            output.push(group);
        }
        else if (token.token.startsWith("Quantifi")) {
            output[output.length - 1].quantifier = token;
        }
        else {
            output.push(token);
        }
    }
    return output;
}

function _parseGroup(tokens) {
    /* Locate the end of the group (recursing if necessary) */
    let token;
    let group = [];
    let groupname;
    // Group Name should only appear at the very beginning
    /* Since this is supposed to be invoked post-regex creation,
              we shouldn't need to verify that the first token is the
        only Named Group token */
    if (tokens[0].token === "Named Group") {
        groupname = NAMEPARSER.exec(tokens.shift().value)[1];
    }
    while (tokens.length) {
        token = tokens.shift();
        // On New (sub) Group, recurse
        if (token.token === "Open Group") {
            let subgroup;
            [tokens, subgroup] = _parseGroup(tokens);
            group.push(subgroup);
        }
        // Close Group ends our group
        else if (token.token === "Close Group") {
            return [tokens, new BREGroup(group, groupname)];
        }
        else if (token.token.startsWith("Quantifi")) {
            group[group.length - 1].quantifier = token;
        }
        // Otherwise, add token to current group
        else {
            group.push(token);
        }
    }
    throw new Error("Reached end of Tokens without encountering Group Closure");
}
