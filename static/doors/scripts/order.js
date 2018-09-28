var ENDLOCKS = {
    all: ["FLSTP", "FLCST", "FLCWD", "CRCST", "CRCWD","MNCST"],
    BRD: ["", "FLSTP", "FLCST", "FLCWD"],
    NY: ["", "FLSTP", "FLCST", "FLCWD"],
    CRN: ["", "CRCST", "CRCWD"],
    MCR: ["", "MNCST"],
    defaults: {
        BRD: "FLSTP",
        NY: "FLCST",
        CRN: "CRCST",
        MCR: "MNCST"
    },
    "": "None",
    "FLSTP": "Flat Stamped",
    "FLCST": "Flat Cast",
    "FLCWD": "Flat Cast Windlocks",
    "CRCST": "Curved Cast",
    "CRCWD": "Curved Cast Windlocks",
    "MNCST":"Mini Cast"
};

var DOORCOMPONENT = `
                        <div class="section component" data-type="door">
                            <h3>Door<i class="material-icons cancel-button" /></h3>
                            <div data-type="doorinfo">
                                <div class="floatleft" style="align-items:center;">
                                    <label>Door Name<input type="text" name="name" /></label>
                                    <label>Clear Height<input name="clearheight"type="text" class="measureit" /></label>
                                    <label>Clear Width<input name="clearwidth"type="text" class="measureit" /></label>
                                    <div><span style="font-weight:bold;margin-right:-5px;">Hand</span><label class="toggle" data-value="hand" data-on="Right" data-off="Left" data-checked style="vertical-align:middle;"></label></div>
                                    <div><span style="font-weight:bold;margin-right:-5px;">Full Seal</span><label class="toggle" data-value="fullseal" data-on="Seal" data-off="" data-callback="toggleSeal" style="vertical-align:middle;"></label></div>
                                </div>
                            </div>
                            <div style="text-align:center;">
                                <div class="floatleft">
                                    <button type="button" class="beveled itemlabel noglow" style="background-color:rgb(127,255,148)" onclick="addComponent(this,'complete')">Complete Door</button>
                                    <button type="button" class="beveled itemlabel noglow" style="background-color:rgb(127,234,255)" onclick="addComponent(this,'pipe')">Pipe</button>
                                    <button type="button" class="beveled itemlabel noglow" style="background-color:rgb(255,127,234)" onclick="addComponent(this,'tracks')">Tracks</button>
                                    <button type="button" class="beveled itemlabel noglow" style="background-color:rgb(255,212,127)" onclick="addComponent(this,'hood')">Hood</button>
                                    <button type="button" class="beveled itemlabel noglow" style="background-color:rgb(255,148,127)" onclick="addComponent(this,'slats')">Slats</button>
                                    <button type="button" class="beveled itemlabel noglow" style="background-color:rgb(127,170,255)" onclick="addComponent(this,'bottombar')">Bottom Bar</button>
                                    <button type="button" class="beveled itemlabel noglow" style="background-color:rgb(148,127,255)" onclick="addComponent(this,'accessories')">Accessories</button>
                                </div>
                            </div>
                            <div data-type="components"></div>
                        </div>`

var PIPECOMPONENT = `<div class="component" data-type="pipe">
                        <h4>Pipe<i class="material-icons cancel-button" /></h4>
                        <label class="toggle" data-value="autocalculation" data-on="Auto" data-off="Manual" data-callback='showDataType(this,"pipeinfo");' data-checked>Pipe Information</label>
                        <div class="toggleable boxed" data-type="pipeinfo">
                            <button type="button" onclick="addSpring(this);" style="display:block;">Add Spring</button>
                            <div class="floatleft vcenter">
                                <label>Pipe Diameter
                                    <select data-value="pipediameter">
                                        <option value="4">4 Inch</option>
                                        <option value="6">6 Inch</option>
                                        <option value="8">8 Inch</option>
                                    </select>
                                </label>
                                <label>Pipe Length<input type="text" class="measureit" data-value="pipelength" /></label>
                                <label>Shaft Size
                                    <select data-value="shaftdiameter">
                                        <option value="1">1 Inch</option>
                                        <option value="1.25" selected>1 1/4 Inch</option>
                                        <option value="1.5">1 1/2 Inch</option>
                                        <option value="1.75">1 3/4 Inch</option>
                                    </select>
                                </label>
                                <label>Shaft Length<input type="text" class="measureit" data-value="shaftlength" /></label>
                            </div>
                            <div class="springdiv"></div>
                        </div>
                    </div>`;

