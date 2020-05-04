$(document).ready(getLoadSketch);

function getLoadSketch() {
/* Queries the API for the sketch */
    if (!doorid) return;
    $.get("/doors/order/api/sketches", { doorid: doorid }, loadSketch);
}

function loadSketch(resp) {
    /* Callback for getLoadSketch which displays the returned image */
    console.log(resp);
}