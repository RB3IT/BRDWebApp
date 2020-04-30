
function loadCoils() {
    /* Calls API to load the coils into the outputcoils page */
    // TODO: Handle Fail
    if (page === false) {
        hideMoreButton();
        return;
    }
    $.get("api/getcoillist", {page:page, pagestart: pagestart}, setCoils)//.fail(badSetTurns);
};

function hideMoreButton() {
    $("#loadmorebtn").prop("disabled",true).css("display", "none");
};

function setCoils(data) {
    /* Loads the coil information into the outputcoils page */
    let table = $("#coilTable");
    if (data.result != "success") { return badSetCoils(); };
    page = data.nextpage;
    pagestart = data.pagestart;
    if (page === false) { hideMoreButton();}
    for (let coil of data.coils) {
        // Output coil to table
        $(`<tr class="coil" data-stage="${coil.stage}" data-size="${coil.size}"><td><input type='checkbox' value='${coil.pk}'/></td><td><a href="${coil.pk}">${coil.pk}</a></td><td>${coil.size}</td><td>${coil.weight}</td><td>${coil.stage}</td><td>${coil.date}</td></tr>`).appendTo(table);
    }
    filterCoils();
};

function badSetCoils(data) {
};

function getCoils() {
    /* Gathers a list of all selected coils */
    let table = $("#coilTable");
    let coils = [];
    table.find("tr.coil input[type=checkbox]:checked").each(function () {
        coils.push(this.value);
    });
    return coils;
};

function outputCoils() {
    /* Composes a printable sheet of labeled QR codes that is sent to the browser's `print` command */
    let coils = getCoils();
    if (coils.length == 0) {
        // TODO: Show error
        return;
    }
    // TODO: Handle Fail
    showLoading();
    $.get("api/printcoils", { coils : JSON.stringify(coils) }, printCoils)//.fail(badSetTurns);
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
    $("#statsButton").prop("disabled", true);
};

function hideLoading() {
    /* Hides the loading window */
    printingFlag = false;
    $("#outputButton").prop("disabled", null);
    $("#statsButton").prop("disabled", null);
};

function getStats() {
    /* Get the stats sheet */
    coils = getCoils();
    if (coils.length === 0) {
        showSnackbar({type:"danger",title:"No Coils",label:"No coils selected to output."});
        return;
    }
    coils = btoa(JSON.stringify(coils));
    window.location.href = "getStats?coils=" + coils;
};

function filterCoils() {
/* Filters Coil Output */
    let filters = [];
    // Build list of selected filters
    for (let rbutton of [$("#received"), $("#opened"), $("#finished"), // Stage Filters
                         $(document.getElementById("5.28")), $(document.getElementById("5.34"))] // Size Filters (note- jquery doesn't like numeric ids)
    ) {
        // If filter is checked, add it to list
        console.log(rbutton)
        if (rbutton.prop("checked")) filters.push(rbutton.attr("value"));
    }
    // Iterate over coils
    console.log(filters);
    for (let coil of $(".coil")) {
        coil = $(coil);
        // If coil's stage is in filters, unhide it
        console.log(coil.attr("data-stage"), filters.indexOf(coil.attr("data-stage")) > -1, coil.attr("data-size"), filters.indexOf(coil.attr("data-size")) > -1);
        if (filters.indexOf(coil.attr("data-stage")) > -1 && filters.indexOf(coil.attr("data-size")) > -1) {
            coil.show();
        }
        // Otherwise, hide it
        else {
            coil.hide();
            // If it was checked, uncheck it
            if (coil.find("input").prop("checked")) coil.find("input").prop("checked", false);
        }
    }
}

function selectAll() {
    let check = $("#outputSelectall").prop("checked");
    for (let coil of $(".coil")) {
        coil = $(coil);
        if (coil.css("display") !== "none") coil.find("input").prop("checked", check);
    }
}