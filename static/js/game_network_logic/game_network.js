import { getAPI, postAPI } from "../api_handlers.js";

function getGamePk() {
    return $("#gameNetwork").data("game-pk");
}

function addNode(nodeData, callback) {
    postAPI(
        `/api/network/add_node/${getGamePk()}/`,
        {"name": nodeData["label"]},
        (response) => {
            nodeData["id"] = response["room_id"];
            callback(nodeData);
        },
    );
}

function addEdge(edgeData, callback) {
    postAPI(
        `/api/network/add_edge/${getGamePk()}/`, 
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
        `/api/network/delete_node/${deleteData["nodes"][0]}/`,
        {},
        (response) => {callback(deleteData)},
    );
}

function deleteEdge(deleteData, callback) {
    postAPI(
        `/api/network/delete_edge/${deleteData["edges"][0]}/`,
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
        "manipulation": {
            "enabled": true,
            "addNode": addNode,
            "addEdge": addEdge,
            "deleteNode": deleteNode,
            "deleteEdge": deleteEdge,
        }};
    var network = new vis.Network(container, data, options);
}


$(document).ready(function() {
    createNetwork(getGamePk());
});