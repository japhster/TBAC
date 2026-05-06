
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function getAPI(api_url) {
    try {
        const response = await fetch(api_url);
        const data = await response.json();

        return data;
    } catch (error) {
        console.error("Failed to fetch:", error);
    }
}

function postAPI(api_url, data) {
    $.ajax({
        url: api_url,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        headers: { "X-CSRFToken": getCookie('csrftoken') }, // Security!
        success: function(response) {
            // This is where you update the UI
            alert("update success!");
        },
        error: function(error) {
            console.log("Error:", error);
        }
    });
}
