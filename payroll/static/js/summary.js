document.addEventListener("DOMContentLoaded", function() {
    // === 1. Обработчики для input-баланса ===
    document.querySelectorAll('.input-balance').forEach(input => {
        input.addEventListener('change', function() {
            const employeeId = this.dataset.employee;
            const amount = this.value;
            const year = parseInt(this.dataset.year); // data-year в input

            fetch("/payroll/summary/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie('csrftoken')
                },
                body: JSON.stringify({
                    employee_id: employeeId,
                    amount: amount,
                    year: year
                })
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.status === "ok") {
                    window.location.reload(); // обновляем страницу после сохранения
                } else {
                    alert("Ошибка: " + (data.message || "неизвестная ошибка"));
                }
            })
            .catch(err => console.error("Ошибка:", err));
        });
    });


    // === 2. Dropdown для выбора года ===
    const dropdown = document.querySelector('.dropdown');
    if (dropdown) {  // на случай, если блок отсутствует на странице
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        const items = dropdown.querySelectorAll('.dropdown-item');
        const hiddenInput = document.getElementById('year-input');
        const form = dropdown.closest('form');

        // показать/скрыть меню
        toggle.addEventListener('click', () => {
            menu.classList.toggle('open');
        });

        // выбор года
        items.forEach(item => {
            item.addEventListener('click', () => {
                const value = item.getAttribute('data-value');
                hiddenInput.value = value;
                toggle.textContent = `Год: ${value}`;
                menu.classList.remove('open');
                form.submit(); // отправка формы
            });
        });

        // закрытие по клику вне
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                menu.classList.remove('open');
            }
        });
    }
});

/**
 * Функция для получения CSRF токена из cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i=0; i<cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


