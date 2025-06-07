document.addEventListener("DOMContentLoaded", function () {
    // Get references to all relevant DOM elements
    const apptNumberGroup = document.getElementById('apptNumberGroup');
    const formFields = document.getElementById('formFields');
    const apptForm = document.getElementById('apptForm');
    const createBtn = document.getElementById('createBtn');
    const editBtn = document.getElementById('editBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const descriptionLabel = document.getElementById('descriptionLabel');
    const descriptionField = document.getElementById('description');
    const actionRow = document.querySelector('.appointment-form .action-row');

    let currentAction = null; // Track which action is currently selected

    // Show the form fields and adjust which fields are visible based on the action
    function showForm(action) {
        formFields.style.display = 'block';
        currentAction = action;
        // For create: hide appointment number, show description
        if (action === 'create') {
            apptNumberGroup.style.display = 'none';
            document.getElementById('appt_number').removeAttribute('required');
            descriptionLabel.style.display = '';
            descriptionField.style.display = '';
        // For edit: show appointment number and description
        } else if (action === 'edit') {
            apptNumberGroup.style.display = 'block';
            document.getElementById('appt_number').setAttribute('required', 'required');
            descriptionLabel.style.display = '';
            descriptionField.style.display = '';
        // For delete: show appointment number, hide description
        } else if (action === 'delete') {
            apptNumberGroup.style.display = 'block';
            document.getElementById('appt_number').setAttribute('required', 'required');
            descriptionLabel.style.display = 'none';
            descriptionField.style.display = 'none';
        }
        // Switch buttons to horizontal
        if (actionRow) actionRow.classList.add('horizontal');
    }

    // Hide the form fields and reset the form
    function hideForm() {
        formFields.style.display = 'none';
        apptForm.reset();
        // Switch buttons back to vertical
        if (actionRow) actionRow.classList.remove('horizontal');
    }

    // Show the info panel with the appointment number
    function showCalendarPanel() {
    const calendarPanel = document.getElementById('calendarPanel');
    const infoPanel = document.getElementById('infoPanel');
    if (calendarPanel) calendarPanel.style.display = '';
    if (infoPanel) infoPanel.style.display = 'none';
    }

    // Show form for create action
    createBtn.addEventListener('click', function (e) {
        e.preventDefault();
        showCalendarPanel(); // Show calendar panel, hide any existing info panel
        showForm('create');
    });
    // Show form for edit action
    editBtn.addEventListener('click', function (e) {
        e.preventDefault();
        showCalendarPanel(); // Show calendar panel, hide any existing info panel
        showForm('edit');
    });
    // Show form for delete action
    deleteBtn.addEventListener('click', function (e) {
        e.preventDefault();
        showCalendarPanel(); // Show calendar panel, hide any existing info panel
        showForm('delete');
    });

    // When cancel is clicked, hide and reset the form, and revert buttons to vertical
    cancelBtn.addEventListener('click', function () {
        hideForm();
    });

    // Set the action before submit, let browser handle validation
    apptForm.addEventListener('submit', function (e) {
        document.getElementById('formAction').value = currentAction;
    });

    // Prevent accidental form submission when pressing Enter (except in textarea)
    apptForm.addEventListener('keydown', function (e) {
        if (e.key === "Enter" && e.target.tagName !== "TEXTAREA") {
            e.preventDefault();
        }
    });
});