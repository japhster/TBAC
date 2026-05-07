import { updateExitData } from "./exit_tab.js";
import { initCreateConnectionForm } from "./room_tab.js";


$(document).ready(() => {
    updateExitData()
    initCreateConnectionForm(updateExitData);
});