var SPRING = `  
            <div>
                <span style="font-weight:bold;font-size:1em;">Spring</span><i class="material-icons" style="font-size:.75em;color:red;cursor:pointer;">cancel</i>
                <div class="floatleft vcenter" data-type="spring" style="border:solid thin;">
                    <label>Type
                        <select data-value="springtype">
                            <option value="outer" selected>Outer</option>
                            <option value="inner">Inner</option>
                        </select>
                    </label>
                    <label>Spring OD
                        <input type="text" list="springods" data-value="springod" min="0" />
                    </label>
                    <label>Wire Diameter
                        <input type="text" list="springwd" data-value="springdiameter" min="0" />
                    </label>
                    <label>Stretch<input type="number" size="6" data-value="springstretch" min="0" /></label>
                </div>
            </div>`;

var TRACKSCOMPONENT = `
<div class="component" data-type="tracks">
    <h4>Tracks<i class="cancel-button material-icons"></i></h4>
    <label class="toggle" data-value="autobrackets" data-on="Auto" data-off="Manual" data-callback="showDataType(this,'bracketinfo')" data-checked>Brackets</label>
    <div class="toggleable boxed" data-type="bracketinfo">
        <label>Bracket Size
            <select data-value="bracketsize">
                <option value="14">14 Inch</option>
                <option value="16">16 Inch</option>
                <option value="18" selected>18 Inch</option>
            </select>
        </label>
        <label class="toggle" data-value="hand" data-on="Right" data-off="Left" data-callback="" data-checked data-value="hand">Drive Side</label>
    </div>
    <div class="floatleft" style="text-align:center;">
        <label class="toggle" data-value="weatherstripping" data-on="Include" data-off="None" data-callback="toggleFullSeal">Weatherstripping</label>
        <label>Wall Angle Height<label class="toggle" data-value="autowallangleheight" data-on="Auto" data-off="Manual" data-callback="toggleMeasurement" data-checked ></label><input class="measureit" type="text" data-value="wallangleheight" readonly/></label>
        <label>Guide Height<label class="toggle" data-value="autoguideheight" data-on="Auto" data-off="Manual" data-callback="toggleMeasurement" data-checked ></label><input class="measureit" type="text" data-value="guideheight" readonly/></label>
        <div>
            <label style="display:block">Custom Guide Holes</label><textarea data-value="Guide Holes"></textarea>
        </div>
    </div>
</div>
`;

