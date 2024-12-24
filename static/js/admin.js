// static/js/admin.js

document.addEventListener('DOMContentLoaded', function () {
    // Add responsive classes to tables
    const tables = document.querySelectorAll('#content table');
    tables.forEach(table => {
        table.classList.add('table', 'table-hover');
    });

    // Enhanced filtering
    const filterSelects = document.querySelectorAll('.actions select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.value) {
                const confirmMessage = `Are you sure you want to ${selectedOption.text.toLowerCase()} the selected items?`;
                if (!confirm(confirmMessage)) {
                    this.selectedIndex = 0;
                }
            }
        });
    });

    // Add tooltips to action buttons
    const actionButtons = document.querySelectorAll('.button');
    actionButtons.forEach(button => {
        button.title = button.innerText;
    });

    // Enhance date picker
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.classList.add('vDateField');
    });

    // Add row highlighting
    const dataRows = document.querySelectorAll('tr[class^="row"]');
    dataRows.forEach(row => {
        row.addEventListener('mouseover', function () {
            this.style.backgroundColor = '#f0f4f8';
        });
        row.addEventListener('mouseout', function () {
            this.style.backgroundColor = '';
        });
    });
});