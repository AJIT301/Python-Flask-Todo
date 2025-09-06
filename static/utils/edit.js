
function toggleEditTermInputs() {
    var checkbox = document.getElementById('edit-term-checkbox');
    var termInputs = document.getElementById('edit-term-inputs');
    termInputs.classList.toggle('hidden', !checkbox.checked);
}