var SLATSCOMPONENT = `<div class="component" data-type="slats">
                        <h4>Slats<i class="cancel-button material-icons"></i></h4>
                        <label>Slat Type
                            <select data-value="slattype">
                                <option value="BRD" selected>BRD</option>
                                <option value="NY">New York</option>
                                <option value="CRN">Crown</option>
                                <option value="MCR">Mini Crown</option>
                            </select>
                        </label>
                        <label class="toggle" data-value="facing" data-on="Interior" data-off="Exterior" data-checked data-value="facing">Face</label>
                        <label class="toggle" data-value="assembled" data-on="Assembled" data-off="Loose" data-checked data-value="assembly">Assembly</label>
                        <div class="floatleft">
                            <label>Endlocks
                                <select data-value="endlocks">
                                    <option value="">None</option>
                                    <option value="FLSTP" selected>Flat Stamped</option>
                                    <option value="FLCST">Flat Cast</option>
                                </select>
                                <label>
                                    <input type="checkbox" data-value="continuousendlocks"/>
                                    Continuous
                                </label>
                            </label>
                        </div>
                        <div>
                            <label class="toggle" data-value="autolength" data-on="Auto" data-off="Manual" data-checked data-callback="showDataType(this,'slatlength')">Slat Length</label>
                            <div class="toggleable boxed" data-type="slatlength">
                                <label>Slat Length
                                    <input class="measureit" type="text" data-value="slatlength"/>
                                </label>
                            </div>
                        </div>
                        <div>
                            <label class="toggle" data-value="autoquantity" data-on="Auto" data-off="Manual" data-checked data-callback="showDataType(this,'slatquantity')">Quantity</label>
                            <div class="toggleable boxed" data-type="slatquantity">
                                <label>Number of Slats
                                    <input type="number" data-value="slatquantity" = min="0"/>
                                </label>
                            </div>
                        </div>
                    </div>
`;

var BOTTOMBARCOMPONENT = `<div class="component" data-type="bottombar">
                        <h4>Bottom Bar<i class="cancel-button material-icons"></i></h4>
                        <label class="toggle" data-value="facing" data-on="Interior" data-off="Exterior" data-checked data-value="facing"></label>
                        <label>Slat Type
                            <select data-value="slattype">
                                <option value="BRD" selected>BRD</option>
                                <option value="NY">New York</option>
                                <option value="CRN">Crown</option>
                                <option value="MCR">Mini Crown</option>
                            </select>
                        </label>
                        <label class="toggle" data-value="autolength" data-on="Auto" data-off="Manual" data-checked data-callback="showDataType(this,'slatinfo')">Slat Length</label>
                        <div class="toggleable boxed" data-type="slatinfo">
                            <label>Slat Length
                                <input class="measureit" type="text" data-value="slatlength"/>
                            </label>
                        </div>
                        <label>Angle
                            <select data-value="angle">
                                <option value="single">Single Angle</option>
                                <option value="double" selected>Double Angle</option>
                            </select>
                        </label>
                        <label class="toggle" data-value="bottomrubber" data-on="Standard" data-off="Custom" data-callback="showDataType(this,'rubberinfo')" data-checked>Bottom Rubber</label>
                        <div class="toggleable boxed" data-type="rubberinfo">
                            <label>Description<textarea data-value="customrubber"></textarea></label>
                        </div>
                        <label class="toggle" data-value="slope" data-on="Standard" data-off="Custom" data-callback="showDataType(this,'slopeinfo')" data-checked>Slope</label>
                        <div class="toggleable boxed" data-type="slopeinfo">
                            <label class="toggle" data-value="slopelongside" data-on="Right" data-off="Left" data-checked data-value="slopeside">Long Side</label>
                            <label>Extra Height
                            <input class="measureit" type="text" data-value="slopeheight"/></label>
                        </div>
                    </div>
`;

HOODCOMPONENT = `
                    <div class="component" data-type="hood">
                        <h4>Hood<i class="cancel-button material-icons"></i></h4>
                        <label class="toggle" data-value="baffle" data-on="Include" data-off="None" data-callback="toggleFullSeal">Hood Baffle</label>
                        <label class="toggle" data-value="standardhood" data-on="Standard" data-off="Custom" data-callback="showDataType(this,'hoodinfo')" data-checked>Hood Style</label>
                        <div class="toggleable boxed" data-type="hoodinfo">
                            <label class="toggle" data-value="autolength" data-on="Auto" data-off="Manual" data-checked data-callback="showDataType(this,'hoodlength')">Hood Length</label>
                            <div class="toggleable boxed" data-type="hoodlength">
                                <label>Length
                                    <input class="measureit" type="text" data-value="hoodlength"/>
                                </label>
                            </div>
                            <label>Description
                                <textarea data-value="hooddescription"></textarea>
                            </label>
                        </div>
                    </div>
`

