
$(document).ready(function() {
    $('.delete-button').on('click', function(e) {
        // 1. Prevent the link from opening immediately
        e.preventDefault();
        // 2. Get the item name and the URL
        const itemName = $(this).data('name');
        const deleteUrl = $(this).attr('href');
        const customMessage = $(this).data('custom-message');

        // 3. Show the confirmation box
        const confirmed = confirm(
            customMessage === undefined ? "Are you sure you want to delete '" + itemName + "'? This cannot be undone." : customMessage
        );

        // 4. If they clicked 'OK', redirect them
        if (confirmed) {
            window.location.href = deleteUrl;
        }
    });
});
