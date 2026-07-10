// JavaScript для управления продуктами
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех Bootstrap компонентов
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Сортировка таблицы
    const tableHeaders = document.querySelectorAll('#productsTable th[data-sort]');
    tableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const column = this.getAttribute('data-sort');
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isAscending = this.classList.contains('sorted-asc');

            rows.sort((a, b) => {
                const cellA = a.querySelector(`td:nth-child(${this.cellIndex + 1})`).textContent;
                const cellB = b.querySelector(`td:nth-child(${this.cellIndex + 1})`).textContent;

                if (isNumeric(cellA) && isNumeric(cellB)) {
                    return (isAscending ? 1 : -1) * (parseFloat(cellA) - parseFloat(cellB));
                } else {
                    return (isAscending ? 1 : -1) * cellA.localeCompare(cellB, 'ru');
                }
            });

            rows.forEach(row => tbody.appendChild(row));
            this.classList.toggle('sorted-asc');
            this.classList.toggle('sorted-desc');
        });
    });

    // Проверка чисел
    function isNumeric(str) {
        return !isNaN(parseFloat(str));
    }
});

// Добавление компонента
function addComponent() {
    const type = document.getElementById('componentType').value;
    const componentId = document.getElementById('componentId').value;
    const quantity = document.getElementById('quantity').value;

    if (type && componentId && quantity) {
        // Логика добавления компонента
        console.log('Добавлен компонент:', { type, componentId, quantity });
    }
}

// Удаление компонента
function deleteComponent(componentId) {
    if (confirm('Вы уверены, что хотите удалить компонент?')) {
        // Логика удаления
        console.log('Удален компонент:', componentId);
    }
}

// Редактирование компонента
function editComponent(componentId) {
    // Логика редактирования
    console.log('Редактирование компонента:', componentId);
}

// Импорт из Excel
function importFromExcel() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.xlsx,.xls';

    input.onchange = e => {
        const file = e.target.files[0];
        if (file) {
            // Логика импорта
            console.log('Импортирован файл:', file.name);
        }
    };

    input.click();
}
