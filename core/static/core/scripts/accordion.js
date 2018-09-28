/* Basic Javascript + CSS Accordion adapted from W3School */

$(document).ready(function () {
    let accordions = document.getElementsByClassName("accordion");
    bindAccordions(accordions);
});

function bindAccordions(accordions) {
    /* Binds the given accordions */
    for (let accordion of accordions) {
        $(accordion).on("click", function () {
            accordion.toggleClass("active");
            let panel = $(accordion.find(".accordion-panel"));
            if (accordion.hasClass("active")) {
                panel.css("maxHeight", panel[0].scrollHeight + "px");
            } else {
                panel.css("maxHeight",0);
            };
        });
    };
};