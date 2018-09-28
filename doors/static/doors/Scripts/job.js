$(document).ready(function () {
    $("#customer").on('input',updateID).keyup(autoCompleteAjax);
});

var ERRORBUBBLES = {
    "customer": "#customer",
    "customerpo": "#customer_po",
    "workorder": "#work_order",
    "origindate": "#origin_date",
    "duedate": "#due_date"
};

function showError(element, text) {
    /* Shows a blur Bubble at a given element with the given text */
    if (typeof element === "string") {
        if (!(ERRORBUBBLES.hasOwnProperty(element))) {
            throw new Error(`Invalid Error: ${element}`);
        };
        element = ERRORBUBBLES[element];
    };
    element = $(element);
    blurBubble(element, text);
};

function updateID(event) {
    let ele = $("#customer");
    let elelist = $("#customer_list");
    if (!ele | !elelist | typeof ele == undefined | typeof elelist == undefined | !ele.val()) { return; };
    let selected = elelist.children(`option[value=${ele.val()}]`);
    if (!selected.length | typeof ele == undefined) { return; };
    let id = selected.attr('data-id');
    $("#customer_id").attr("value", id);
    // Close dropdown Menu
    ele.blur();
    $("#customer_po").focus();
};

function gatherForm() {
    /* Gathers and validates the form data */
    let formele = $("#jobinfoform");
    let out = formele.serializeArray();
    let data = {};
    for (let obj of out) {
        let [k, v] = [obj.name, obj.value];
        data[k] = v;
    };
    let valid = true;
    if (!data.customer) {
        showError("customer", "Customer name Required")
        valid = false;
    };
    if (!data.origin_date) {
        showError("origindate", "Order Date is Required");
        valid = false;
    };
    if (!data.due_date) {
        showError("duedate", "Due Date is Required");
        valid = false;
    }
    else if (data.origin_date && new Date(data.due_date) < new Date(data.origin_date)) {
        showError("duedate", "Due Date cannot be before Order Date")
        valid = false;
    };
    if (valid) { return data; };
};

function submitOrder(event) {
    /* Gathers and Submits Order Form */
    $(".errorbubble-container").off("click.bubble", "*").off("blur.bubble").remove();
    showSubmitIndicator();
    let data = gatherForm();
    if (!data) {
        hideSubmitIndicator();
        let offset = $("#jobinfoform").offset();
        let top = offset.top;
        if ($("#navbar").length) {
            top -= $("#navbar").height();
        }
        window.scroll(0, top);
        return;
    };
    let doors = gatherComponents();
    data.doors = doors;
    hideSubmitIndicator();
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "/doors/order/validate",
        data: JSON.stringify(data),
        success: redirectoOrder,
        error: processSubmitOrderError
    });
};

function showSubmitIndicator() {
    $("#submitindicator").css("display", "block");
};

function hideSubmitIndicator() {
    $("#submitindicator").css("display", "none");
};


function redirectoOrder(response) {
    /* Callback to redirect to the submitted order */
    ordernumber = response.ordernumber;
    // Server Error
    if (!ordernumber) {
        showSubmitOrderError({status:500});
        return;
    }
    // Otherwise, redirect to order summary
    window.location.href = `/doors/orderinfo/${ordernumber}`;
};

function processSubmitOrderError(error) {
    /* Process a bad response from the server */
    data = error.responseJSON;

    // Unknown (server/network) Error
    if (typeof data == "undefined") {
        showSnackbar({ alerttype: "warning", label: "Unknown Submittion Error", text: `Failed to submit Order` });
        return;
    }

    // ShowResponseErrors may use the Snackbar, which would interfere
    // with showSubmitOrderError(as well as be redundant)
    let showSnackbarResponse
    //try {
        showSnackbarResponse = showResponseErrors(data['results']);
    //} catch (e) { console.log(e);};

    // If showResponseErrors used the Snackbar, don't use it.
    if (showSnackbarResponse) { showSubmitOrderError(error); };
};

function showSubmitOrderError(error) {
    /* Shows an error when the order submission fails */
    hideSubmitIndicator();
    let errorcode = "Unknown";
    if (error.status) { errorcode = error.status; };
    showSnackbar({ alerttype: "danger", label: `Failed to Save (${errorcode})`, text: "please attempt to resubmit" });
};

function showResponseErrors(errors) {
    /* Iterates through errors and generates error bubbles for each */
    // 
    let focused = false;
    let ele;
    function checkScrolled() {
        /* Checks if we have scrolled to the first error yet, and if not, does so. */
        if (!focused && ele) {
            ele[0].scrollIntoView();
            window.scrollBy(0, -100);
            focused = true;
        };
    };

    let joberrors = errors['job']
    let text;
    for (let error of joberrors) {
        switch (error) {
            case "Invalid Customer":
                ele = "customer";
                text = "Invalid Customer Name";
                break;
            case "Invalid Customer PO":
                ele = "customerpo";
                text = "Invalid Customer PO";
                break;
            case "Bad Work Order":
                ele = "workorder";
                text = "Invalid Work Order";
                break;
            case "Bad Origin Date":
                ele = "origindate";
                text = "Invalid Origin Date";
                break;
            case "Bad Due Date":
                ele = "duedate";
                text = "Invalid Due Date";
                break
            case "Bad Origin or Due Date":
                ele = "duedate";
                text = "Due Date cannot be before Order Date"
        };
        // Unknown Error
        if (!ele) {
            showSnackbar({ alerttype: "warning", label: "Unknown Submittion Error", text: `(${error})` });
        };
        showError(ele, text);
        checkScrolled();
    };
    let doors = $(".component[data-type=door]")
    for (let doorerrors of errors['doors']) {
        let doorele = $(doors[doorerrors.index]);
        ele = doorele.find('input[name="name"]').first();
        let out = []
        if (doorerrors.door) {
            let doorerrorstring = doorerrors.door.map(e => `Door: ${e}`);
            out.push(doorerrorstring.join("<br />"));
        };
        if (doorerrors.components) {
            let componenterrorstring = doorerrors.components.map(e => `Component: ${e}`);
            out.push(componenterrorstring.join("<br />"));
        };
        let errorstring = out.join("<br />");
        showError(ele, errorstring);
        checkScrolled();
    };
};