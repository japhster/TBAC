import { getAPI, postAPI } from "./api_handlers.js";

async function updateEnemyTable() {
    const tbody = $("#enemyTableData");
    const sessionPk = tbody.data("session-pk");
    const data = await getAPI(`/api/play/fight/enemies/${sessionPk}/`);
    tbody.empty();
    data["enemies"].forEach(enemy => {
        tbody.append(`
            <tr>
                <th>${ enemy.name }:</th>
                <td>
                    <div class="progress">
                    <div
                        class="progress-bar bg-success"
                        role="progressbar"
                        style="width: ${ enemy.health_bar_percentage }%;"
                        aria-valuenow="${ enemy.current_health }"
                        aria-valuemin="0"
                        aria-valuemax="${ enemy.max_health }"
                    >
                        ${ enemy.current_health }hp
                    </div>
                    </div>
                </td>
                <td class="text-center">
                    <button
                    class="btn btn-sm btn-danger attack-button"
                    data-toggle="modal"
                    data-target="#attackModal"
                    data-attack-url="/api/play/fight/${sessionPk}/${enemy.pk}/0/"
                    data-enemy-pk="${ enemy.pk }"
                    data-enemy-name="${ enemy.name }"
                    data-enemy-description="${ enemy.description }"
                    >
                        Attack
                    </button>
                </td>
            </tr>
        `);
    });
}

async function updatePlayerTable() {
    const sessionPk = $("#enemyTableData").data("session-pk");
    const data = await getAPI(`/api/play/fight/player/${sessionPk}/`);
    const player = data["player"];
    $("#playerHealth").text(`${player["current_health"]}hp`);
    const healthBar = $("#playerHealthBar")
    healthBar.width(`${player["health_bar_percentage"]}%`);
    healthBar.attr("aria-valuenow", player["health_bar_percentage"]);
    healthBar.attr("aria-valuemax", player["max_health"]);
    if (player["current_health"] <= 20) {
        healthBar.addClass("bg-danger");
        healthBar.removeClass("bg-success");
    } else {
        healthBar.removeClass("bg-danger");
        healthBar.addClass("bg-success");
    }
}

async function performAttackRound(enemyPk, attackPk) {
    postAPI(
        $("#enemyTableData").data("attack-url"),
        {"enemy": enemyPk, "attack_pk": attackPk},
        function(data) {
            $("#attackModal").modal("hide");
            if (data["remaining_enemies_count"] == 0 || data["player_is_dead"]) {
                window.location.href = $("#finishURL").data("finish-url");
            }
            updateEnemyTable();
            updatePlayerTable();
        },
    );
}


$(document).ready(() => {
    updateEnemyTable();
    updatePlayerTable();
    const attackUrlTemplate = $(".enemyTableData").data("attack-url");
    $(".attack-link").each(function() {
        const attackPk = $(this).data("attack-pk");
        $(this).on("click", function(e) {
            e.preventDefault();
            performAttackRound(
                $(this).data("enemy-pk"),
                $(this).data("attack-pk"),
            );
        });
    });
    $(document).on("click", ".attack-button", function(event) {
        event.preventDefault();
        const button = event.target;
        const enemyName = $(button).data("enemy-name");
        const enemyDescription = $(button).data("enemy-description");

        $("#modalEnemyName").text(enemyName);
        $("#modalEnemyDescription").text(enemyDescription);
        $(".attack-link").each(function() {
            $(this).data("enemy-pk", $(button).data("enemy-pk"))
        });

    });
})