ACCESSORIESCOMPONENT = `
                    <div class="component" data-type="accessories">
                        <h4>Accessory<i class="cancel-button material-icons"></i></h4>
                        <label>Type
                            <select data-value="accessorytype">
                                <optgroup label = "Hood Components">
                                    <option value="brackets">Brackets</option>
                                    <option value="motorcover">Motor Cover</option>
                                    <option value="gearcover">Gear Cover</option>
                                    <option value="facia">Facia</option>
                                </optgroup>
                                <optgroup label = "Operation Accessories">
                                    <option value="foc">Front of Motor Clip</option>
                                    <option value="chainplate">Chainplate</option>
                                </optgroup>
                                <optgroup label = "Locks">
                                    <option value="slidelocks">Slide Locks (pair)</option>
                                    <option value="pinlocks">Pin Locks (pair)</option>
                                </optgroup>
                                <optgroup label = "Misc.">
                                    <option value="feederslat">Feeder Slat</option>
                                    <option value="hardware">Hardware</options>
                                    <option value="" selected>Other</option>
                                </optgroup>
                            </select>
                        </label>
                        <div data-type="subcomponent">
                            <label>Name<input type="text" data-value="name" /></label>
                            <label>Description<input type="text" data-value="description" /></label>
                        </div>
                    </div>
`

ACCESSORYSUBS = {
    "": `
                            <label>Name<input type="text" data-value="name" /></label>
                            <label>Description<textarea data-value="description"></textarea></label>
`,
    brackets: `
                            <label class="toggle" data-value="hand" data-on="Right" data-off="Left" data-callback="" data-checked>Hand</label>
                            <label class="toggle" data-value="brackettype" data-on="Drive" data-off="Charge" data-callback="" data-checked data-value="type">Side</label>
                            <div class="toggleable boxed" data-type="bracketinfo">
                                <label>Bracket Size
                                    <select data-value="bracketsize">
                                        <option value="14">14 Inch</option>
                                        <option value="16">16 Inch</option>
                                        <option value="18" selected>18 Inch</option>
                                    </select>
                                </label>
                            </div>
`,
    motorcover: `
                            <label class="toggle" data-value="hand" data-on="Right" data-off="Left" data-callback="" data-checked data-value="hand">Hand</label>
                            <label>Additional Information<textarea data-value="additionalinfo"></textarea></label>
`,
    facia: `
                            <label>Width<label class="toggle" data-value="autowidth" data-on="Auto" data-off="Manual" data-callback="toggleMeasurement" data-checked ></label><input class="measureit" type="text" data-value="width" readonly/></label>
                            <label>Height<label class="toggle" data-value="autoheight" data-on="Auto" data-off="Manual" data-callback="toggleMeasurement" data-checked ></label><input class="measureit" type="text" data-value="height" readonly/></label>
                            <label>Additional Information<textarea data-value="additionalinfo"></textarea></label>
`,
    foc: `
                            <label>Additional Information<textarea data-value="additionalinfo"></textarea></label>
`,
    chainplate: `
                            <label>Additional Information<textarea data-value="additionalinfo"></textarea></label>
`,
    slidelocks: `
                            <label>Additional Information<textarea data-value="additionalinfo"></textarea></label>
`,
    pinlocks: `
                            <label>Additional Information<textarea data-value="additionalinfo"></textarea></label>
`,
    gearcover: `
                            <label class="toggle" data-type="hand" data-on="Right" data-off="Left" data-callback="" data-checked data-value="hand">Hand</label>
                            <label>Additional Information<textarea data-value="additionalinfo"></textarea></label>
`,
    feederslat: `
                            <label class="toggle" data-value="facing" data-on="Interior" data-off="Exterior" data-checked data-value="facing"></label>
                            <label>Slat Type
                                <select data-value="slattype">
                                    <option value="BRD" selected>BRD</option>
                                    <option value="NY">New York</option>
                                    <option value="CRN">Crown</option>
                                    <option value="MCR">Mini Crown</option>
                                </select>
                            </label>
                            <label class="toggle" data-value="autolength" data-on="Auto" data-off="Manual" data-checked data-callback="showDataType(this,'slatinfo')">Slat Length</label>
                            <div class="toggleable boxed" data-type="slatinfo">
                                <label>Slat Length
                                    <input class="measureit" type="text" data-value="slatlength"/>
                                </label>
                            </div>
`,
    hardware: `
                            <label>Type
                                <select data-value="hardware">
                                    <option value="endlocks" selected>Endlocks</option>
                                    <option value="rivets">Rivets</option>
                                    <option value="washers">Washers</option>
                                </select>
                            </label>
                            <div class="toggleable on" data-type="endlocks">
                                <label>Type
                                    <select data-value="endlocks">
                                    </select>
                                </label>
                            </div>
                            <label>Quantity
                                <input type="number" min="0" data-value="quantity" />
                            </label>
`
};

