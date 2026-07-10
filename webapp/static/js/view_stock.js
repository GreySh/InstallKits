// JavaScript для просмотра остатков
document.addEventListener('DOMContentLoaded', function() {
    const dispatchModalDialog = document.getElementById('dispatchModalDialog');
    if (dispatchModalDialog) {
        dispatchModalDialog.addEventListener('show.bs.modal', function() {
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('dispatchDate').value = today;
            document.getElementById('dispatchDialogProduct').value = '';
            document.getElementById('dispatchDialogQuantity').value = '';
        });
    }
});

function dispatchBatch() {
    const inputs = document.querySelectorAll('.dispatch-qty-input');
    const items = [];
    const summary = [];

    for (const input of inputs) {
        const quantity = parseInt(input.value, 10);
        if (!quantity || quantity <= 0) {
            continue;
        }

        const productId = parseInt(input.dataset.productId, 10);
        const productName = input.dataset.productName;
        const available = parseInt(input.dataset.available, 10);

        if (quantity > available) {
            alert(`Для продукта "${productName}" указано ${quantity}, доступно только ${available}`);
            return;
        }

        items.push({ product_id: productId, quantity });
        summary.push(`${productName}: ${quantity} шт.`);
    }

    if (items.length === 0) {
        alert('Укажите количество для списания хотя бы по одному продукту');
        return;
    }

    if (!confirm(`Списать комплекты?\n\n${summary.join('\n')}`)) {
        return;
    }

    fetch('/dispatch-batch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(items)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.messages.join('\n'));
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка при списании');
    });
}

// Экспорт в Excel
function exportToExcel() {
    // Получаем данные из таблицы
    const data = {
        products: [],
        discs: [],
        boxes: []
    };
    
    // Сбор данных продуктов
    const stockTable = document.getElementById('stockTable');
    if (stockTable) {
        const productRows = stockTable.querySelectorAll('tbody tr');
        productRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                data.products.push({
                    name: cells[0].textContent.trim(),
                    available: cells[1].textContent.trim()
                });
            }
        });
    }
    
    // Сбор данных носителей
    const discsTable = document.getElementById('discsStockTable');
    if (discsTable) {
        const discRows = discsTable.querySelectorAll('tbody tr');
        discRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                data.discs.push({
                    name: cells[0].textContent.trim(),
                    quantity: cells[1].textContent.trim()
                });
            }
        });
    }
    
    // Сбор данных коробок
    const boxesTable = document.getElementById('boxesStockTable');
    if (boxesTable) {
        const boxRows = boxesTable.querySelectorAll('tbody tr');
        boxRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                data.boxes.push({
                    name: cells[0].textContent.trim(),
                    quantity: cells[1].textContent.trim()
                });
            }
        });
    }
    
    // Отправляем данные на сервер для создания Excel
    fetch('/export-stock-to-excel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.blob())
    .then(blob => {
        // Создаем ссылку для скачивания
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'остатки_' + new Date().toISOString().split('T')[0] + '.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    })
    .catch(error => console.error('Ошибка при экспорте:', error));
}

// Генерация данных для Excel
function generateExcelData() {
    let csv = 'БУХГАЛТЕРСКИЙ БАЛАНС;\n';
    csv += 'Остатки на ' + new Date().toLocaleDateString('ru-RU') + ';\n\n';
    
    // Таблица продуктов
    csv += 'Остатки по продуктам;;\n';
    csv += 'Продукт;Доступно;Носителей;Коробок;\n';
    
    const stockTable = document.getElementById('stockTable');
    if (stockTable) {
        const productRows = stockTable.querySelectorAll('tbody tr');
        productRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 4) {
                csv += cells[0].textContent + ';' + cells[1].textContent + ';' + cells[2].textContent + ';' + cells[3].textContent + ';\n';
            }
        });
    }
    
    csv += '\nОстатки носителей;;\n';
    csv += 'Название;Количество;\n';
    
    const discsTable = document.getElementById('discsStockTable');
    if (discsTable) {
        const discRows = discsTable.querySelectorAll('tbody tr');
        discRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                csv += cells[0].textContent + ';' + cells[1].textContent + ';\n';
            }
        });
    }
    
    csv += '\nОстатки коробок;;\n';
    csv += 'Название;Количество;\n';
    
    const boxesTable = document.getElementById('boxesStockTable');
    if (boxesTable) {
        const boxRows = boxesTable.querySelectorAll('tbody tr');
        boxRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                csv += cells[0].textContent + ';' + cells[1].textContent + ';\n';
            }
        });
    }
    
    return csv;
}

// Фильтрация по продукту
function filterByProduct(productId) {
    // Логика фильтрации
    console.log('Фильтр по продукту:', productId);
}

// Печать отчета
function printStock() {
    window.print();
}

// Печать отчета (альтернативная функция)
function printReport() {
    window.print();
}

// Сортировка таблицы
function sortTable(column, tableId) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = table.classList.contains('sorted-asc');

    rows.sort((a, b) => {
        const cellA = a.querySelector(`td:nth-child(${column})`).textContent;
        const cellB = b.querySelector(`td:nth-child(${column})`).textContent;

        if (isNumeric(cellA) && isNumeric(cellB)) {
            return (isAscending ? 1 : -1) * (parseFloat(cellA) - parseFloat(cellB));
        } else {
            return (isAscending ? 1 : -1) * cellA.localeCompare(cellB, 'ru');
        }
    });

    rows.forEach(row => tbody.appendChild(row));
    table.classList.toggle('sorted-asc');
}

// Проверка чисел
function isNumeric(str) {
    return !isNaN(parseFloat(str));
}

// Обновление данных
function refreshData() {
    location.reload();
}
