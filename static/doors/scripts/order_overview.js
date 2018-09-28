var POPUPSHELL = `
<div id="popup" class="popup">
</div>`

$(document).ready(function () {
    bind_popups();
    setupCSRFAjax();
});

function bind_popups() {
    /* Binds the Magnifying Glasses on the page (<i material-icons search>)
     * to trigger a popup window */

    $("i.popup-icon").click(popupWindow);
};

function popupWindow(event) {
    /* Opens a popup window that displays information about the item selected */
    let ele = $(event.target);
    let popup = $(POPUPSHELL);

    event.preventDefault();

    let parent = ele.parents(".door");
    let doorid = parent.attr("data-id");
    let type = ele.attr("data-type");
    let id = ele.attr("data-id");
    let content;
    switch (type) {
        case "pipe":
            content = popupPipe(ele);
            callback = populatePipe;
            break;
        case "tracks":
            content = popupTracks(ele);
            callback = populateTracks;
            break;
        case "hood":
            content = popupHood(ele);
            callback = populateHood;
            break;
    };
    
    if (!content) {
        /* This code should never fire */
        popup.remove();
        throw new Error("Did not generate any content");
    };
    popup.html(content);
    $("body").append(popup);

    let rect = popup[0].getBoundingClientRect();
    popup.css({ "margin-left": -rect.width / 2, "margin-top": -rect.height / 2 });

    popup.css("visibility", "visible");

    function destroypopup(e) {
        let target = e.target;
        popup.remove();
        $(document).unbind("click.popup");
    };

    $.ajax({
        url: "componentapi",
        success: function(data){ callback(data, type,popup); },
        data: {doorid:doorid, id:id,type:type}
    }).fail(failPopup);

    $(document).on("click.popup", destroypopup);
    return false;
};


function popupPipe(ele) {
    /* Templates the popup for a Pipe */
    let content = $(`
<div>
    <table class="popup-table">
        <caption>Pipe</caption>
        <tbody>
            <tr>
                <td>Pipe Length</td>
                <td data-value="pipelength"></td>
            </tr>
            <tr>
                <td>Pipe Dia.</td>
                <td data-value="pipediameter"></td>
            </tr>
            <tr>
                <td>Shaft Length</td>
                <td data-value="shaftlength"></td>
            </tr>
            <tr>
                <td>Shaft Dia.</td>
                <td data-value="shaftdiameter"></td>
            </tr>
        </tbody>
    </table>
</div>
`);

    let springs = ele.parents("tr").first().find("td")[2]
    springs = parseInt(springs);
    if (!Number.isInteger(springs)) {
        springs = 0;
    };

    for (let i = 0; i < springs; i++) {
        let springele = $(`
<table class="popup-table" data-type="spring">
    <caption>Spring</caption>
    <tbody>
        <tr>
            <td>Position</td>
            <td data-type="springtype"></td>
        </tr>
        <tr>
            <td>Wire</td>
            <td data-type="wirediameter"></td>
        </tr>
        <tr>
            <td>OD</td>
            <td data-type="outerdiameter"></td>
        </tr>
        <tr>
            <td>Stretch</td>
            <td data-type="stretch"></td>
        </tr>
    </tbody>
</table>
`);
        content.append(springele);
    };

    return content;
};

function popupTracks(ele) {
    /* Templates the popup for Tracks */
    let brackets = $(`
<table class="popup-table" data-type="brackets">
    <caption>Brackets</caption>
    <tbody>
        <tr>
            <td>Size</td>
            <td data-type="size"></td>
        </tr>
        <tr>
            <td >Drive</td>
            <td data-type="hand"></td>
        </tr>
    </tbody>
</table>`);
    let angles = $(`
<table class="popup-table" data-type="angle">
    <caption>Tracks</caption>
    <tbody>
        <tr>
            <td>Wall Angle</td>
            <td data-type="wallangle"></td>
        </tr>
        <tr>
            <td>Inner Angle</td>
            <td data-type="innerangle"></td>
        </tr>
        <tr>
            <td>Outer Angle</td>
            <td data-type="outerangle"></td>
        </tr>
        <tr>
            <td>Weather Stripping</td>
            <td data-type="weatherstripping"></td>
        </tr>
        <textarea style="display:none;" data-type="holepattern" readonly />
    </tbody>
</table>
`)
    return brackets.add(angles)
};