COMPONENTS = {
    pipe: PIPECOMPONENT,
    tracks: TRACKSCOMPONENT,
    slats: SLATSCOMPONENT,
    bottombar: BOTTOMBARCOMPONENT,
    hood: HOODCOMPONENT,
    accessories: ACCESSORIESCOMPONENT
};

$(document).ready(function () {
    setupCSRFAjax();
    generateToggle();
});

function addComponent(btn,component) {
    /* Adds a Component Widget Collection to the Components Div */
    let element, ele;
    if (component == "door") {
        element = $(DOORCOMPONENT);
        $("#Components").append(element);
        element.find("input[name=name]").focus();
    }
    else if (component == "complete") {
        for (component of ["pipe", "tracks", "hood", "slats", "bottombar"]) {
            addComponent(btn, component);
        }
        // Don't apply any bindings
        return
    }
    else {
        if (!(component in COMPONENTS)){ throw new Error(`Invalid Component ${component}`); };
        element = $(COMPONENTS[component]);
        ele = $(btn).parents(".component[data-type=door]");
        $(ele.children("[data-type=components]")[0]).append(element);
    };
    // For Door and Non-complete components
    element.find("i.cancel-button").on("click", removeComponent);
    generateToggle();
    measureit_rebind();
    bindQuantities();

    // Additional Bindings
    if (component == "tracks") {
        // Update for seal
        if (getToggleValue(ele.find("[data-value=fullseal]")).toLowerCase() == "seal") {
            setToggle(element.find("[data-value=weatherstripping]"), true);
        };
    }
    else if (component == "hood") {
        if (getToggleValue(ele.find("[data-value=fullseal]")).toLowerCase() == "seal") {
            setToggle(element.find("[data-value=baffle]"), true);
        };
    }
    else if (component == "slats") {
        element.find("select[data-value=slattype]").change(updateEndlocks).each(updateEndlocks);
    }
    else if (component == "accessories") {
        element.find("select[data-value=accessorytype]").change(updateSubcomponent);
    };
};

function bindQuantities() {
    /* Binds any Number input with min=0 so that "-" cannot be replaced */
    $('input[min="0"]').keydown(function (e) {
        if (e.which == 109 || e.which == 189) {
            e.preventDefault();
            return false;
        };
    })
};

function removeComponent() {
    /* Removes the given component */
    let component = findParentComponent(this);
    component.remove();
};

function findParentDoor(ele) {
    /* Returns the first door (note- there should only be one to begin with...) in the given element's parents */
    let comps = $(ele).parents(".component[data-type=door]");
    if (comps.length > 1) { return comps.first(); };
    return comps;
}

function findParentComponent(ele) {
    /* Returns the first component in the given element's parents */
    let comps = $(ele).parents(".component");
    if (comps.length > 1) { return comps.first(); };
    return comps;
};

