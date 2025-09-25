async function loadGroups() {
    //added console_debug for getting user group data from database
    //default = false
    //helps to identify problems with fetching data.
    
    const console_debug = false;
    try {
        if (console_debug) {
            console.log('Loading groups from API...');
        }

        const response = await fetch('/api/registration/groups');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const groups = await response.json();

        if (console_debug) {
            console.log('Groups received:', groups);
        }

        const select = document.querySelector('select[name="group"]');
        select.innerHTML = '<option value="" disabled selected>Choose your group</option>';

        groups.forEach(group => {
            const option = document.createElement('option');
            // Use lowercase for value to match DB, but nice display name
            option.value = group.name.toLowerCase();  // lowercase for DB match
            option.textContent = group.description || group.name;  // nice display
            if (console_debug) {
                console.log(`Adding option: value="${group.name.toLowerCase()}", text="${group.description}"`);
            }
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load groups:', error);
        const select = document.querySelector('select[name="group"]');
        select.innerHTML = '<option value="" disabled>Error loading groups</option>';
    }
}

document.addEventListener('DOMContentLoaded', loadGroups);