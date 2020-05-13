SOCKETELEMENT = `
<div data-type="socket" style="border:1px black solid;padding:5px;">
    <i class="material-icons cancel-button" />
    <div><span style="font-weight:bold;margin-right:-5px;">Casting Style</span><label class="toggle" data-type="castingtoggle" data-on="Single" data-off="Double" data-callback="changeCasting" data-checked style="vertical-align:middle;"></label></div>
</div>`;

CASTINGELEMENT = `
<table class="bordered-table" data-type="casting" data-value="">
    <thead>
        <tr>
            <th>Wire Gauge</th>
            <th>Outer Dia.</th>
            <th>Coils</th>
            <th>Length</th>
            <th>Torque</th>
            <th>Max Turns</th>
        </tr>
    </thead>
    <tbody>
    </tbody>
</table>
`;

SPRINGELEMENT = `
<tr data-type="spring">
    <td>
        <input type="number" class="autoclear" step="${springprec}" min="0" data-value="wiregauge" list="wiregauges" style="width:8em;"/>
    </td>
    <td>
        <input type="number" class="autoclear" step="${odprec}" min="0" data-value="outerdiameter" list="ods" style="width:6em;"/>
    </td>
    <td>
        <input data-value="coils" type="number" min="0" style="width:3em;"/>
    </td>
    <td>
        <span data-value="lengthcoiled"></span>
    </td>
    <td>
        <span data-value="torque"></span>
    </td>
    <td>
        <span data-value="maxturns"></span>
    </td>
</tr>
`;

SIDEBARASSEMBLY = `
<div class="accordion sidebar-assembly">
    <input type="text" class="vcenter" data-type="name" />
    <div class="floatleft vcenter"">
        <button type="button" onclick="sidebarLoadAssembly(this);">Set</button>
        <button type="button" onclick="removeSidebarAssembly(this);">Delete</button>
    </div>
    <div class="accordion-panel">
        <table>
            <tr>
                <td>Pipe</td>
                <td data-value="pipe"></td>
            </tr>
        </table>
    </div>
</div>
`;

SIDEBARCASTING = `
<tbody>
</tbody>
`;

SIDEBARSPRING = `
<tr>
    <td>Spring</td>
    <td data-value="gauge"></td>
</tr>`;

function bindAutoClear(ele) {
    /* Binds the OnClick event of inputs within ele to clear input */
    ele.find("input.autoclear").click(function () {
        $(this).val("");
    });
}

/***************************************************************************
 *                           GUI CONSTRUCTION
 **************************************************************************/

function addSocket(button) {
    /* Adds a Socket to the given Button's Assembly */
    let parent = $(button).parents("[data-type='assembly']");
    let socket = buildSocketElement();
    parent.append(socket);
    bindSocket(socket);
}

function bindSocket(socket) {
    /* The bindings for a socket */
    generateToggle();
    bindAutoClear(socket);
    socket.find("tr[data-type='spring'] input[data-value='coils']").on("change", getCalculateSpring);
    socket.find("tr[data-type='spring'] input[data-value='wiregauge']").on("change", getCalculateSpring);
    socket.find("tr[data-type='spring'] input[data-value='outerdiameter']").on("change", getCalculateSpring);
    socket.find("i.cancel-button").on("click", function () {
        socket.remove();
        validateAssembly();
    });
}

function buildSocketElement() {
    /* Builds an Socket Element */
    let socket = $(SOCKETELEMENT);

    let double = buildCastingElement();
    addSpringtoCasting(double);
    addSpringtoCasting(double).hide();

    socket.append(double);
    return socket;
}

function addSpringtoCasting(casting) {
    let springele = buildSpringElement();
    casting.find("tbody").append(springele);
    return springele;
}

function buildCastingElement() {
    /* Builds a Casting Element. Casting Elements are Tables. */
    return $(CASTINGELEMENT);
}

function buildSpringElement() {
    /* Builds a Spring Element. Spring Elements are Table Rows. */
    return $(SPRINGELEMENT);
}

function clearAssembly() {
    /* Removes all castings from the Current */
    $("#assembly>div[data-type='socket']").remove();
    updateAssembly();
}

function getAssembly() {
    /* Pulls the current Assembly */
    output = {
        name: "Assembly",
        castings: []
    };
    for (let casting of $("#assembly").find("div[data-type='socket']")) {
        casting = $(casting);
        let outcasting = [];
        for (let spring of casting.find("tr[data-type='spring']:visible")) {
            spring = $(spring);
            let out = {};
            out['gauge'] = spring.find("input[data-value='wiregauge']").val();
            out['od'] = spring.find("input[data-value='outerdiameter']").val();
            out['coils'] = spring.find("input[data-value='coils']").val();
            if (out['gauge'] && out['od'] && out['coils']) { outcasting.push(out); }
        }
        if (outcasting.length) {
            output.castings.push(outcasting);
        }
    }
    return output;
}

