document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');
    const backdrop = document.getElementById('modalBackdrop');
    const modals = document.querySelectorAll('.modal');
    const items = document.querySelectorAll('.dropdown-item[data-modal]');

    // Дропдауны
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        toggle.addEventListener('click', e => {
            e.stopPropagation();
            const isOpen = menu.classList.contains('open');
            document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
            if (!isOpen) menu.classList.add('open');
        });

        dropdown.querySelectorAll('.dropdown-item[data-value]').forEach(item => {
            item.addEventListener('click', () => {
                const value = item.getAttribute('data-value');
                const text = item.textContent;
                dropdown.querySelector('.dropdown-toggle').textContent = text;
                dropdown.querySelector('input[type="hidden"]').value = value;
                dropdown.querySelector('.dropdown-menu').classList.remove('open');
            });
        });
    });

    document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown-menu.open').forEach(menu => menu.classList.remove('open'));
    });

    // Открытие модалок
    items.forEach(item => {
        item.addEventListener('click', () => {
            const modalId = item.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (!modal) return;
            modals.forEach(m => m.style.display = 'none');
            modal.style.display = 'flex';
            backdrop.style.display = 'block';
            const menu = item.closest('.dropdown-menu');
            if (menu) menu.classList.remove('open');
        });
    });

    function closeAllModals() {
        modals.forEach(m => m.style.display = 'none');
        backdrop.style.display = 'none';
    }

    backdrop.addEventListener('click', closeAllModals);
    modals.forEach(modal => {
        const closeBtn = modal.querySelector('.modal-close');
        const cancelBtn = modal.querySelector('.button-cancel');
        if (closeBtn) closeBtn.addEventListener('click', closeAllModals);
        if (cancelBtn) cancelBtn.addEventListener('click', closeAllModals);
    });

    // Функция для получения URL API по id формы
    function getApiUrl(formId) {
        switch(formId) {
            case 'positionForm': return '/payroll/api/positions/';
            case 'departmentForm': return '/payroll/api/departments/';
            case 'statusForm': return '/payroll/api/statuses/';
            case 'employeeTypeForm': return '/payroll/api/employee-types/';
            case 'paymentTypeForm': return '/payroll/api/payment-types/';

            default: return null;
        }
    }

    // Отправка форм на DRF endpoints
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', e => {
            e.preventDefault();
            const url = getApiUrl(form.id);
            if (!url) return console.error('Unknown form id:', form.id);

            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.id) { // DRF возвращает объект с id при успешном создании
                    // alert('Добавлено успешно!');
                    closeAllModals();
                    form.reset();
                    location.reload();
                    // TODO: Динамически обновить таблицу без перезагрузки
                } else {
                    alert('Ошибка: ' + JSON.stringify(data));
                }
            })
            .catch(err => {
                console.error(err);
                alert('Ошибка при отправке формы');
            });
        });
    });

    
});

