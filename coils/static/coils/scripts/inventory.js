$(document).ready(function () {

    setupCSRFAjax();

    $('.autoupdate').focusout(autoUpdate);
    $('.autoupdate').keypress(function (event) {
        event.stopPropagation();
        if (event.which == 13) {
            autoUpdate;
            $(this).blur();
        };
    });

});