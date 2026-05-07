import { getAPI } from "../api_handlers.js";

export async function updateExitData() {
    const tbody = $('#exitTableBody');
    const gamePk = tbody.data("game-id")
    const exitData = await getAPI(`/api/exit/list/${gamePk}/`);
    tbody.empty(); // Clear "Loading..." or old data

    const editHTML = $("#editHTML").html();
    const deleteHTML = $("#deleteHTML").html();

    exitData["exits"].forEach(item => {
        tbody.append(`
        <tr>
            <th>${item["room_1__name"]}</th>
            <th>${item["room_2__name"]}</th>
            <td>${item["is_locked"] ? "Yes" : "No"}</td>
            <td>
            <a href="/room/edit_exit/${gamePk}/${item["pk"]}/" style="text-decoration:none">
                ${editHTML}
            </a>
            <a class="delete-button" data-name="exit" href="/room/delete_exit/${item["pk"]}/" style="text-decoration:none">
                ${deleteHTML}
            </a>
            </td>
        </tr>
        `);
    });

    if ( exitData["exits"].length == 0 ) {
        tbody.append("<tr><th colspan=4>No exits have been added</th></tr>");
    }
}