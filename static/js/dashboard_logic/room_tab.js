import { postAPI } from "../api_handlers.js";



function showHideIsLocked(isLocked) {
    const $rows = $('.hideable-row');
    if (isLocked) {
        // Show only the rows that match the item-type attribute
        $rows.filter('[checkboxId="id_is_locked"]').show();
    } else {
        // Hide everything first
        $rows.hide();
    }
}

export function initCreateConnectionForm(updateExitData) {
    document.querySelectorAll("[data-room-pk]").forEach(function(button) {
        button.addEventListener("click", function() {
        const roomPk = this.getAttribute("data-room-pk");
        const roomName = this.getAttribute("data-room-name");

        $(".modalRoomName").text(roomName);

        $("#exitForm").on("submit", function(e) {
            e.preventDefault();

            const link = `/api/exit/add/${roomPk}/`
            const formDictionary = {};
            $.each($(this).serializeArray(), function(_, field) {
                formDictionary[field.name] = field.value;
            });

            postAPI(
                link,
                formDictionary,
                function(response) {
                    $("#exitFormModal").html("<p>Connection Created!</p>");
                    updateExitData();
                },
                function(response) {
                    $.each(response.responseJSON.errors, function(fieldName, messages) {
                    $.each(messages, function(_, message) {
                        $("#exitFormModal").append(
                        `<p style='color:#CC0000'>${message}</p>`
                        );
                    });
                    });
                }
            );

        });

        });
    });

    $(document).ready(function() {
        const isLocked = $('#id_is_locked').prop("checked");
        showHideIsLocked(isLocked);
        $('#id_is_locked').on('change', function() {
            isLocked = $(this).prop("checked");
            showHideIsLocked(isLocked);
        });
    });

}