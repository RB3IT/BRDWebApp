$(document).ready(function () {
    autoAddPopulate();
    }
);

function autoAddPopulate() {
    /* Populates Auto Calc with the initial lines */
    // No input
    if (!autolines) { return; }
    // Convert to array
    let addlines = autolines.split("\n");

    $(".autoaddline").empty();

    for (line of addlines) {
        // Skip empty lines
        if (!line || line === "None") { continue; }
        // Get new widget
        let linewidget = addAutoCalcLine(line);
    }
    // Add new line at end
    addAutoCalcLine();    
}

function addAutoCalcLine(value) {
    /* Adds a new Auto Calc Line */
    // Create and add line
    let line = $(`<div class="inlineclear autoaddline">
    <i class="material-icons cancel-button" onclick="removeAutoAdd(this);"></i>
    <input class="autoadd" type="text"\>
    <input type="button" onClick="autoCalcNewandSum();" value="Calculate"\>
<\div>`);
    $("#calcholder").append(line);
    line.keypress(function (event) {
        event.stopPropagation();
        if (event.which === 13) {
            autoCalcNewandSum();
            $(this).blur();
        }
    });
    line.find("input.autoadd").focus();

    // Add value if available
    if (typeof value !== "undefined") {
        line.find("input.autoadd").val(value);
    }

    // Auto Calculate
    autoCalc();

    return line;
}

function autoCalcNewandSum() {
    /* Primary usage loop: Check if a new line needs to be added, Send Update to API, AutoCalc GUI */
    if (!$(".autoaddline").length || $(".autoaddline:last input.autoadd").val()) {
        addAutoCalcLine();
    }
    updateSums();
    autoCalc();
}

function updateSums() {
    /* Calls the API to update the item's sums */
    let date = `${year}-${month}-1`;
    let autoadds = $(".autoadd");
    let sumsstring = "";
    for (let auto of $.makeArray(autoadds)) {
        sumsstring = sumsstring + (auto.value ? "\n" + auto.value : "");
    }
    $.post('/inventory/api/item',
        { itemid: itemid, date: date, sums:  sumsstring},
        // Success Function here //,
        "json"
    ).fail(
        // Failure Matters?
        );
}

function autoCalc() {
    /* Executes the Auto Calculation and sets the GUI */
    let autoadds = $(".autoadd");
    let sum = 0;
    for (i = 0; i < autoadds.length; i++) {
        let input = autoadds[i].value;
        input = input.replace("x", "\*");
        let value = math.eval(input);
        if (!isNaN(value)) {
            sum = sum + value;
        }
    }
    $("#autoCalcTotal").text(sum);
}

function removeAutoAdd(span) {
    let line = $(span).parents(".autoaddline");
    line.remove();
    autoCalcNewandSum();
}

function autoCalcToTotal() {
    let autototal = $("#autoCalcTotal").text();
    let elementid = escapeIDSelector(itemid);
    let total = $(elementid);
    total.val(autototal);
    total.blur();
}

function escapeIDSelector(myid) {
    return "#" + myid.replace(/(:|\.|\[|\]|,|=|@)/g, "\\$1");
}