function getStoreAssembly() {
    /* Pulls the current Assembly and adds it to the Sidebar (removing it from current display) */

    let output = getAssembly();
    if (output.castings.length) {
        // Only proceed with saving and clearing if we actually have an assembly
        storeAssembly(output);
        clearAssembly();
        updateAssembly();
    }
}

function storeAssembly(assembly) {
    /* Adds an Assembly to the Sidebar */
    // API Assembly format:
    /* {                    // Assembly
            name:"",
            castings: [
                [           // Casting
                    {},...  //Springs
                ],...
            ],...
       ]
     */
    SIDEBAR.push(assembly);
    let sass = $(SIDEBARASSEMBLY);
    sass.find("input[data-type='name']").val(assembly.name);
    for (let casting of assembly.castings) {
        let sacs = $(SIDEBARCASTING);
        for (let spring of casting) {
            let sspr = $(SIDEBARSPRING);
            sspr.find("td[data-value='gauge']").html(spring.gauge);
            sacs.append(sspr);
        }
        sass.find("table").append(sacs);
    }
    $("#savedAssemblies").append(sass);
    bindAccordions([sass]);
}

function getSidebarInfo(child) {
    /* Gets the pertinant information for a given subelement of a Sidebar Assembly.
     * 
     * Returns [index,sidebarelement,SIDEBAR child object] */
    let parent = $(child).parents("div.sidebar-assembly");
    let allassemblies = $("#savedAssemblies .sidebar-assembly");
    let index = allassemblies.index(parent[0]);
    return [index, parent, SIDEBAR[index]];
}

function removeSidebarAssembly(button) {
    /* Removes the Clicked Assembly from the Sidebar (both DOM and Var) */

    let [index, sidebar, obj] = getSidebarInfo(button);
    sidebar.remove();
    SIDEBAR.splice(index, 1);
}

function sidebarLoadAssembly(button) {
    /* Gets and Loads an Assembly from the Sidebar */
    let [index, sidebar, obj] = getSidebarInfo(button);
    loadAssembly(obj);
}

function loadAssembly(assembly) {
    /* Replaces the current Assembly with the given one */
    clearAssembly();
    for (let casting of assembly.castings) {
        let socket = buildSocketElement();
        $("#assembly").append(socket);
        //TODO: The current setup only supports up to 2 springs; can be updated to 
        for (let i = 0; i < casting.length; i++) {
            let spring = casting[i];
            let springele = $(socket.find("tr[data-type='spring']")[i]);
            springele.find("input[data-value='wiregauge']").val(spring.gauge);
            springele.find("input[data-value='outerdiameter']").val(spring.od);
            springele.find("input[data-value='coils']").val(spring.coils);
            calcSpring(springele);
        }
        bindSocket(socket);
        if (casting.length === 2) {
            socket.find("input[type='checkbox']").prop('checked', false).trigger('change');
        }

    }
    updateAssembly();
    validateAssembly();
}

/***************************************************************************
 *                           Events
 **************************************************************************/
function reloadAssembly() {
    /* Reloads the assembly saved to the database for the current door */
    if (!doorid || !assembly) return;
    loadAssembly(assembly);
}

function generateAssemblies(btn) {
    /* Disable Generate Assemblies Button and Start API call for Viable Assemblies */
    $(btn).prop("disabled", true);
    let pipe = $("#pipesize").val();
    if (doorid) {
        $.get("/doors/springs/api/assemblies", { doorid: doorid, pipe: pipe }, setAssemblies).fail(badSetAssemblies);
    }
    else {
        $.get("/doors/springs/api/assemblies", { clearopening_width: door.clearopening_height, clearopening_height: door.clearopening_height, slattype:door.slattype, castendlocks:door.castendlocks, pipe: pipe }, setAssemblies).fail(badSetAssemblies);
    }
}

function setAssemblies(data) {
    /* Callback for API call in generateAssemblies */
    $("#sidebar").find(":button:disabled").remove();
    for (let assembly of data.results.assemblies) {
        storeAssembly(assembly);
    }
}

function badSetAssemblies(data) {
    /* Failure Callback for API call in generateAssemblies */
    showSnackbar({ type: "danger", label: "Bad Request", text: data });
    let btn = $("#sidebar button:contains(Generate)");
    $(btn).prop("disabled", false);
}

