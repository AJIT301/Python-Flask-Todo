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
// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('deadlineModal');
    if (event.target == modal) {
        closeDeadlineModal();
    }
}

// Close modal with Escape key
document.onkeydown = function (evt) {
    evt = evt || window.event;
    var isEscape = false;
    if ("key" in evt) {
        isEscape = (evt.key === "Escape" || evt.key === "Esc");
    } else {
        isEscape = (evt.keyCode === 27);
    }
    if (isEscape) {
        closeDeadlineModal();
    }
};