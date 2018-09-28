var lineiter = 0;

$(document).ready(function () {
    addAutoCalcLine();
    }
);

function autoAddPopulate(inputstring) {
    if (!inputstring) { return; };
    let addlines = inputstring.split("\n");
    console.log(addlines);
    $(".autoaddline").each(function () { $(this).remove();});
    for (line of addlines) {
        if (!line || line == "None") { continue; };
        addAutoCalcLine();
        $(".autoadd").last().val(line);
    };
    addAutoCalcLine();
    autoCalc();
};

function addAutoCalcLine() {
    $("#calcholder").append(
        `<div class="inlineclear autoaddline" data-line="${lineiter}"><span class="glyphicon glyphicon-remove-sign" aria-hidden="true" onclick="removeAutoAdd(${lineiter})"></span><input class="autoadd" type="text" name="${lineiter}"  data-line=${lineiter}\><input type="button" onClick="AutoCalcNewandSum(${lineiter})" value="Calculate" data-line=${lineiter}\><\div>`
    );
    lineiter = lineiter + 1;
    $('.autoadd').keypress(function (event) {
        event.stopPropagation();
        if (event.which == 13) {
            let widget = $(this);
            AutoCalcNewandSum(widget.attr("data-line"));
            widget.blur();
        };
    });
    $(".autoadd").last().focus();
};

function AutoCalcNewandSum(iteration) {
    checkNewLine(iteration);
    updateSums();
    autoCalc();
};

function checkNewLine(iteration) {
    let autoadds = $(".autoadd");
    let lastiter = autoadds.eq(autoadds.length - 1).attr("name");
    if (iteration == lastiter) {
        addAutoCalcLine();
    };
};

function updateSums() {
    let date = `${year}-${month}-1`;
    let autoadds = $(".autoadd");
    let sumsstring = "";
    for (let auto of $.makeArray(autoadds)) {
        sumsstring = sumsstring + (auto.value ? "\n" + auto.value : "");
    };
    $.post('/inventory/api/item',
        { itemid: itemid, date: date, sums:  sumsstring},
        // Success Function here //,
        "json"
    ).fail(
        // Failure Matters?
        );
};

function autoCalc() {
    let autoadds = $(".autoadd");
    let sum = 0;
    for (i = 0; i < autoadds.length; i++) {
        let input = autoadds[i].value;
        input = input.replace("x", "\*");
        let value = math.eval(input);
        if (!isNaN(value)) {
            sum = sum + value
        };
    };
    $("#autoCalcTotal").text(sum);
};

function removeAutoAdd(iteration) {
    let autoadds = $(".autoadd");
    if (autoadds.length == 1) {
        autoadds.eq(0).val(0);
        autoCalc();
        return;
    };
    let line = $(`div[data-line="${iteration}"]`);
    if (!line) { return; };
    line.remove();
    autoCalc();
};

function autoCalcToTotal() {
    let autototal = $("#autoCalcTotal").text();
    let elementid = escapeIDSelector(itemid);
    let total = $(elementid);
    total.val(autototal);
    total.blur();
};

function escapeIDSelector(myid) {
    return "#" + myid.replace(/(:|\.|\[|\]|,|=|@)/g, "\\$1");
};