function addSpring(button) {
    /* Adds a Spring to the Pipe Component */
    let component = $(button).parent();
    let springdiv = component.children(".springdiv");
    if (!springdiv.length) { throw new Error("Could not Determine Spring Div"); };

    let spring = $(SPRING);

    // Set change callback
    spring.children(`i.material-icons:contains("cancel")`).on("click", removeSpring);

    springdiv.append(spring);
    bindQuantities();
};

function removeSpring() {
    /* Removes the Spring from the Pipe */
    let spring = $(this).parent();
    spring.remove();
};

function toggleSeal() {
    /* Toggles all Weatherseal and Hoodbaffle Toggles to match this element's value */
    let door = findParentDoor(this);
    // I may be going crazy, but passing this.checked as an argumenent results in undefined...
    let value = this.checked;
    $(".component[data-type=tracks]").each(function () {
        setToggle($(this).find("[data-value=weatherstripping]"), value);
    });
    $(".component[data-type=hood]").each(function () {
        setToggle($(this).find("[data-value=baffle]"), value);
    });
};

function showToggles() {
    /* Shows any toggle boxes in the give same div */
    let component = findParentComponent(this);
    let toggles = component.find("div.toggleable");
    if (!toggles.length) { throw new Error("Could not Determine any toggles."); };

    if (!this.checked) {
        toggles.addClass("on");
    }
    else {
        toggles.removeClass("on");
    };
};

function showDataType(ele,datatype) {
    /* Shows any toggle box by data-type */
    let component = findParentComponent(ele);
    let toggles = component.find(`.toggleable[data-type=${datatype}]`);
    if (!toggles.length) { throw new Error("Could not Determine any toggles with the given data-type."); };

    if (!ele.checked) {
        toggles.addClass("on");
    }
    else {
        toggles.removeClass("on");
    };
};

function toggleMeasurement() {
    /* Toggles Height to Stops Input */
    let label = getToggle(this).parents().first();
    let input = label.find("input[type=text]");
    if (!input.length) { throw new Error("Could not Determine Input"); };

    if (this.checked) {
        // Selection is Not Custom, disable input
        input.prop("readonly", true);
    } else {
        // Selection is Custom, enable input
        input.prop("readonly", false);
        input.focus();
    };
};

function toggleFullSeal() {
    let door = findParentDoor(this);
    if (!this.checked) {
        setToggle(door.find("[data-value=fullseal]"), false);
    }
    else {
        let on = true;
        door.find("[data-value=weatherstripping],[data-value=baffle]").each(function () {
            on = on && getInput(this)[0].checked;
        });
        if (on) {
            setToggle(door.find("[data-value=fullseal]"), true);
        };
    };
};

function updateEndlocks() {
    /* Updates the available endlock options for the given slat type */
    let value = $(this).val();
    let component = findParentComponent(this);
    let endlocks = component.find("select[data-value=endlocks]");
    let current = endlocks.val();

    endlocks.empty();
    let endlocklist = ENDLOCKS[value];
    if (!(current in endlocklist)) {
        current = ENDLOCKS.defaults[value]
    };
    for (let endlock of endlocklist) {
        let name = ENDLOCKS[endlock];
        let select = ""
        if (endlock == current) { select = "selected"; };
        endlocks.append(`<option value=${endlock} ${select}>${name}</option>`);
    };
};

function updateSubcomponent() {
    /* Updates the current subcomponent for an Accessory Component */
    let value = $(this).val();
    let component = findParentComponent(this);
    let subdiv = component.find("div[data-type=subcomponent]");
    if (!subdiv) { throw new Error("Could not find subcomponent div"); };

    subdiv.empty();
    cmp = $(ACCESSORYSUBS[value]);
    subdiv.append(cmp);
    if (value == "facia") {
        measureit_rebind();
    }
    else if (value == "feederslat") {
        measureit_rebind();
    }
    else if (value == "hardware") {
        updateHardwareEndlocks(cmp);
        bindEndlockToggle(cmp);
        bindQuantities();
    };
    generateToggle();
};

