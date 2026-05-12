
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
    const csrfToken = $("meta[name='csrf-token']").attr("content");
    $.ajax({
        url: api_url,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        headers: { "X-CSRFToken": csrfToken ? csrfToken : data["csrfmiddlewaretoken"] }, // Security!
        success: function(response) {
            // This is where you update the UI
            if (successFunc) { successFunc(response) };
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
