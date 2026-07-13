/**
 * stock.js — Управление остатками на странице /stock
 *
 * Функционал:
 *  1. Сохранение и восстановление активной вкладки (Носители / Коробки)
 *     при перезагрузке страницы после POST-запросов (корректировка, добавление).
 *  2. Открытие модального окна корректировки остатка с предзаполненными данными.
 *  3. Заготовки функций добавления носителя, коробки и импорта остатков.
 */

// ── Инициализация после загрузки DOM ───────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // ─── 1. Восстановление активной вкладки ────────────────────────
    // После перенаправления (POST /stock/adjust → redirect /stock)
    // страница перезагружается и Bootstrap сбрасывает вкладку на первую.
    // Чтобы сохранить положение пользователя, мы храним ID активной
    // вкладки в sessionStorage и восстанавливаем её здесь.

    var savedTab = sessionStorage.getItem('stock_active_tab');
    if (savedTab) {
        // savedTab хранит CSS-селектор вида "#boxes-tab"
        var tabEl = document.querySelector(savedTab);
        if (tabEl) {
            // Используем API Bootstrap для программного переключения вкладки
            var tab = new bootstrap.Tab(tabEl);
            tab.show();
        }
        // Удаляем запись, чтобы при следующем обычном открытии страницы
        // вкладка не принудительно переключалась
        sessionStorage.removeItem('stock_active_tab');
    }

    // ─── 2. Сохранение активной вкладки при ручном переключении ────
    // При клике на вкладку Bootstrap событие 'shown.bs.tab' срабатывает
    // после завершения анимации переключения. Записываем ID кнопки
    // вкладки в sessionStorage, чтобы он пережил перезагрузку страницы.

    document.querySelectorAll('#stockTabs .nav-link').forEach(function (tab) {
        tab.addEventListener('shown.bs.tab', function (e) {
            // e.target — кнопка-вкладка, на которую переключились
            sessionStorage.setItem('stock_active_tab', '#' + e.target.id);
        });
    });

    // ─── 3. Сохранение вкладки перед отправкой формы корректировки ─
    // Форма корректировки (#adjustForm) отправляется POST-запросом,
    // сервер выполняет корректировку и делает redirect обратно на /stock.
    // При этом событие 'shown.bs.tab' может не сработать (форма внутри
    // модального окна, не вкладки). Поэтому явно сохраняем текущую
    // активную вкладку в момент отправки формы.

    var adjustForm = document.getElementById('adjustForm');
    if (adjustForm) {
        adjustForm.addEventListener('submit', function () {
            var activeTab = document.querySelector('#stockTabs .nav-link.active');
            if (activeTab) {
                sessionStorage.setItem('stock_active_tab', '#' + activeTab.id);
            }
        });
    }

    // ─── 4. Инициализация модального окна корректировки ────────────
    // Bootstrap автоматически управляет фокусом и backdrop при открытии
    // модального окна. Обработчик оставлен на случай, если в
    // будущем потребуется дополнительная логика при открытии.

    var adjustModal = document.getElementById('adjustModal');
    if (adjustModal) {
        adjustModal.addEventListener('show.bs.modal', function () {
            // Место для будущей логики, например, загрузки данных с сервера
        });
    }
});


// ── Корректировка остатка ──────────────────────────────────────────

/**
 * adjustStock(button) — Открывает модальное окно корректировки остатка.
 *
 * Вызывается из HTML через onclick="adjustStock(this)" на кнопке
 * «Корректировка» в строке таблицы остатков.
 *
 * Данные передаются через data-атрибуты кнопки:
 *   data-type     — тип компонента: "disc" или "box"
 *   data-id       — ID компонента в БД
 *   data-name     — отображаемое название
 *   data-quantity — текущее количество на складе
 *
 * @param {HTMLButtonElement} button — кнопка, из которой считываются data-атрибуты
 */