function updateHardwareEndlocks(element) {
    /* Programattically updates the current Hardware SubComponent with available Endlocks */
    element = $(element);
    let endlocks = element.find("select[data-value=endlocks]");
    let selected = "selected";
    for (let endlock of ENDLOCKS.all) {
        // For each endlockvalue in ENDLOCKS.all, get display name
        let name = ENDLOCKS[endlock];
        endlocks.append(`<option value="${endlock}" ${selected}>${name}</option>`);
        // remove selected after first element
        selected = "";
    };
};

function bindEndlockToggle(element) {
    /* Display the Endlocks div when hardware is set to  */
    $(element).find("select[data-value=hardware]").change(toggleHardware);
};

function toggleHardware() {
    /* Toggles the Endlock display on Accessory>Hardware when "Endlocks" is (un)selected */
    let element = $(this);
    let parent = findParentComponent(this);
    let endlocks = parent.find("div.toggleable[data-type=endlocks]");
    if (element.val() == "endlocks") {
        endlocks.addClass("on");
    }
    else {
        endlocks.removeClass("on");
    };
};


/*<><><><><><><><><><><><><><><><><><><><><><><>
 
                  COLLECTION
  
 <><><><><><><><><><><><><><><><><><><><><><><>*/


function gatherComponents() {
    /* Iterates through all available components and gathers data from them */
    let compdiv = $("#Components");
    let output = []
    compdiv.children(".component[data-type=door]").each(function () {
        output.push(collectDoor($(this)));
    });
    return output;
};

function collectDoor(door) {
    /* Gathers all available information for a door */
    let output = { type: "door", components: [] }
    let info = door.children("div[data-type=doorinfo]")
    output.name = info.find("input[name=name]").val();
    output.clearheight = info.find("input[name=clearheight]").val();
    output.clearwidth = info.find("input[name=clearwidth]").val();
    output.hand = getToggleValue(info.find("label[data-value=hand]"));
    for (comp of door.children("[data-type=components]").children(".component")) {
        // Add each component of Door
        output.components.push(collectComponent($(comp)));
    };
    return output
};

function collectComponent(component) {
    /* Gathers all available information from the component */
    let type = component.attr("data-type");
    if (type == "pipe") { return collectPipe(component) };
    let output = { type: type };
    findAndProcessComponents(component, output);
    return output;
};

function collectPipe(component) {
    /* A collection function specific to pipes due to their springs sub-components */
    let type = component.attr("data-type");
    if (type != "pipe") {
        throw new Error(`collectPipe expected "pipe" element, got ${type}.`);
    };

    let output = { type:type, springs: [] };

    output.autocalculation = getToggleValue(component.find("[data-value=autocalculation]"));
    for (let val of ["pipediameter", "pipelength", "shaftdiameter", "shaftlength"]) {
        output[val] = component.find(`[data-value=${val}]`).val()
    };

    component.find("[data-type=spring]").each(function () {
        let springoutput = findAndProcessComponents($(this));
        output.springs.push(springoutput);
    });

    return output;
};

function findAndProcessComponents(element, output) {
    /* Searches the element for children with a data-value element and processes them with processComponent */
    if (typeof output === "undefined") { output = {}; };
    element = $(element);
    element.find(':not(.component)[data-value!=""][data-value]').each(function () {
        processComponent($(this), output);
    });
    // NOTE: returning output is only relevant if output was not supplied to begin with
    return output;
};

function processComponent(element, output) {
    /* Pulls element's data-value and val as a key:value pair and adds it to the provided output object */
    let key = element.attr("data-value");
    let value;
    if (element.hasClass("toggle")) {
        value = getToggleValue(element);
    }
    else {
        value = element.val();
    };
    output[key] = value;
};