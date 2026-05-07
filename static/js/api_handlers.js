
export async function getAPI(api_url) {
    try {
        const response = await fetch(api_url);
        const data = await response.json();

        return data;
    } catch (error) {
        console.error("Failed to fetch:", error);
    }
}

export function postAPI(api_url, data, successFunc, errorFunc=null) {
    $.ajax({
        url: api_url,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        headers: { "X-CSRFToken": data["csrfmiddlewaretoken"] }, // Security!
        success: function(response) {
            // This is where you update the UI
            successFunc(response);
        },
        error: function(response) {
            if (errorFunc === null) {
                console.log(response);
            } else {
                errorFunc(response);
            }
        }
    });
}
