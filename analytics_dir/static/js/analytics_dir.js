document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');
    const backdrop = document.getElementById('modalBackdrop'); // один бекдроп
    const modals = document.querySelectorAll('.modal');
    const items = document.querySelectorAll('.dropdown-item[data-modal]');

    // Дропдаун
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        toggle.addEventListener('click', e => {
            e.stopPropagation();
            const isOpen = menu.classList.contains('open');

            // Закрываем все остальные меню
            document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));

            if (!isOpen) menu.classList.add('open');
        });
    });

    // Закрываем дропдаун при клике вне
    document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown-menu.open').forEach(menu => menu.classList.remove('open'));
    });

    // Открытие модалки
    items.forEach(item => {
        item.addEventListener('click', () => {
            const modalId = item.getAttribute('data-modal');
            const modal = document.getElementById(modalId);

            if (!modal) return;

            // Скрываем все модалки
            modals.forEach(m => m.style.display = 'none');

            // Показываем нужную
            modal.style.display = 'flex'; // flex, чтобы сохранялся твой CSS
            backdrop.style.display = 'block';

            // Закрываем дропдаун
            const menu = item.closest('.dropdown-menu');
            if (menu) menu.classList.remove('open');
        });
    });

    // Закрытие модалки по бекдропу
    backdrop.addEventListener('click', () => {
        modals.forEach(m => m.style.display = 'none');
        backdrop.style.display = 'none';
    });
});
