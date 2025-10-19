function loadVariabilitiesForFlowType(flowTypeId, formSelector) {
    const form = document.querySelector(formSelector);
    const dropdown = form.querySelector('.dropdown[data-name="variability"]');
    const toggle = dropdown.querySelector('.dropdown-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');
    const hiddenInput = dropdown.querySelector('input[type="hidden"]');

    // Сброс dropdown
    hiddenInput.value = '';
    toggle.textContent = toggle.dataset.placeholder || 'Выберите тип изменчивости';
    menu.innerHTML = '';

    if (!flowTypeId) return;

    fetch(`/analytics-dir/api/variabilities/?flow_type=${flowTypeId}`)
        .then(response => response.json())
        .then(variabilities => {
            variabilities.forEach(v => {
                const item = document.createElement('div');
                item.className = 'dropdown-item';
                item.dataset.value = v.id;
                item.textContent = v.name;

                item.addEventListener('click', () => {
                    hiddenInput.value = v.id;
                    toggle.textContent = v.name;
                    menu.classList.remove('open');
                    toggle.classList.remove('active');
                });

                menu.appendChild(item);
            });
        })
        .catch(err => console.error('Ошибка загрузки изменчивостей:', err));
}

document.querySelectorAll('.dropdown[data-name="flow_type"] .dropdown-menu').forEach(menu => {
        menu.addEventListener('click', function(e) {
            const item = e.target.closest('.dropdown-item');
            if (!item) return;

            const form = item.closest('form');
            const flowTypeId = item.dataset.value;

            // Подгружаем сотрудников для текущей формы
            loadVariabilitiesForFlowType(flowTypeId, `#${form.id}`);
        });
    });


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
            case 'projectForm': return '/analytics-dir/api/projects/';
            case 'participantForm': return '/analytics-dir/api/participants/';
            case 'paymentSystemForm': return '/analytics-dir/api/payment-systems/';
            case 'counterpartyForm': return '/analytics-dir/api/counterparties/';
            case 'groupForm': return '/analytics-dir/api/groups/';
            case 'flowTypeForm': return '/analytics-dir/api/flow-types/';
            case 'variabilityForm': return '/analytics-dir/api/variabilities/';
            case 'itemForm': return '/analytics-dir/api/items/';
            case 'frequencyForm': return '/analytics-dir/api/frequencies/';
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

