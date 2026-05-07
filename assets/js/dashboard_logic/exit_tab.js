import { getAPI } from "../api_handlers.js";

export async function updateExitData() {
    const tbody = $('#exitTableBody');
    const exitData = await getAPI(`/api/exit/list/${tbody.data("game-id")}/`);
    tbody.empty(); // Clear "Loading..." or old data

    exitData["exits"].forEach(item => {
        tbody.append(`
        <tr>
            <th>${item["room_1__name"]}</th>
            <th>${item["room_2__name"]}</th>
            <td>${item["is_locked"] ? "Yes" : "No"}</td>
            <td>
            <a href="/room/edit_exit/{{game.pk}}/${item["pk"]}/" style="text-decoration:none">
                {% static "icons/edit.html" %}
            </a>
            <a class="delete-button" data-name="exit" href="/room/delete_exit/${item["pk"]}/" style="text-decoration:none">
                {% static "icons/delete.html" %}
            </a>
            </td>
        </tr>
        `);
    });
}