// JavaScript для управления остатками
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация модальных окон
    const adjustModal = document.getElementById('adjustModal');
    if (adjustModal) {
        adjustModal.addEventListener('show.bs.modal', function(event) {
            // Данные уже заполнены в adjustStock, просто логируем
            console.log('Modal show event - data already set');
        });
    }

    // Автообновление при добавлении остатка
    const stockForms = document.querySelectorAll('form[action*="add_stock"]');
    stockForms.forEach(form => {
        form.addEventListener('submit', function() {
            setTimeout(() => {
                location.reload();
            }, 1000);
        });
    });
});

// Корректировка остатка - упрощенная версия
function adjustStock(button) {
    console.log('adjustStock called with button:', button);
    console.log('Button data attributes:', {
        type: button.getAttribute('data-type'),
        id: button.getAttribute('data-id'),
        name: button.getAttribute('data-name'),
        quantity: button.getAttribute('data-quantity')
    });
    
    // Очищаем поля перед заполнением
    document.getElementById('adjustType').value = '';
    document.getElementById('adjustId').value = '';
    document.getElementById('componentName').textContent = '';
    document.getElementById('currentStock').textContent = '';
    
    // Получаем данные из кнопки
    const type = button.getAttribute('data-type');
    const id = button.getAttribute('data-id');
    const name = button.getAttribute('data-name');
    const quantity = button.getAttribute('data-quantity');
    
    // Заполняем скрытые поля
    document.getElementById('adjustType').value = type;
    document.getElementById('adjustId').value = id;
    
    // Заполняем отображаемые поля
    document.getElementById('componentName').textContent = name || '-';
    document.getElementById('currentStock').textContent = quantity || '-';
    
    console.log('Data set in modal:', { type, id, name, quantity });
    
    // Открываем модальное окно
    const modalElement = document.getElementById('adjustModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    console.log('Modal should be open');
}

// Добавление носителя
function addDisc() {
    const name = document.getElementById('discName').value;
    const description = document.getElementById('discDescription').value;

    if (name) {
        // Логика добавления
        console.log('Добавлен носитель:', { name, description });
    }
}

// Добавление коробки
function addBox() {
    const name = document.getElementById('boxName').value;
    const description = document.getElementById('boxDescription').value;

    if (name) {
        // Логика добавления
        console.log('Добавлена коробка:', { name, description });
    }
}

// Импорт остатков
function importStock() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.xlsx,.xls';

    input.onchange = e => {
        const file = e.target.files[0];
        if (file) {
            // Логика импорта
            console.log('Импортированы остатки:', file.name);
        }
    };

    input.click();
}
