
function loadSprings() {
    /* Calls API to load the springs into the outputsprings page */
    // TODO: Handle Fail
    if (page === false) {
        hideMoreButton();
        return;
    }
    $.get("api/getspringlist", { page: page, pagestart: pagestart }, setSprings);
};

function hideMoreButton() {
    $("#loadmorebtn").prop("disabled",true).css("display", "none");
};

function setSprings(data) {
    /* Loads the spring information into the outputsprings page */
    let table = $("#springTable");
    if (data.result != "success") { return badSetSprings(); };
    page = data.nextpage;
    pagestart = data.pagestart;
    if (page === false) { hideMoreButton();}
    for (let spring of data.springs) {
        // Output spring to table
        $(`<tr class="spring" data-stage="${spring.stage}" data-size="${spring.size}"><td><input type='checkbox' value='${spring.pk}'/></td><td><a href="${spring.pk}">${spring.pk}</a></td><td>${spring.size}</td><td>${spring.length}</td><td>${spring.stage}</td><td>${spring.date}</td></tr>`).appendTo(table);
    }
    filterSprings();
};

function badSetSprings(data) {
};

function getSprings() {
    /* Gathers a list of all selected spring */
    let table = $("#springTable");
    let springs = [];
    table.find("tr.spring input[type=checkbox]:checked").each(function () {
        springs.push(this.value);
    });
    return springs;
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
    springs = getSprings();
    if (springs.length === 0) {
        showSnackbar({ type: "danger", title: "No Springs", label:"No springs selected to output."});
        return;
    }
    springs = btoa(JSON.stringify(springs));
    window.location.href = "getStats?springs=" + springs;
};

function filterSprings() {
/* Filters Spring Output */
    let filters = [];
    // Build list of selected filters
    for (let rbutton of $("input.filter")) {
        // If filter is checked, add it to list
        if (rbutton.checked) filters.push(rbutton.getAttribute("value"));
    }
    // Iterate over Springs
    for (let spring of $(".spring")) {
        spring = $(spring);
        // If spring's stage is in filters, unhide it
        if (filters.indexOf(spring.attr("data-stage")) > -1 && filters.indexOf(spring.attr("data-size")) > -1) {
            spring.show();
        }
        // Otherwise, hide it
        else {
            spring.hide();
            // If it was checked, uncheck it
            if (spring.find("input").prop("checked")) spring.find("input").prop("checked", false);
        }
    }
}

function selectAll() {
    let check = $("#outputSelectall").prop("checked");
    for (let spring of $(".spring")) {
        spring = $(spring);
        if (spring.css("display") !== "none") spring.find("input").prop("checked", check);
    }
}