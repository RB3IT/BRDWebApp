
function loadCoils() {
    /* Calls API to load the coils into the outputcoils page */
    // TODO: Handle Fail
    $.get("/inventory/coils/api/getcoillist", {page:page, pagestart: pagestart}, setCoils)//.fail(badSetTurns);
};

function setCoils(data) {
    /* Loads the coil information into the outputcoils page */
    let table = $("#coilTable");
    if (data.result != "success") { return badSetCoils(); };
    for (let coil of data.coils) {
        // Output coil to table
        $(`<tr class="coil"><td><input type='checkbox' value='${coil.pk}'/></td><td>${coil.pk}</td><td>${coil.weight}</td><td>${coil.stage}</td><td>${coil.date}</td></tr>`).appendTo(table);
    };
};

function badSetCoils(data) {
};

function outputCoils() {
    /* Composes a printable sheet of labeled QR codes that is sent to the browser's `print` command */
    let table = $("#coilTable");
    let coils = [];
    table.find("tr.coil input[type=checkbox]:checked").each(function () {
        coils.push(this.value);
    });
    if (coils.length == 0) {
        // TODO: Show error
        return;
    }
    // TODO: Handle Fail
    showLoading();
    $.get("/inventory/api/printcoils", { coils : JSON.stringify(coils) }, printCoils)//.fail(badSetTurns);
};

function printCoils(data) {
    /* The callback for outputCoils, which (sans errors) calls print(coilsheet) */
    if (printingFlag) {
        let pdfwindow = window.open("");
        pdfwindow.document.write(`<iframe width='100%' height='100%' src='data:application/pdf;base64, ${encodeURI(data)}'></iframe>`)
        hideLoading();
    };
};

function showLoading() {
    /* Shows a loading window */
    printingFlag = true;
    $("#outputButton").prop("disabled", true);
};

function hideLoading() {
    /* Hides the loading window */
    printingFlag = false;
    $("#outputButton").prop("disabled", null);
}