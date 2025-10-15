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

// === 3. Применение цветов отделов ===
document.addEventListener("DOMContentLoaded", function() {
    const colorsEl = document.getElementById("departmentColorsData");
    if (!colorsEl) return;

    let colors = {};
    try {
        const raw = colorsEl.getAttribute("data-colors");
        colors = JSON.parse(raw);
        console.log("✅ Цвета отделов:", colors);
    } catch (err) {
        console.error("❌ Ошибка парсинга цветов:", err);
        return;
    }

    // Проходим по каждому отделу и задаем стили
    document.querySelectorAll(".dept-data").forEach(deptBlock => {
        const deptNameEl = deptBlock.querySelector(".dept-name span");
        if (!deptNameEl) return;

        const deptName = deptNameEl.textContent.trim();
        const color = colors[deptName];

        if (color) {
            const infoEl = deptBlock.querySelector(".dept-info");
            if (infoEl) {
                infoEl.style.background = color.bg;
                infoEl.style.borderColor = color.text;
            }

            // Цвет текста
            deptNameEl.style.color = color.text;

            // Цвет кружка в svg
            const circle = deptBlock.querySelector(".dept-name svg circle");
            if (circle) circle.setAttribute("fill", color.text);
        }
    });
});


