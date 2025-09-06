
// Add any deadline management scripts here
document.addEventListener('DOMContentLoaded', function () {
    // Confirm before toggling deadlines
    const toggleForms = document.querySelectorAll('form[action*="toggle"]');
    toggleForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const button = form.querySelector('button');
            const action = button.textContent.trim();
            if (!confirm(`Are you sure you want to ${action.toLowerCase()} this deadline?`)) {
                e.preventDefault();
            }
        });
    });
});
