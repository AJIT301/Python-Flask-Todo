
// Optional: Add any interactive features for group management
document.addEventListener('DOMContentLoaded', function () {
    // Add expand/collapse functionality for groups
    const groupHeaders = document.querySelectorAll('.group-header');
    groupHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function () {
            const groupCard = this.closest('.group-card');
            const membersList = groupCard.querySelector('.group-members');
            membersList.classList.toggle('collapsed');
        });
    });
});
