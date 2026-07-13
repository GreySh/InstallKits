// Маппинг типов операций на русские названия
const operationTypeMap = {
    'add_disc': 'Добавлен носитель',
    'add_box': 'Добавлена коробка',
    'adjust_stock': 'Корректировка остатка',
    'dispatch': 'Списание комплекта',
    'write_off': 'Списание по браку'
};

// Функция для перевода типа операции
function getOperationTypeName(type) {
    return operationTypeMap[type] || type;
}

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация календарей
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = getCurrentDate();
        }
    });
});

// Показать модальное окно отчета по операциям
function showOperationsReport() {
    const modal = new bootstrap.Modal(document.getElementById('operationsReportModal'));
    modal.show();
    
    // Загрузить все операции
    fetch('/api/operations')
        .then(response => response.json())
        .then(operations => {
            allOperations = operations;
            console.log('Загружено операций:', operations.length);
            if (operations.length > 0) {
                console.log('Пример операции:', JSON.stringify(operations[0], null, 2));
            }
            // Автоматически отобразить все операции при загрузке
            renderOperationsTable(operations);
        })
        .catch(error => {
            console.error('Ошибка загрузки операций:', error);
            document.getElementById('noOperationsMessage').style.display = 'block';
        });
}

// Фильтровать и отображать операции
function filterAndRenderOperations() {
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;
    
    let filtered = allOperations;
    
    if (start_date || end_date) {
        filtered = allOperations.filter(op => {
            const opDate = new Date(op.date);
            
            if (start_date) {
                const startDate = new Date(start_date);
                startDate.setHours(0, 0, 0, 0);
                if (opDate < startDate) return false;
            }
            
            if (end_date) {
                const endDate = new Date(end_date);
                endDate.setHours(23, 59, 59, 999);
                if (opDate > endDate) return false;
            }
            
            return true;
        });
    }
    
    renderOperationsTable(filtered);
}

// Отобразить операции в таблице
function renderOperationsTable(operations) {
    const tbody = document.getElementById('operationsTableBody');
    const noMessage = document.getElementById('noOperationsMessage');
    
    tbody.innerHTML = '';
    
    console.log('Отображение операций, количество:', operations.length);
    
    if (!operations || operations.length === 0) {
        noMessage.style.display = 'block';
        return;
    }
    
    noMessage.style.display = 'none';
    
    operations.forEach((op, index) => {
        console.log('Операция', index, ':', op);
        const tr = document.createElement('tr');
        
        // Форматирование даты
        let dateStr = '';
        try {
            const dt = new Date(op.date);
            dateStr = dt.toLocaleString('ru-RU');
        } catch (e) {
            console.error('Ошибка парсинга даты:', e);
            dateStr = op.date || 'неизвестно';
        }
        
        // Получение названия продукта
        const product_id = op.product_id;
        const product_name = op.product_name || getProductNameById(product_id) || 'Неизвестно';
        
        // Тип операции
        const op_type = getOperationTypeName(op.operation_type || 'неизвестно');
        
        // Количество
        const quantity = op.quantity || 0;
        
        // Детали
        let details_text = '';
        const details = op.details;
        if (typeof details === 'object' && details !== null) {
            const components = details.components;
            if (components && Array.isArray(components) && components.length > 0) {
                // Для операций списания показываем сколько комплектов и какие компоненты
                if (op.operation_type === 'dispatch' && details.kits_count) {
                    details_text = `Комплектов: ${details.kits_count}; Компоненты: `;
                    details_text += components.map(c => {
                        const type = c.type || 'неизвестно';
                        const name = c.name || 'неизвестно';
                        const qty_per = c.quantity_per_set || '?';
                        const total_qty = c.total_quantity || c.quantity || '';
                        return `${name} (${qty_per} на комплект × ${details.kits_count} = ${total_qty} шт.)`;
                    }).join('; ');
                } else {
                    // Для остальных операций простой формат
                    details_text = components.map(c => {
                        const type = c.type || 'неизвестно';
                        const name = c.name || 'неизвестно';
                        const total_qty = c.total_quantity || c.quantity || '';
                        return `${name} (${total_qty} шт.)`;
                    }).join('; ');
                }
            }
        }
        
        tr.innerHTML = `
            <td>${dateStr}</td>
            <td>${op_type}</td>
            <td>${product_name}</td>
            <td>${quantity}</td>
            <td>${details_text}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

// Получить имя продукта по ID (заглушка для API)
function getProductNameById(product_id) {
    // В реальном приложении можно кэшировать продукты
    return null;
}

// Показать отчет (обновить таблицу)
function viewOperationsReport() {
    filterAndRenderOperations();
}

// Экспорт в Excel (CSV)
function exportOperationsReport() {
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;
    
    // Формируем URL с параметрами
    let url = '/reports/operations/export?';
    if (start_date) url += `start_date=${start_date}&`;
    if (end_date) url += `end_date=${end_date}`;
    
    // Создаем скрытую ссылку для скачивания
    const link = document.createElement('a');
    link.href = url;
    link.download = `operations_${start_date || 'all'}_${end_date || 'now'}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Получить текущую дату
function getCurrentDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

// Скачивание файла
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Экспорт уровней остатков
function exportStockLevels() {
    window.location.href = '/reports/stock-levels/export';
}

// Фильтрация по дате
function filterByDate(startDate, endDate) {
    // Логика фильтрации
    console.log('Фильтр по дате:', { startDate, endDate });
}

// Экспорт в CSV
function exportToCSV() {
    alert('Экспорт в CSV будет доступен в ближайшем обновлении!');
}

// Выбор периода
function selectPeriod(period) {
    const today = new Date();
    let startDate, endDate;

    switch (period) {
        case 'today':
            startDate = endDate = getCurrentDate();
            break;
        case 'week':
            startDate = new Date(today.setDate(today.getDate() - 7)).toISOString().split('T')[0];
            endDate = getCurrentDate();
            break;
        case 'month':
            startDate = new Date(today.setMonth(today.getMonth() - 1)).toISOString().split('T')[0];
            endDate = getCurrentDate();
            break;
        case 'year':
            startDate = new Date(today.setFullYear(today.getFullYear() - 1)).toISOString().split('T')[0];
            endDate = getCurrentDate();
            break;
    }

    document.getElementById('start_date').value = startDate;
    document.getElementById('end_date').value = endDate;
}
