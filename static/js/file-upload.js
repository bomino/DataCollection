

// static/js/file-upload.js

document.addEventListener('DOMContentLoaded', function () {
    const uploadSection = document.querySelector('.upload-section');
    if (!uploadSection) return; // Exit if not on upload page

    const fileInput = uploadSection.querySelector('input[type="file"]');
    if (!fileInput) return;

    // Handle drag and drop
    uploadSection.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadSection.classList.add('border-primary');
    });

    uploadSection.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadSection.classList.remove('border-primary');
    });

    uploadSection.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadSection.classList.remove('border-primary');

        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            // Trigger change event
            fileInput.dispatchEvent(new Event('change'));
        }
    });

    // Show selected filename
    fileInput.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name;
        if (fileName) {
            const fileNameDisplay = uploadSection.querySelector('h5');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
        }
    });
});