function popupHood(ele) {
    /* Templates the popup for Tracks */
    let content = `
<table class="popup-table">
    <caption>Hood</caption>
    <tr>
        <td>Width</td>
        <td data-type="width"></td>
    </tr>
    <tr>
        <td>Shape</td>
        <td data-type="shape"></td>
    </tr>
    <tr>
        <td>Hood Baffle</td>
        <td data-type="baffle"></td>
    </tr>
    <textarea style="display:none;" data-type="description" readonly />
</table>
`
    return content;
};

function populatePipe(data,model,popup) {
    /* Populates the current Pipe Popup with data from the API */
    table = popup.find("table.popup-table");

    if ([data.pipelength, data.pipediameter, data.shaftlength, data.shaftdiameter].some(d => d == "Auto")) {
        popup.append(
            $(`<button type="btn" onclick="calculateDoor(${data.doorid})"> Calculate </button>`)
        );
    };

    table.find('td[data-value="pipelength"]').html(data.pipelength);
    table.find('td[data-value="pipediameter"]').html(data.pipediameter);
    table.find('td[data-value="shaftlength"]').html(data.shaftlength);
    table.find('td[data-value="shaftdiameter"]').html(data.shaftdiameter);
    //TODO: Load Springs
};

function populateTracks(data, model, popup) {
    /* Populates the current Tracks Popup with data from the API */
    table = popup.find("table.popup-table");
    table.find('td[data-type="size"]').html(data['bracketsize']);
    table.find('td[data-type="hand"]').html(data['hand']);
    table.find('td[data-type="wallangle"]').html(data['wall_angle_height']);
    table.find('td[data-type="innerangle"]').html(data['inner_angle_height']);
    table.find('td[data-type="outerangle"]').html(data['outer_angle_height']);
    let weather;
    if (data['weatherstripping']) {
        weather = $('<i class="material-icons true-icon"></i>');
    }
    else { weather = $('<i class="material-icons false-icon"></i>'); };
    table.find('td[data-type="weatherstripping"]').append(weather);
    let pattern = data['hole_pattern'];
    if (pattern) {
        let text = table.find('td[data-type="holepattern"]').val(pattern).css("display","block");
    };
    
};

function populateHood(data, model, popup) {
    /* Populates the current Hood Popup with data from the API */
    table = popup.find("table.popup-table");
    table.find('td[data-type="width"]').html(data['width']);
    table.find('td[data-type="shape"]').html(data['custom']);
    let baffle;
    if (data['baffle']) {
        baffle = $('<i class="material-icons true-icon"></i>');
    }
    else { baffle = $('<i class="material-icons false-icon"></i>'); };
    table.find('td[data-type="baffle"]').append(baffle);
    let description = data['description'];
    if (description) {
        let text = table.find('td[data-type="description"]').val(description).css("display", "block");
    };

};

function failPopup(data) {
    /* Shows an Error Message and closes the Popup window */
    $("div.popup").remove();
    $(document).unbind("click.popup");
    showSnackbar({ alerttype: "warning", label: "Popup Error", text: `Failed to get Popup Data: ${data.responseText}` })
};

function calculateDoor(doorid) {
    /* Sends a request to the server to calculate the stats on the given door */

    $.ajax({
        url: "doorupdate",
        method:"POST",
        success: function (data) { location.reload(); },
        data: { doorid: doorid }
    }).fail(failUpdate);

};

function failUpdate(data) {
    /* Shows an Error Message when the Door fails to update */
    if (Math.floor(data.status / 100) == 5) {
        showSnackbar({ alertype: "warning", label: "Calculation Failure", text: `Failed to AutoCalculate Door: ${data.responseText}` });
    } else {
        showSnackbar({ alertype: "warning", label: "Calculation Failure", text: `Failed to AutoCalculate Door: ${data.status} ${data.statusText}` })
    }
};