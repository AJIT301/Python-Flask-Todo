
(function () {
    'use strict';

    function initDeadlineForm() {
        // Set default deadline date to tomorrow at 5 PM
        const deadlineInput = document.getElementById('deadline_date');
        if (deadlineInput && !deadlineInput.value) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(17, 0, 0, 0);

            const year = tomorrow.getFullYear();
            const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
            const day = String(tomorrow.getDate()).padStart(2, '0');
            const hours = String(tomorrow.getHours()).padStart(2, '0');
            const minutes = String(tomorrow.getMinutes()).padStart(2, '0');

            deadlineInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
        }

        // Get form elements
        const assignIndividual = document.getElementById('assign_individual');
        const assignGroup = document.getElementById('assign_group');
        const assignEveryone = document.getElementById('assign_everyone');
        const assignmentSelects = document.getElementById('assignment-selects');
        const individualSelect = document.getElementById('individual-select');
        const groupSelect = document.getElementById('group-select');
        const usersSelect = document.getElementById('selected_users');
        const groupsSelect = document.getElementById('selected_groups');

        if (!assignIndividual || !assignGroup || !assignEveryone) {
            console.error('Assignment checkboxes not found');
            return;
        }

        // Load users from API
        function loadUsers() {
            fetch('/admin/api/users')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to fetch users');
                    return response.json();
                })
                .then(users => {
                    usersSelect.innerHTML = '';

                    if (users.length === 0) {
                        usersSelect.innerHTML = '<option disabled>No users available</option>';
                        return;
                    }

                    users.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.id;
                        option.textContent = `${user.username} (${user.email})`;
                        usersSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error loading users:', error);
                    usersSelect.innerHTML = '<option disabled>Error loading users</option>';
                });
        }

        // Load groups from API
        function loadGroups() {
            fetch('/admin/api/groups')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to fetch groups');
                    return response.json();
                })
                .then(groups => {
                    groupsSelect.innerHTML = '';

                    if (groups.length === 0) {
                        groupsSelect.innerHTML = '<option disabled>No groups available</option>';
                        return;
                    }

                    groups.forEach(group => {
                        const option = document.createElement('option');
                        option.value = group.id;
                        option.textContent = `${group.name} - ${group.description}`;
                        groupsSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error loading groups:', error);
                    groupsSelect.innerHTML = '<option disabled>Error loading groups</option>';
                });
        }

        // Update form display based on selections
        function updateAssignmentDisplay() {
            // If "Everyone" is selected, hide other options
            if (assignEveryone.checked) {
                assignmentSelects.style.display = 'none';
                assignIndividual.checked = false;
                assignGroup.checked = false;
                return;
            }

            // If "Everyone" is unchecked and others are selected, uncheck "Everyone"
            if ((assignIndividual.checked || assignGroup.checked) && assignEveryone.checked) {
                assignEveryone.checked = false;
            }

            // Show/hide assignment selects container
            const showContainer = assignIndividual.checked || assignGroup.checked;
            assignmentSelects.style.display = showContainer ? 'block' : 'none';

            // Handle individual users section
            if (assignIndividual.checked) {
                individualSelect.style.display = 'block';
                loadUsers(); // Load fresh user data
            } else {
                individualSelect.style.display = 'none';
            }

            // Handle groups section
            if (assignGroup.checked) {
                groupSelect.style.display = 'block';
                loadGroups(); // Load fresh group data
            } else {
                groupSelect.style.display = 'none';
            }
        }

        // Add event listeners to checkboxes
        assignIndividual.addEventListener('change', updateAssignmentDisplay);
        assignGroup.addEventListener('change', updateAssignmentDisplay);
        assignEveryone.addEventListener('change', updateAssignmentDisplay);

        // Initialize form state
        updateAssignmentDisplay();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDeadlineForm);
    } else {
        initDeadlineForm();
    }
})();