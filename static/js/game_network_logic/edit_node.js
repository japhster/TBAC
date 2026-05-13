import { getAPI, postAPI } from "../api_handlers.js";

// update form field values when room is selected to know what the current values are

async function updateNodeForm(nodeId) {
    const data = await getAPI(`/api/network/node/data/${nodeId}/`)
    $.each(data, function(fieldName, value) {
        $(`#id_${fieldName}`).val(value);
    });
}


export function editNode(data, callback) {
    $("#modalRoomName").text(data["label"]);
    updateNodeForm(data["id"]);
    $("#roomModal").modal("show");

    $("#roomForm").on("submit", function(e) {
        e.preventDefault();
        $('p.error-message').remove();
        const link = `/api/network/node/update/${data["id"]}/`

        const form = document.querySelector("#roomForm")
        const formData = new FormData(form);

        const formDictionary = Object.fromEntries(formData.entries());
 
        formDictionary["required_items"] = formData.getAll("required_items");

        postAPI(
            link,
            formDictionary,
            function(response) {
                data["label"] = response["room_name"];
                $("#roomModal").modal("hide");
            },
            function(response) {
                $.each(response.responseJSON.errors, function(fieldName, messages) {
                    $.each(messages, function(_, message) {
                        $(`#${fieldName}`).append(
                        `<p style='color:#CC0000' class='error-message'>${message}</p>`
                        );
                    });
                });
            }
        );
    });

    $("#roomModal").on("hide.bs.modal", function() { callback(data) })



}