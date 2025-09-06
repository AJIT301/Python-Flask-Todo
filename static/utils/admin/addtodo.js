
    document.addEventListener("DOMContentLoaded", () => {
    const checkbox = document.getElementById("select-term-checkbox");
    const termInputs = document.getElementById("term-inputs");
    checkbox.addEventListener("change", () => {
        termInputs.style.display = checkbox.checked ? "block" : "none";
    });
});
    function toggleTermInputs() {
        const checkbox = document.getElementById("select-term-checkbox");
        const termInputs = document.getElementById("term-inputs");
        termInputs.style.display = checkbox.checked ? "block" : "none";
    }

    /* Custom dropdown functionality */
    document.querySelectorAll('.custom-select').forEach(select => {
        const selected = select.querySelector('.selected');
        const options = select.querySelectorAll('li');
        const hiddenInput = select.nextElementSibling; // hidden input to submit value

        selected.addEventListener('click', () => {
            select.classList.toggle('open');
        });

        options.forEach(option => {
            option.addEventListener('click', () => {
                selected.textContent = option.textContent;
                hiddenInput.value = option.dataset.value;
                select.classList.remove('open');
            });
        });
    });

    // Close dropdown if clicked outside
    document.addEventListener('click', e => {
        document.querySelectorAll('.custom-select').forEach(select => {
            if (!select.contains(e.target)) {
                select.classList.remove('open');
            }
        });
    });
    
