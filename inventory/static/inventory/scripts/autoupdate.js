function autoUpdate() {
    let $input = $(this);
    let itemid = $input.attr('data-itemid');
    let description = $input.attr('data-description');
    let attribute = $input.attr("data-attribute");
    let value = $input.val();
    let date = `${year}-${month}-1`;
    input = { itemid: itemid, date: date };
    input[attribute] = value;
    $.post('/inventory/api/item',
        input,
        function (data) {
            if (attribute == "quantity") {
                let quantity = data['object']['quantity'];
                if (quantity == null) {
                    quantity = "None";
                } else {
                    try { quantity = quantity.toFixed(2); }
                    catch { undefined; }   
                }
                $input.val(quantity);
            }
            showSnackbar({ type: "success", text: "Successfully updated " + description });
        },
        "json"
    ).fail(
        function (response) {
            let original = $input.attr('value');
            $input.val(original);
            showSnackbar({ type: "danger", label: "Failure!", text: "Failed to update " + description + " (" + response.status + "): Refresh the Webpage" });
        }
        );

};