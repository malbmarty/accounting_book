
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
function loadPayouts() {
    
    fetch(`/payroll/api/payouts/`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('payoutsBody');
            tbody.innerHTML = '';
            
            data.forEach(payout => {
                  // Форматирование даты
                const [year, month, day] = payout.date.split('-');
                const formattedDate = `${day}.${month}.${year}`;
                const row = `
                    <tr>
                        <td>${formattedDate}</td>  
                        <td>${payout.project_name}</td>
                        <td>${payout.payer_name}</td>
                        <td>${payout.recipient_name}</td>  
                        <td>${payout.department_name}</td>
                        <td>${payout.employee_name}</td>  
                        <td>${payout.payment_type}</td>
                        <td>${payout.amount}</td>
                        <td>${payout.comment || ''}</td>
                        <td>
                            <a href="/payroll/edit-payout/${payout.id}/">Редактировать</a>
                            <button onclick="deletepayout(${payout.id})">Удалить</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}


// Удаление транзакции
function deletepayout(id) {
    if (confirm('Удалить запись?')) {
        fetch(`/payroll/api/payouts/${id}/`, { method: 'DELETE' })
            .then(() => loadPayouts());
    }
}

// Создание новой записи сотрудника
document.getElementById('createPayoutForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/payroll/api/payouts/', {
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
        loadPayouts()
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
    if (document.getElementById('payoutsBody')) {
        loadPayouts();
    }
});