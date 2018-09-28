var POPUPSHELL = `
<div id="popup" class="floating popup">
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
        case "slats":
            content = popupSlats(ele);
            callback = populateSlats;
            break
        case "bottombar":
            content = popupBottombar(ele);
            callback = populateBottombar;
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
        success: function(data){ callback(data, type, popup); },
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
    
    let headers = ele.parents("table").first().find("thead").first();
    let heads = headers.find("tr.headerrow").first().find("td");
    let springhead = headers.find("td:contains(Springs)").first();
    let index = heads.index(springhead);
    index = parseInt(index);
    let springs = parseInt(ele.parents("tr").first().find("td").slice(index).text());
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
            <td data-value="springtype"></td>
        </tr>
        <tr>
            <td>Wire</td>
            <td data-value="wirediameter"></td>
        </tr>
        <tr>
            <td>OD</td>
            <td data-value="outerdiameter"></td>
        </tr>
        <tr>
            <td>Stretch</td>
            <td data-value="stretch"></td>
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
    /* Templates the popup for Hood */
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

function popupSlats(ele) {
    /* Templates the popup for Slats */
    let content = `
<table class="popup-table">
    <caption>Slats</caption>
    <tr>
        <td>Profile</td>
        <td data-type="slattype"></td>
    </tr>
    <tr>
        <td>Width</td>
        <td data-type="width"></td>
    </tr>
    <tr>
        <td>Quantity</td>
        <td data-type="quantity"></td>
    </tr>
    <tr>
        <td>Facing</td>
        <td data-type="face"></td>
    </tr>
    <tr>
        <td>Assembled</td>
        <td data-type="assembly"></td>
    </tr>
</table>
<table class="popup-table" data-type="endlocks">
    <caption>Endlocks</caption>
    <tr>
        <td>Type</td>
        <td data-type="endlocktype"></td>
    </tr>
    <tr>
        <td>Continuous</td>
        <td data-type="endlockcont"></td>
    </tr>
    <tr>
        <td>Quantity</td>
        <td data-type="endlockquantity"></td>
    </tr>
</table>
`
    return content;
};

function popupBottombar(ele) {
    /* Templates the popup for Bottombar */
    let content = `
<table class="popup-table">
    <caption>Bottombar</caption>
    <tr>
        <td>Feeder Slat</td>
        <td data-type="slat_type"></td>
    </tr>
    <tr>
        <td>Face</td>
        <td data-type="facing"></td>
    </tr>
    <tr>
        <td>Width</td>
        <td data-type="width"></td>
    </tr>
    <tr>
        <td>Angle</td>
        <td data-type="angle"></td>
    </tr>
    <tr>
        <td>Rubber</td>
        <td data-type="bottom_rubber"></td>
    </tr>
</table>
`
    return content;
};

function populatePipe(data,model,popup) {
    /* Populates the current Pipe Popup with data from the API */
    table = popup.find("table.popup-table:has(caption:contains(Pipe))");

    if ([data.pipelength, data.pipediameter, data.shaftlength, data.shaftdiameter].some(d => d == "Auto")) {
        popup.append(
            $(`<button type="btn" onclick="setSprings(${data.doorid})"> Set Springs </button>`)
        );
    };

    table.find('td[data-value="pipelength"]').html(data.pipelength);
    table.find('td[data-value="pipediameter"]').html(data.pipediameter);
    table.find('td[data-value="shaftlength"]').html(data.shaftlength);
    table.find('td[data-value="shaftdiameter"]').html(data.shaftdiameter);

    if (data.assembly) {
        springtables = popup.find("table.popup-table[data-type=spring]");
        for (let i = 0; i < data.springs; i++) {
            let stable = springtables.slice(i,i+1);
            if (!stable) { break; };
            stable.find('td[data-value="springtype"]').html(data.assembly[i].springtype);
            stable.find('td[data-value="wirediameter"]').html(data.assembly[i].wirediameter);
            stable.find('td[data-value="outerdiameter"]').html(data.assembly[i].outerdiameter);
            stable.find('td[data-value="stretch"]').html(data.assembly[i].stretch);
        };
    };
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

function populateSlats(data, model, popup) {
    /* Populates the current Slats Popup with data from the API */
    table = popup.find("table.popup-table");
    table.find('td[data-type="slattype"]').html(data['slat_type_name']);
    table.find('td[data-type="width"]').html(data['width']);
    table.find('td[data-type="quantity"]').html(data['slatquantity']);
    table.find('td[data-type="face"]').html(data['facing']);
    let assemble;
    if (data['assemble']) {
        assemble = $('<i class="material-icons true-icon"></i>');
    }
    else { assemble = $('<i class="material-icons false-icon"></i>'); };
    table.find('td[data-type="assembly"]').append(assemble);

    let endlocktable = popup.find('table.popup-table[data-type="endlocks"]');
    if (!data['endlocktype']) {
        endlocktable.find('tr').remove();
    }
    else {
        table.find('td[data-type="endlocktype"]').html(data['endlocktype']);
        let endlockcont;
        if (data['endlockcontinuous']) {
            endlockcont = $('<i class="material-icons true-icon"></i>');
        }
        else { endlockcont = $('<i class="material-icons false-icon"></i>'); };
        table.find('td[data-type="endlockcont"]').append(endlockcont);

        table.find('td[data-type="endlockquantity"]').html(data['endlockquantity']);

        if (data['windlockquantity']) {
            let windlocks = data['windlockquantity'];
            endlocktable.append($(`
<tr>
    <td>Windlocks</td>
    <td>${windlocks}</td>
</tr>
`));
        };
    };
};

function populateBottombar(data, model, popup) {
    /* Populates the current Bottombar Popup with data from the API */
    table = popup.find("table.popup-table");
    table.find('td[data-type="slat_type"]').html(data['slat_type_name']);
    table.find('td[data-type="facing"]').html(data['face_name']);
    table.find('td[data-type="width"]').html(data['width']);
    table.find('td[data-type="angle"]').html(data['angle']);
    table.find('td[data-type="bottom_rubber"]').html(data['bottom_rubber']);
    if (data['slope']) {
        slopeinfo = $(`
    <tr>
        <td>Slope Height</td>
        <td data-type="slope_height">${data['slope_height']}</td>
    </tr>
    <tr>
        <td>Rubber</td>
        <td data-type="slope_side">${data['slope_side_name']}</td>
    </tr>
`);
        table.append(slopeinfo);
    };
};

function failPopup(data) {
    /* Shows an Error Message and closes the Popup window */
    $("div.popup").remove();
    $(document).unbind("click.popup");
    showSnackbar({ alerttype: "warning", label: "Popup Error", text: `Failed to get Popup Data: ${data.responseText}` })
};

function setSprings(doorid) {
    /* Sends a request to the server to calculate the stats on the given door */

    window.location.href = `/doors/springs/${doorid}`;
};

function failUpdate(data) {
    /* Shows an Error Message when the Door fails to update */
    if (Math.floor(data.status / 100) == 5) {
        showSnackbar({ alertype: "warning", label: "Calculation Failure", text: `Failed to AutoCalculate Door: ${data.responseText}` });
    } else {
        showSnackbar({ alertype: "warning", label: "Calculation Failure", text: `Failed to AutoCalculate Door: ${data.status} ${data.statusText}` })
    }
};