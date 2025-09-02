function sendHeartbeat() {
    // Only run if user is authenticated and page has focus
    if (document.body.dataset.userAuthenticated === "true" && document.hasFocus()) {
        // Get the CSRF token from the meta tag
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch('/api/heartbeat', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken // <-- Add the CSRF token here
            }
            // body: JSON.stringify({...}) // Add if you need to send data
        })
            .then(response => {
                if (response.status === 204) {
                    console.log("Heartbeat successful");
                    // Handle success
                } else if (response.status === 401) {
                    console.log("Heartbeat failed: Unauthorized");
                    // Handle not logged in
                } else {
                    console.log("Heartbeat failed: Unexpected status", response.status);
                    // Handle other potential HTTP errors
                }
            })
            .catch(function (error) {
                console.log('Heartbeat network error:', error);
            });
    }
}
// Send heartbeat immediately when page loads (if conditions are met)
sendHeartbeat();
// Then set interval for every 30 seconds
setInterval(sendHeartbeat, 30000);