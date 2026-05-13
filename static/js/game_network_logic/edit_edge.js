import { getAPI, postAPI } from "../api_handlers.js";
import { showHideRelevantRows } from "../table_logic.js";

// update form field values when edge is selected to know what the current values are

async function updateEdgeForm(edgeId) {
    const data = await getAPI(`/api/network/edge/data/${edgeId}/`)
    $.each(data, function(fieldName, value) {
        if (fieldName == "room_1_name" || fieldName == "room_2_name") {
            $(`.${fieldName}`).text(value);
        } else if (fieldName == "is_locked") {
            $("#id_is_locked").prop("checked", value);
        } else {
            $(`#id_${fieldName}`).val(value);
        }
    });

    showHideRelevantRows(data["is_locked"], "id_is_locked");
    $("#id_is_locked").off("change").on("change", function() {
        const isLocked = $(this).prop("checked");
        showHideRelevantRows(isLocked, "id_is_locked");
    });

}



export function editEdge(data, callback) {
    $("#modalEdgeName").text(data["label"]);
    updateEdgeForm(data["id"]);
    $("#edgeModal").modal("show");

    $("#edgeForm").off("submit").on("submit", function(e) {
        e.preventDefault();
        $('p.error-message').remove();
        const link = `/api/network/edge/update/${data["id"]}/`

        const form = document.querySelector("#edgeForm")
        const formData = new FormData(form);

        const formDictionary = Object.fromEntries(formData.entries());

        postAPI(
            link,
            formDictionary,
            function(response) {
                data["dashes"] = formDictionary.is_locked !== undefined;
                $("#edgeModal").modal("hide");
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

    $("#edgeModal").off("hide.bs.modal").on("hide.bs.modal", function() { callback(data) })



}