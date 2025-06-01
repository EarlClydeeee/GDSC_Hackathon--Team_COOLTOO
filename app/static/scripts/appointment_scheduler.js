document.addEventListener("DOMContentLoaded", function () {
    // Get references to all relevant DOM elements
    const apptNumberGroup = document.getElementById('apptNumberGroup');
    const formFields = document.getElementById('formFields');
    const apptForm = document.getElementById('apptForm');
    const createBtn = document.getElementById('createBtn');
    const editBtn = document.getElementById('editBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    const submitBtn = document.getElementById('submitBtn');
    const confirmBtn = document.getElementById('confirmBtn');
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
            descriptionLabel.style.display = '';
            descriptionField.style.display = '';
        // For edit: show appointment number and description
        } else if (action === 'edit') {
            apptNumberGroup.style.display = 'block';
            descriptionLabel.style.display = '';
            descriptionField.style.display = '';
        // For delete: show appointment number, hide description
        } else if (action === 'delete') {
            apptNumberGroup.style.display = 'block';
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

    // Show form for create action
    createBtn.addEventListener('click', function (e) {
        e.preventDefault();
        showForm('create');
    });
    // Show form for edit action
    editBtn.addEventListener('click', function (e) {
        e.preventDefault();
        showForm('edit');
    });
    // Show form for delete action
    deleteBtn.addEventListener('click', function (e) {
        e.preventDefault();
        showForm('delete');
    });

    // When confirm is clicked, set the action and submit the form
    confirmBtn.addEventListener('click', function () {
        document.getElementById('formAction').value = currentAction; // Set the action
        apptForm.submit(); // Submit the form
    });

    // When cancel is clicked, hide and reset the form, and revert buttons to vertical
    cancelBtn.addEventListener('click', function () {
        hideForm();
    });

    // Prevent accidental form submission when pressing Enter (except in textarea)
    apptForm.addEventListener('keydown', function (e) {
        if (e.key === "Enter" && e.target.tagName !== "TEXTAREA") {
            e.preventDefault();
        }
    });
});

// Toggle the buttons on Appointment Scheduler section
document.addEventListener('DOMContentLoaded', function() {
    const actionRow = document.querySelector('.appointment-form .action-row');
    if (!actionRow) return;
    actionRow.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', function() {
            actionRow.classList.add('horizontal');
        });
    });
});

// When cancel is clicked, hide and reset the form, and revert buttons to vertical
cancelBtn.addEventListener('click', function () {
    hideForm();
    // Remove horizontal class to stack buttons vertically again
    const actionRow = document.querySelector('.appointment-form .action-row');
    if (actionRow) {
        actionRow.classList.remove('horizontal');
    }
});