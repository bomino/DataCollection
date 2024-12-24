// static/js/generic-upload.js

class FileUploadManager {
    constructor() {
        this.dropzone = document.querySelector('.upload-dropzone');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.selectedFiles = document.querySelector('.selected-files');
        this.uploadForm = document.getElementById('uploadForm');
        this.uploadButton = document.getElementById('uploadButton');
        this.fileTypeSelect = document.getElementById('fileType');

        // File type configurations
        this.allowedTypes = {
            'excel': ['.xlsx', '.xls'],
            'csv': ['.csv'],
            'text': ['.txt'],
            'pdf': ['.pdf']
        };

        // File type icons
        this.fileIcons = {
            'xlsx': 'bi-file-earmark-excel',
            'xls': 'bi-file-earmark-excel',
            'csv': 'bi-file-earmark-spreadsheet',
            'txt': 'bi-file-earmark-text',
            'pdf': 'bi-file-earmark-pdf',
            'default': 'bi-file-earmark'
        };

        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Drag and drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropzone.addEventListener(eventName, this.preventDefaults.bind(this), false);
        });

        // Highlight dropzone
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropzone.addEventListener(eventName, this.highlight.bind(this), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropzone.addEventListener(eventName, this.unhighlight.bind(this), false);
        });

        // Handle file drop
        this.dropzone.addEventListener('drop', this.handleDrop.bind(this), false);

        // Handle file input change
        this.fileInput.addEventListener('change', () => {
            this.handleFiles(this.fileInput.files);
        });

        // Browse button click
        document.querySelector('.browse-btn').addEventListener('click', () => {
            this.fileInput.click();
        });

        // Form submission
        this.uploadForm.addEventListener('submit', this.handleSubmit.bind(this));

        // File type change
        this.fileTypeSelect.addEventListener('change', () => {
            this.updateFileInputAccept();
            this.validateExistingFiles();
        });
    }

    updateFileInputAccept() {
        const selectedType = this.fileTypeSelect.value;
        const allowedExtensions = this.allowedTypes[selectedType] || [];
        this.fileInput.accept = allowedExtensions.join(',');
    }

    validateExistingFiles() {
        // Clear file list if type changes and files are selected
        if (this.fileList.children.length > 0) {
            this.fileList.innerHTML = '';
            this.selectedFiles.classList.add('d-none');
            this.fileInput.value = '';
        }
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight() {
        this.dropzone.classList.add('drag-over');
    }

    unhighlight() {
        this.dropzone.classList.remove('drag-over');
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        this.handleFiles(files);
    }

    validateFile(file) {
        const selectedType = this.fileTypeSelect.value;
        if (!selectedType) {
            return { valid: false, error: 'Please select a file type first' };
        }

        if (file.size > this.maxFileSize) {
            return { valid: false, error: `File ${file.name} exceeds 10MB limit` };
        }

        const extension = '.' + file.name.split('.').pop().toLowerCase();
        const allowedExtensions = this.allowedTypes[selectedType] || [];

        if (!allowedExtensions.includes(extension)) {
            return {
                valid: false,
                error: `Invalid file type: ${file.name}. Allowed types: ${allowedExtensions.join(', ')}`
            };
        }

        return { valid: true };
    }

    handleFiles(files) {
        this.selectedFiles.classList.remove('d-none');
        this.fileList.innerHTML = '';
        let hasValidFiles = false;

        Array.from(files).forEach(file => {
            const validation = this.validateFile(file);
            if (validation.valid) {
                const item = this.createFileListItem(file);
                this.fileList.appendChild(item);
                hasValidFiles = true;
            } else {
                this.showMessage(validation.error, 'warning');
            }
        });

        if (!hasValidFiles) {
            this.selectedFiles.classList.add('d-none');
        }

        // Enable/disable upload button
        this.uploadButton.disabled = !hasValidFiles;
    }

    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        return this.fileIcons[extension] || this.fileIcons.default;
    }

    createFileListItem(file) {
        const item = document.createElement('div');
        item.className = 'list-group-item d-flex justify-content-between align-items-center';

        const fileInfo = document.createElement('div');
        const iconClass = this.getFileIcon(file.name);
        fileInfo.innerHTML = `
            <i class="bi ${iconClass} me-2"></i>
            <span>${file.name}</span>
            <small class="text-muted ms-2">(${this.formatFileSize(file.size)})</small>
        `;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.innerHTML = '<i class="bi bi-x"></i>';
        removeBtn.onclick = () => {
            item.remove();
            if (this.fileList.children.length === 0) {
                this.selectedFiles.classList.add('d-none');
                this.uploadButton.disabled = true;
            }
        };

        item.appendChild(fileInfo);
        item.appendChild(removeBtn);

        return item;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async handleSubmit(e) {
        e.preventDefault();
        this.uploadButton.disabled = true;
        this.uploadButton.innerHTML = '<i class="bi bi-arrow-repeat rotate-animation"></i> Uploading...';

        const formData = new FormData(this.uploadForm);

        try {
            const response = await fetch(this.uploadForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showMessage('Files uploaded successfully!', 'success');
                this.resetForm();
            } else if (result.status === 'partial') {
                this.showMessage('Some files were uploaded successfully, but there were errors:', 'warning');
                result.errors.forEach(error => this.showMessage(error, 'danger'));
            } else {
                result.errors.forEach(error => this.showMessage(error, 'danger'));
            }
        } catch (error) {
            this.showMessage('An error occurred during upload.', 'danger');
            console.error('Upload error:', error);
        } finally {
            this.uploadButton.disabled = false;
            this.uploadButton.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>Upload Files';
        }
    }

    showMessage(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="bi ${this.getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        this.uploadForm.insertAdjacentElement('beforebegin', alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'bi-check-circle',
            'danger': 'bi-exclamation-circle',
            'warning': 'bi-exclamation-triangle',
            'info': 'bi-info-circle'
        };
        return icons[type] || icons.info;
    }

    resetForm() {
        this.uploadForm.reset();
        this.fileList.innerHTML = '';
        this.selectedFiles.classList.add('d-none');
        this.uploadButton.disabled = false;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FileUploadManager();
});