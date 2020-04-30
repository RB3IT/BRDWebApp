var SNACKBAR;

$(document).ready(function () {
    checkSnackbar();
});

function setupSnackbar() {
    /* Adds the snackbar to the page */
    let container = $(".snackbar-container");
    if (!container.length) {
        throw new Error("No Snackbar Container defined");
    };
    SNACKBAR = $(`<div id="snackbar" style="display:none;position:absolute;z-index:1;width:50%;margin:0,auto;">
                <span id="snackbar-label" style="font-weight:bold;">&nbsp;</span>&nbsp;<span id="snackbar-text"></span>
            </div>`)
    container.append(SNACKBAR);
};

function checkSnackbar() {
    /* Checks that snackbar exists. If it doesn't, add it */
    if (!$("#snackbar").length) {
        setupSnackbar();
    };
};

function showSnackbar(options) {
    /* Shows the snackbar

        Options:
            type: Snackbar Alert Style ("sucess","info","warning","danger"). Default style is "info".
            label: Snackbar Label (leading bold text). If not supplied, this will reflect the type.
            text: Additional text descrining the alert. By default, this is an empty string.
    */
    checkSnackbar();
    let defaults = { type: "info", label: null, text: "" };
    for (let k of ["type", "label", "text"]) {
        if (typeof options[k] !== "undefined") {
            defaults[k] = options[k];
        };
    };
    if (["success", "info", "warning", "danger"].indexOf(defaults["type"]) < 0) {
        throw new Error("Invalid Alerttype");
    };
    if (defaults["label"] == null) {
        defaults["label"] = defaults['type'].charAt(0).toUpperCase() + defaults['type'].slice(1) + "!"
    };
    SNACKBAR.removeClass().addClass(`alert alert-${defaults["type"]}`);
    $("#snackbar-label").html(defaults["label"]);
    $("#snackbar-text").html(defaults["text"]);
    SNACKBAR.fadeIn(400).delay(2000).fadeOut(400);
};