function toggleSidebar() {
    let toggle = $("#sidebar .toggleable");
    if (toggle.hasClass("on")) {
        toggle.removeClass("on");
        $("#sidebar .toggleable").css("display", "none");
    }
    else {
        toggle.addClass("on");
        $("#sidebar .toggleable").css("display", "block");
    }
}

function updateTurns(event) {
    /* Updates the Turns the door will make based on current pipe size */
    let pipesize = $("#pipesize").val();
    //$.ajax({
    //    type:"POST",
    //    url: "/doors/springs/api/turns",
    //    contentType:"application/json",
    //    data: JSON.stringify({
    //        doorid: doorid,
    //        pipe: pipesize
    //    }),
    //    success: setTurns,
    //    error: badSetTurns
    //});
    $.get("/doors/springs/api/turns", { doorid: doorid, pipe: pipesize }, setTurns).fail(badSetTurns);
}

function setTurns(data) {
    /* The successful response for updateTurns */
    $("#turns").prop("data-value", data.results.turns).html(data.results.turns.toFixed(2));
    $("#turnstoraise").prop("data-value", data.results.turnstoraise).html(data.results.turnstoraise.toFixed(2));
}

function badSetTurns(data) {
    /* The fail response for updateTurns */
    showSnackbar({ type: "danger", label: "Bad Request", text: data });
}

function updateTorque(event) {
    /* Updates the Torque required by the door */
    let pipesize = $("#pipesize").val();
    //$.ajax({
    //    type:"POST",
    //    url: "/doors/springs/api/turns",
    //    contentType:"application/json",
    //    data: JSON.stringify({
    //        doorid: doorid,
    //        pipe: pipesize
    //    }),
    //    success: setTurns,
    //    error: badSetTurns
    //});
    $.get("/doors/springs/api/torque", { doorid: doorid, pipe: pipesize }, setTorque).fail(badSetTorque);
    validateAssembly();
}

function setTorque(data) {
    /* The successful response for updateTorque */
    $("#torqueopen").prop("data-value", data.results.requiredtorqueopen).html(data.results.requiredtorqueopen.toFixed(2));
    $("#torqueclosed").prop("data-value", data.results.requiredtorqueclosed).html(data.results.requiredtorqueclosed.toFixed(2));
    $("#torqueperturn").prop("data-value", data.results.torqueperturn).html(data.results.torqueperturn.toFixed(2));
    validateAssembly();
}

function badSetTorque(data) {
    /* The fail response for updateTorque */
    showSnackbar({ type: "danger", label: "Bad Request", text: data });
}

function changeCasting(event) {
    /* Toggles between Single and Double Spring Castings */
    let ele = getToggle(event.target);
    let assembly = ele.parents("[data-type='socket']");
    let springs = assembly.find("tr[data-type='spring']");
    if (getToggleValue(ele) === 'Single') {
        springs.slice(1).hide();
    }
    else {
        springs.slice(1).show();
    }
    validateAssembly();
}

function calculateRequiredLift() {
    /* Calculates the Required Lift-per-Turn */
    let turns = $("#turnstoraise").prop("data-value");
    let liftopen = $("#torqueopen").prop("data-value"); 
    let liftclosed = $("#torqueclosed").prop("data-value");

    return (liftclosed - liftopen) / turns;
}

function getTotalLift() {
    /* Returns the total lift of all Springs on the current Assembly */
    let lift = 0;

    function springLift() {
        let springlift = parseFloat($(this).find("span[data-value='torque']").first().text());
        if (springlift) {
            lift += springlift;
        }
    }

    function castingLift() {
        $(this).find("tr:visible[data-type='spring']").each(springLift);
    }

    $("#assembly").find("table[data-type='casting']").each(castingLift);

    return lift;
}

function getShaftLength() {
    /* Returns the total shaft length for the current Assembly */
    // Base length for Outside @ 9" + 2" For Bearing/Inside space + 2" For Shaft Support 
    let length = 13;
    let turns = 1.0 * $("#turns").prop("data-value");
    function springLength() {
        let coils = $(this).find("input[data-value='coils']").val();
        let gauge = $(this).find("input[data-value='wiregauge']").val();
        // Length of Coils (coils * gauge) + Stretch (turns * gauge*2)
        let springlength = coils * gauge + turns * gauge * 2;
        if (springlength) {
            // TODO: This 6 is a placeholder for Casting Length: Make more accurate correction
            springlength += 6;
            length += springlength;
        }
    }

    function castingLength() {
        $(this).find("tr:visible[data-type='spring']").each(springLength);
    }

    $("#assembly").find("table[data-type='casting']").each(castingLength);

    return length;
}

