
export function showHideRelevantRows(show, checkboxId) {
    const $rows = $('.hideable-row');
    if (show) {
        // Show only the rows that match the item-type attribute
        $rows.filter(`[checkboxId="${checkboxId}"]`).show();
    } else {
        // Hide everything first
        $rows.hide();
    }
}