function toggleTermInputs() {
    var checkbox = document.getElementById('select-term-checkbox');
    var termInputs = document.getElementById('term-inputs');
    termInputs.style.display = checkbox.checked ? 'block' : 'none';
}

function openDeadlineModal(deadlineId, title, description, dueDate, createdBy) {
    const modal = document.getElementById('deadlineModal');
    const modalTitle = document.getElementById('modalDeadlineTitle');
    const modalContent = document.getElementById('modalDeadlineContent');

    modalTitle.textContent = title;
    modalContent.innerHTML = `
        <p><strong>Description:</strong> ${description || 'No description provided'}</p>
        <p><strong>Due Date:</strong> ${dueDate}</p>
        <p><strong>Created by:</strong> ${createdBy}</p>
        <p><strong>Deadline ID:</strong> ${deadlineId}</p>
    `;

    modal.classList.add('show');
    document.body.style.overflow = 'hidden'; // prevent scroll
}


function closeDeadlineModal() {
    const modal = document.getElementById('deadlineModal');
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Modal close button
    const closeBtn = document.querySelector('.close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeDeadlineModal);
    }

    // Modal footer close button
    const footerCloseBtn = document.querySelector('.deadline-modal-footer .btn-secondary');
    if (footerCloseBtn) {
        footerCloseBtn.addEventListener('click', closeDeadlineModal);
    }

    // Deadline inspect buttons
    document.querySelectorAll('.inspect-deadline-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const deadlineId = this.dataset.deadlineId;
            const title = this.dataset.title;
            const description = this.dataset.description;
            const dueDate = this.dataset.dueDate;
            const createdBy = this.dataset.createdBy;
            openDeadlineModal(deadlineId, title, description, dueDate, createdBy);
        });
    });

    // Delete confirmation links
    document.querySelectorAll('.delete-confirm').forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure?')) {
                e.preventDefault();
                return false;
            }
            // If confirmed, submit the parent form
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // Term inputs toggle
    const termCheckbox = document.getElementById('select-term-checkbox');
    if (termCheckbox) {
        termCheckbox.addEventListener('change', toggleTermInputs);
    }

    // Todo checkboxes - submit form when changed
    document.querySelectorAll('input[type="checkbox"][name="done"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });
});

// Close modal when clicking outside
window.addEventListener('click', function (event) {
    const modal = document.getElementById('deadlineModal');
    if (event.target == modal) {
        closeDeadlineModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function (evt) {
    var isEscape = false;
    if ("key" in evt) {
        isEscape = (evt.key === "Escape" || evt.key === "Esc");
    } else {
        isEscape = (evt.keyCode === 27);
    }
    if (isEscape) {
        closeDeadlineModal();
    }
});
