
// Загрузка таблицы сотрудников 
function loadEmployees() {
    

    fetch(`/payroll/api/employees/`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('employeesBody');
            tbody.innerHTML = '';
            
            
            data.forEach(employee => {
                const row = `
                    <tr>
                        <td>${employee.full_name}</td>
                        <td>${employee.position_name}</td>
                        <td>${employee.department_name}</td>
                        <td>${employee.status_name}</td>
                        <td>${employee.employee_type_name}</td>
                        <td>${employee.bank_name}</td>
                        <td>${employee.card_number || ''}</td>
                        <td>
                            <a href="/payroll/edit-employee/${employee.id}/">Редактировать</a>
                            <button onclick="deleteEmployee(${employee.id})">Удалить</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}


// Удаление транзакции
function deleteEmployee(id) {
    if (confirm('Удалить запись?')) {
        fetch(`/payroll/api/employees/${id}/`, { method: 'DELETE' })
            .then(() => loadEmployees());
    }
}

// Создание новой записи сотрудника
document.getElementById('createEmployeeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/payroll/api/employees/', {
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
        loadEmployees()
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
    if (document.getElementById('employeesBody')) {
        loadEmployees();
    }
});