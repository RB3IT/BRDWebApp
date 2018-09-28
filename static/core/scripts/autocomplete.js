
function autoCompleteAjax(event) {
    /* Makes the Ajax call to update the inputWidget */ 
    let val = event.target.value;
    let key = $(event.target).attr("data-api");
    let data = {};
    data[key] = val;
    $.post({
        url: "/api/company",
        method: "GET",
        data: data,
        success: function (data) { updateWidget(event.target, data) }
    });
};

function updateWidget(element,data) {
    /* The success function for autoCompleteAjax which updates the widget with new options */
    if (data.success != true) { return; };
    let ele = $(element);
    let _list = ele.attr("list");
    datalist = ele.siblings(`datalist#${_list}`);
    datalist.empty()
    for (let option of data.results) {
        let id,value
        [id,value] = option;
        datalist.append($(`<option value=${value} data-id=${id} />`))
    };
};