function adjustStock(button) {
    // ── Считывание данных из data-атрибутов кнопки ──
    var type     = button.getAttribute('data-type');
    var id       = button.getAttribute('data-id');
    var name     = button.getAttribute('data-name');
    var quantity = button.getAttribute('data-quantity');

    // ── Очистка полей модального окна ──
    // Сбрасываем все поля перед заполнением, чтобы не отобразить
    // данные от предыдущего вызова (если модальное окно не закрывалось).

    // Скрытые поля формы (отправляются на сервер)
    document.getElementById('adjustType').value   = '';
    document.getElementById('adjustId').value     = '';

    // Отображаемые пользователю (read-only)
    document.getElementById('componentName').textContent = '';
    document.getElementById('currentStock').textContent  = '';

    // ── Заполнение полей данными ──

    // Скрытые поля — передаются серверу как hidden inputs
    document.getElementById('adjustType').value = type;
    document.getElementById('adjustId').value   = id;

    // Отображаемые поля — показывают пользователю что корректируется
    document.getElementById('componentName').textContent = name  || '-';
    document.getElementById('currentStock').textContent  = quantity || '-';

    // ── Открытие модального окна ──
    // Создаём экземпляр Bootstrap Modal и вызываем show().
    // Bootstrap автоматически: показывает backdrop, переводит фокус,
    // блокирует прокрутку фона.
    var modalElement = document.getElementById('adjustModal');
    var modal = new bootstrap.Modal(modalElement);
    modal.show();
}


// ── Добавление носителя (заготовка) ────────────────────────────────

/**
 * addDisc() — Обработчик добавления нового носителя.
 *
 * В текущей реализации только логирует данные в консоль.
 * Полная реализация: AJAX-запрос к серверу с последующим обновлением таблицы.
 */
function addDisc() {
    var name        = document.getElementById('discName').value;
    var description = document.getElementById('discDescription').value;

    if (name) {
        // TODO: AJAX-запрос POST /discs/add
        console.log('Добавлен носитель:', { name: name, description: description });
    }
}


// ── Добавление коробки (заготовка) ─────────────────────────────────

/**
 * addBox() — Обработчик добавления новой коробки.
 *
 * В текущей реализации только логирует данные в консоль.
 * Полная реализация: AJAX-запрос к серверу с последующим обновлением таблицы.
 */
function addBox() {
    var name        = document.getElementById('boxName').value;
    var description = document.getElementById('boxDescription').value;

    if (name) {
        // TODO: AJAX-запрос POST /boxes/add
        console.log('Добавлена коробка:', { name: name, description: description });
    }
}


// ── Импорт остатков из Excel (заготовка) ───────────────────────────

/**
 * importStock() — Открывает диалог выбора файла для импорта остатков.
 *
 * Поддерживаемые форматы: .xlsx, .xls.
 * В текущей реализации только позволяет выбрать файл и логирует его имя.
 * Полная реализация: чтение файла (SheetJS/xlsx), валидация данных,
 * AJAX-запрос для массового добавления остатков.
 */
function importStock() {
    // Создаём скрытый input для выбора файла,
    // чтобы не зависеть от статичного input в HTML
    var input     = document.createElement('input');
    input.type    = 'file';
    input.accept  = '.xlsx,.xls';

    input.onchange = function (e) {
        var file = e.target.files[0];
        if (file) {
            // TODO: прочитать файл через FileReader / SheetJS,
            //       валидировать данные, отправить на сервер
            console.log('Импортирован файл остатков:', file.name);
        }
    };

    // Программно кликаем по input, чтобы открыть диалог выбора файла
    input.click();
}


// ── Списание по браку ──────────────────────────────────────────────

/**
 * writeOff(button) — Открывает модальное окно списания по браку.
 *
 * Вызывается из HTML через onclick="writeOff(this)" на кнопке «Брак»
 * в строке таблицы остатков.
 *
 * Данные передаются через data-атрибуты кнопки (аналогично adjustStock):
 *   data-type     — тип компонента: "disc" или "box"
 *   data-id       — ID компонента в БД
 *   data-name     — отображаемое название
 *   data-quantity — текущее количество на складе
 *
 * @param {HTMLButtonElement} button — кнопка, из которой считываются data-атрибуты
 */
function writeOff(button) {
    var type     = button.getAttribute('data-type');
    var id       = button.getAttribute('data-id');
    var name     = button.getAttribute('data-name');
    var quantity = button.getAttribute('data-quantity');

    document.getElementById('writeOffType').value     = type;
    document.getElementById('writeOffId').value       = id;
    document.getElementById('writeOffName').textContent  = name || '-';
    document.getElementById('writeOffCurrent').textContent = quantity || '-';
    document.getElementById('writeOffQuantity').value = '';
    document.getElementById('writeOffQuantity').max   = quantity || 1;
    document.getElementById('writeOffReason').value   = '';

    var modalElement = document.getElementById('writeOffModal');
    var modal = new bootstrap.Modal(modalElement);
    modal.show();
}