function getSpring(springele) {
    /* Returns the spring object representation of a spring ele with all stats populated */
    let gauge = springele.find("input[data-value='wiregauge']").val();
    let od = springele.find("input[data-value='outerdiameter']").val();
    let coils = springele.find("input[data-value='coils']").val();
    let cyclerating = $("#cyclerating").val();
    if (!gauge || isundefined(gauge) ||
        !od || isundefined(od) ||
        !coils || isundefined(coils)) {
        return;
    }
    let spring;
    try {
        return calculateSpring({
            gauge: gauge,
            od: od,
            coils: coils,
            cyclerating: cyclerating
        });
    } catch{
        showSnackbar({ type: "danger", label: "Unknown Spring", text: "Site not programmed to handle the given spring." });
        return;
    }
}

function getCalculateSpring(event) {
    /* Event hook for calcSpring */
    let springele = $(event.target).parents("tr[data-type='spring']");
    return calcSpring(springele);
}

function calcSpring(springele) {
    /* Calculates Information for a given Spring */
    springele = $(springele);
    let spring = getSpring(springele);
    
    let lengthcoiled = 0;
    let torque = 0;
    let maxturns = 0;
    if (spring) {
        lengthcoiled = Math.round(spring.lengthcoiled * 1000) / 1000;
        torque = Math.round(spring.torque * 1000) / 1000;
        maxturns = Math.round(spring.maxturns * 1000) / 1000;
    }
    springele.find("span[data-value='lengthcoiled']").html(lengthcoiled);
    springele.find("span[data-value='torque']").html(torque);
    springele.find("span[data-value='maxturns']").html(maxturns);

    // updateTorqueperTurn(); // I don't know why we're updating this here...
    updateAssembly();
    validateAssembly();
}

function updateTorqueperTurn() {
    /* Updates the TorqueperTurn Span element
     
        TODO: I don't know why this function exists....
     */
    let v = calculateRequiredLift();
    $("#torqueperturn").prop("data-value",v).html(v.toFixed(2));
}

function validateCasting() {
    /* Validates all springs on the casting */
    let springeles = $(this).find("tr[data-type='spring']");
    let springs = [];
    for (let springele of springeles) {
        springele = $(springele);
        let spring = getSpring(springele);
        if (spring) {
            springele.removeClass("invalid");
            let turns = $("#turns").prop("data-value");
            if (spring.maxturns < turns * .985) {
                showSnackbar({ type: "danger", label: "Max Turns", text: "Max Turns for this spring is lower or too close to number of Turns." });
                springele.addClass("invalid");
            }
            else if (spring.mp / turns * .99 > spring.lift || spring.mp / turns * 1.015 < spring.lift) {
                showSnackbar({ type: "danger", label: "MP/Turn Error", text: "MP/Turn's for this spring is lower or too close to MP/Turn." });
                springele.addClass("invalid");
            }
            springs.push(spring);
        }
    }
}

function updateAssembly() {
    /* Updates the Displayed Statistics of the current Assembly */
    $("#totallift").html(getTotalLift());
    $("#shaftlength").html(getShaftLength());
}

function validateAssembly() {
    /* Validates all casting in an assembly and validates the assembly itself */
    let castings = $("#assembly").find("table[data-type='casting']");
    castings.each(validateCasting);

    let requiredlift = calculateRequiredLift();
    let lift = getTotalLift();
    if (!lift) { return; }
    if (requiredlift * .99 > lift || requiredlift * 1.015 < lift) {
        showSnackbar({ type: "danger", label: "Unacceptable Torque", text: "Torque is not close enough Torque required (Avg. Torque Req.)." });
        castings.each(function () {
            $(this).find("tr[data-type='spring']").addClass("invalid");
        });
    }
}

function getDoorPopup() {
    /* Triggers the Popup to get or calculate a door */
    if (popup) return popup.focus();
    $("#doorbutton").prop("disabled", true);
    console.log('here')
    popup = window.open("/doors/doorgen_popup.html", "Set Door", "width=400,height=400");
    let timer = setInterval(function () {
        if (popup.closed) {
            clearInterval(timer);
            door = popup.door;
            if (door !== undefined) {
                $("#weightclosed").val(door.hangingweight_closed);
                $("#weightopen").val(door.hangingweight_open);
                $("#torqueclosed").text(door.requiredtorque_closed);
                $("#torqueopen").text(door.requiredtorque_open);
                $("#torqueperturn").text(door.torqueperturn);
                $("#turns").text(door.totalturns);
                $("#turnstoraise").text(door.turnstoraise);
                $("#pipesizes").text(door.pipe.shell);
            }
            enableDoorButton();
            popup = undefined;
        }
    }, 1000);
}
function enableDoorButton() {
    /* Enables the door button (used after popup is closed) */
    $("#doorbutton").prop("disabled", null);
}
