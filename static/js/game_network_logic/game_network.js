import { getAPI, postAPI } from "../api_handlers.js";
import { editNode } from "./edit_node.js";
import { editEdge } from "./edit_edge.js";

function getGamePk() {
    return $("#gameNetwork").data("game-pk");
}

function addNode(nodeData, callback) {
    postAPI(
        `/api/network/node/add/${getGamePk()}/`,
        {"name": nodeData["label"]},
        (response) => {
            nodeData["id"] = response["room_id"];
            callback(nodeData);
        },
    );
}

function addEdge(edgeData, callback) {
    postAPI(
        `/api/network/edge/add/${getGamePk()}/`, 
        {
            "from_room": edgeData["from"],
            "to_room": edgeData["to"],
        },
        (response) => {
            edgeData["id"] = response["exit_id"];
            callback(edgeData);
        },
    );
    ;
}

function deleteNode(deleteData, callback) {
    postAPI(
        `/api/network/node/delete/${deleteData["nodes"][0]}/`,
        {},
        (response) => {callback(deleteData)},
    );
}

function deleteEdge(deleteData, callback) {
    postAPI(
        `/api/network/edge/delete/${deleteData["edges"][0]}/`,
        {},
        (response) => {callback(deleteData)}
    );
}

async function createNetwork(gamePk) {
    const networkData = await getAPI(`/api/network/data/${gamePk}/`);

    var nodes = new vis.DataSet(networkData["nodes"]);

    // create an array with edges
    var edges = new vis.DataSet(networkData["edges"]);

    // create a network
    var container = document.getElementById("gameNetwork");
    var data = {
        nodes: nodes,
        edges: edges,
    };
    var options = {
        "layout": {"randomSeed": 3.14},
        "manipulation": {
            "enabled": true,
            "addNode": addNode,
            "addEdge": addEdge,
            "editNode": editNode,
            "editEdge": {"editWithoutDrag": editEdge},
            "deleteNode": deleteNode,
            "deleteEdge": deleteEdge,
        }};
    var network = new vis.Network(container, data, options);

    network.on("doubleClick", function(params) {
        if (params["nodes"]) {
            window.location.href = `/room/detail/${params["nodes"][0]}/`;
        }
    });
}


$(document).ready(function() {
    createNetwork(getGamePk());
});