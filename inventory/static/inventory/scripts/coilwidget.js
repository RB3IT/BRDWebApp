function COIL(inventorycoil) {
    let coil, onclick, disable;
    if (isInventoryCoil(inventorycoil)) {
        coil = inventorycoil.coil;
        onclick = "";
        disable = " disabled";
    }
    else {
        coil = inventorycoil;
        onclick = "addCoil(this);";
        disable = "";
    }

    return `<div class="coil" data-weight="${coil.weight}" data-width="${coil.width}" data-pk="${inventorycoil.pk}" data-coil-pk="${coil.pk}">
    <label><i class="material-icons cancel-button" onclick="removeCoil(this);"></i><i class="material-icons add-button${disable}" onclick="${onclick}"></i>${coil.pk} (${coil.size})</label>
    <label>Width<input name="width" class="autoblur" type="number" value="${inventorycoil.width}" step=".01" min="0.00"/></label>
    <label>Weight<input name="weight" type="number" min="0.00" value="${inventorycoil.weight}" disabled/></label>
</div>`;
}

function isInventoryCoil(coil) {
    return coil.coil !== undefined;
}

$(document).ready(getLoadCoils);

function getLoadCoils() {
    /* Queries the API for coils associated with the current Inventory Item (callback to loadCoils) */
    if (inventoryid === null) {
        return getInventoryID(getLoadCoils);
    }
    $.get("/inventory/coils/api/inventorycoils", { item:inventoryid }, loadCoils);
}

function clearGetLoadCoils() {
/* As getLoadCoils, but clears all the coils first */
    $("#coilcontainer .coil").remove();
    return getLoadCoils();
}

function loadCoils(data) {
    /* Loads the coils in a JSON response into the coils widget (creating their necessary elements; via loadCoil)*/
    let coilsdiv = $("#coilcontainer");
    let coilpks = [];
    coilsdiv.find(".coil").each((it, item) => coilpks.push($(item).attr("data-coil-pk")));
    for (let coil of data.coils) {
        if (coilpks.indexOf(String(coil.pk)) >= 0) continue;
        loadCoil(coil);
    }
    $('.coil input[name="width"]').change(calculateWeight);
}

function loadCoil(coil) {
    let coilsdiv = $("#coilcontainer");
    let div = $(COIL(coil));
    div.find(".autoblur").keypress(enterBlur);
    coilsdiv.append(div);
    return div;
}

function getOpenCoils() {
/* Queries the API for all open coils */
    let size;
    if (itemid.indexOf("528") >= 0) size = 5.28
    else if (itemid.indexOf("534") >= 0) size = 5.34;
    $.get("/inventory/coils/api/coils", { size: size }, loadCoils);
}

function removeCoil(cancelButton) {
/* Removes a coil from the Inventory item and DOM */
    let parent = $(cancelButton).parents("div.coil").first();
    let coilid = parent.attr("data-pk");
    $.ajax({ url: `/inventory/coils/api/inventorycoils/${coilid}`, method: "DELETE" });
    parent.remove();
}

function calculateWeight() {
    /* Crude Method for calculating weight of an opened coil
     * 
     * Divide original weight by the original width to get a weight/inch.
     * Multiply weight/inch by the current width.
     */
    // Get numbers
    let input = $(this);
    let currentWidth = parseFloat(input.val());
    let parent = input.parents("div.coil").first();
    let originalWeight = parseFloat(parent.attr("data-weight"));
    let originalWidth = parseFloat(parent.attr("data-width"));
    // Do math
    let weight = currentWidth * (originalWeight / originalWidth);
    // Set "weight" input (toggling disable off and back on)
    parent.find('input[name="weight"]').prop('disabled', false).val(weight).prop("disabled", true);
    // Enable save
    enableSave(parent);
}

function addToQuick() {
    /* Add all coils to the Quick Add */
    let coilsdiv = $("#coilcontainer");
    // Last autoCalc line
    let lastline = $(".autoaddline:last");
    // If last autoCalc line is empty, remove it
    // so that we don't get a blank in the middle
    if (!lastline.find("input.autoadd").val()) { lastline.remove(); }
    let coils = coilsdiv.find(".coil");
    // Add to quickadd
    coils.each(function (index, item) {
        let weight = $(item).find("input[name='weight']").first().val();
        addAutoCalcLine(weight);
    });
    // Save all coils at once to decrease backend load
    let output = [];
    coils.each(function (index, item) {
        let coil = $(item);
        let width, pk;
        pk = coil.attr("data-pk");
        width = coil.find("input[name='width']").first().val();
        output.push({ coil: pk, width: width });
    });
    console.log(output)
    $.post("/inventory/coils/api/inventorycoils/width", { coils: output });
    
    // Add new line
    autoCalcNewandSum();

}

function enableSave(coilWidget) {
    /* Removes .disabled and adds saveCoil callback to save icon */
    coilWidget = $(coilWidget);
    coilWidget.find(".add-button").removeClass("disabled").attr("onclick","saveCoil(this);");
}

function disableSave(coilWidget) {
    /* Adds .disabled and removes saveCoil callback from save icon */
    coilWidget = $(coilWidget);
    coilWidget.find(".add-button").addClass("disabled").attr("onclick", null);
}

function addCoil(addButton) {
/* Saves the coil as an InventoryCoil for the given Inventory item with the current width */
    if (inventoryid === null) {
        return getInventoryID(function () { addCoil(addButton); });
    }
    let parent = $(addButton).parents("div.coil").first();
    let coilid = parent.attr("data-pk");
    $.post("/inventory/coils/api/inventorycoils/coil", { item: inventoryid, coil: coilid }, function (data) {
        // After saving coil, update pk and width
        parent.attr("data-pk", data.coil.pk);
        saveCoil(addButton);
    });
}

function saveCoil(addButton) {
/* Saves the coil's current size via the API */
    if (inventoryid === null) {
        return getInventoryID(function () { saveCoil(addButton); });
    }
    let parent = $(addButton).parents("div.coil").first();
    let coilid = parent.attr("data-pk");
    let width = parent.find("input[name='width']").val();
    $.post("/inventory/coils/api/inventorycoils/width", { coil: coilid, width: width },
        function (data) {
            if (data.success) disableSave(parent);
        });
}

function getAddCoil(addButton) {
/* Add a Coil (by ID) to the current Inventory */
    console.log(">>>", inventoryid)
    if (inventoryid === null) {
        return getInventoryID(function () { getAddCoil(addButton); });
    }
    let coilinput = $(addButton).siblings("input[name='coilid']");
    let coilid = coilinput.val();
    if (!coilid) return showSnackbar({ type: "danger", label: "No ID", text: "Please input Coil ID" });
    $.post("/inventory/coils/api/inventorycoils/coil", {item: inventoryid,coil:coilid},
        function (data) {
            getCoil(data.coil.pk);
        });
}

function getCoil(inventorycoil) {
/* Queries the API for an Inventory Coil (by PK) and forwards to loadCoil */
    $.get(`/inventory/coils/api/inventorycoils/${inventorycoil}`, function (data) {
        return loadCoil(data.coil);
    });
}


function getInventoryID(callback) {
/* Retrieves the inventoryid, creating a new Inventory item if necessary, and then calls the callback */
    $.get(`/inventory/api/item/${itemid}/${date}`, function (data) {
        console.log(data)
        inventoryid = data.object.pk;
        return callback();
    }).fail(function () { // Failure is assumed to be "object already exists" #lazy
        $.post(`/inventory/api/item/${itemid}/${date}`, function () {
            inventoryid = data.object.pk;
            return callback();
        });
    });
}