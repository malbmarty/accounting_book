
// Загрузка сотрудников доступных по выбранному отделу
function loadEmployees() {
    const departmentId = document.getElementById('department').value;
    if (!departmentId) return;
    
    fetch(`/payroll/api/employees/?department=${departmentId}`)
        .then(response => response.json())
        .then(employees => {
            const select = document.getElementById('employee');
            select.innerHTML = '<option value="">Выберите сотрудника</option>';
            
            employees.forEach(emp => {
                select.innerHTML += `<option value="${emp.id}">${emp.full_name}</option>`;
            });
            
        });
}

// Загрузка таблицы начислений 
function loadAccruals() {
    

    fetch(`/payroll/api/accruals/`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('accrualsBody');
            tbody.innerHTML = '';
            
            data.forEach(accrual => {
                  // Форматирование даты
                const [year, month, day] = accrual.date.split('-');
                const formattedDate = `${day}.${month}.${year}`;
                const row = `
                    <tr>
                        <td>${formattedDate}</td>  
                        <td>${accrual.project_name}</td>  
                        <td>${accrual.department_name}</td>
                        <td>${accrual.employee_name}</td>  
                        <td>${accrual.hourly_pay}</td>
                        <td>${accrual.salary}</td>
                        <td>${accrual.addition_pay}</td>
                        <td>${accrual.deduction}</td>
                        <td>${accrual.comment || ''}</td>
                        <td>
                            <a href="/payroll/edit-accrual/${accrual.id}/">Редактировать</a>
                            <button onclick="deleteaccrual(${accrual.id})">Удалить</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}


// Удаление транзакции
function deleteaccrual(id) {
    if (confirm('Удалить запись?')) {
        fetch(`/payroll/api/accruals/${id}/`, { method: 'DELETE' })
            .then(() => loadAccruals());
    }
}

// Создание новой записи сотрудника
document.getElementById('createAccrualForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/payroll/api/accruals/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
           'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                // Создаем объект ошибки с данными от сервера
                const error = new Error('Validation Error');
                error.responseData = errorData;
                throw error;
            });
        }
        return response.json();
    })
    .then(data => {
        alert('Запись создана успешно!');
        this.reset(); // Очищаем форму
        loadAccruals()
    })
    .catch(error => {
        if (error.responseData) {
            // Обрабатываем ошибки валидации из сериализатора
            let errorMessage = 'Ошибки валидации:\n\n';
            
            // Проходим по всем полям с ошибками
            for (const [field, message] of Object.entries(error.responseData)) {
                const fieldName = field;
                errorMessage += `• ${fieldName}: ${message}\n`;
            }
            
            alert(errorMessage);
        } else {
            alert('Ошибка при создании записи: ' + error.message);
        }
    });
});

// Функция для получения CSRF токена
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

// Загружаем данные при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли на странице таблица транзакций
    if (document.getElementById('accrualsBody')) {
        loadAccruals();
    }
});