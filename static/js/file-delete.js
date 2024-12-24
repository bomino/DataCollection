// static/js/file-delete.js

let currentFileId = null;
let deleteModal = null;

document.addEventListener('DOMContentLoaded', function () {
    // Initialize the modal
    deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));

    // Add click handler for confirm delete button
    document.getElementById('confirmDeleteBtn').addEventListener('click', function () {
        deleteFile();
    });
});

function confirmDelete(fileId, filename) {
    currentFileId = fileId;
    document.getElementById('filename-to-delete').textContent = filename;
    deleteModal.show();
}

function deleteFile() {
    if (!currentFileId) return;

    // Get CSRF token from the form
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/delete-upload/${currentFileId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'  // Important for CSRF
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Hide modal
                deleteModal.hide();
                // Reload page to show updated list
                window.location.reload();
            } else {
                alert('Error deleting file: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting file: ' + error.message);
        })
        .finally(() => {
            currentFileId = null;
        });
}