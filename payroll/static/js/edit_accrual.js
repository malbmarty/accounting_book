// Загружаем сотрудников по отделу.
// preserveSelected — если true, используем data-selected-employee (нужно для initial load).
async function loadEmployees(preserveSelected = false) {
    const departmentId = document.getElementById('department').value;
    const employeeSelect = document.getElementById('employee');

    if (!departmentId) {
        employeeSelect.innerHTML = '<option value="">Выберите сотрудника</option>';
        employeeSelect.value = '';
        return;
    }

    // Показываем заглушки пока идут запросы
    employeeSelect.innerHTML = '<option value="">Загрузка сотрудника...</option>';

    try {
        const response = await fetch(`/payroll/api/employees/?department=${departmentId}`);
        if (!response.ok) throw new Error('Ошибка при загрузке сотрудников');
        const employees = await response.json();

        // Построим options
        let html = '<option value="">Выберите сотрудника</option>';
        employees.forEach(emp => {
            html += `<option value="${emp.id}">${emp.full_name}</option>`;
        });
        employeeSelect.innerHTML = html;

        if (preserveSelected && employeeSelect.dataset.selectedEmployee) {
            // начальная загрузка: выставляем категорию из data-*
            employeeSelect.value = employeeSelect.dataset.selectedEmployee;
        } 

    } catch (err) {
        console.error(err);
        employeeSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
    }
}

// Редактирование начисления
document.getElementById('editAccrualForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = this;
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    const accrualId = window.location.pathname.split('/').filter(Boolean).pop();
    const successUrl = form.dataset.successUrl;

    fetch(`/payroll/api/accruals/${accrualId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                const error = new Error('Validation Error');
                error.responseData = errorData;
                throw error;
            });
        }
        return response.json();
    })
    .then(data => {
        alert('Запись отредактирована успешно!');
        window.location.href = successUrl;
    })
    .catch(error => {
        if (error.responseData) {
            let errorMessage = 'Ошибки валидации:\n\n';
            for (const [field, message] of Object.entries(error.responseData)) {
                errorMessage += `• ${field}: ${message}\n`;
            }
            alert(errorMessage);
        } else {
            alert('Ошибка при редактировании записи: ' + error.message);
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



// Инициализация при открытии страницы
document.addEventListener('DOMContentLoaded', async function() {
    const departmentId = document.getElementById('department').value;
    if (departmentId) {
        // При начальной загрузке сохраняем выбранные значения (data-*)
        await loadEmployees(true);
    } else {
        document.getElementById('employee').innerHTML = '<option value="">Выберите отдел</option>';
    }

});
