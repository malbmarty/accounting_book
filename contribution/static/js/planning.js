
// Загрузка таблицы оперативный учет 
function loadPlanning() {

    fetch(`/contribution/api/planning-records/`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('planningBody');
            tbody.innerHTML = '';
            
            
            data.forEach(record => {
                // Форматирование даты
                const [year, month, day] = record.date.split('-');
                const formattedDate = `${day}.${month}.${year}`;
              
                
                const row = `
                    <tr>
                        <td>${formattedDate}</td>
                        <td>${record.project_name}</td>
                        <td>${record.item_name}</td> 
                        <td>${record.payment_amount}</td>
                        <td>${record.frequency_name}</td>
                        <td>${record.comment || ''}</td>
                        <td>
                            <a href="/contribution/edit-planning/${record.id}/">Редактировать</a>
                            <button onclick="deletePlanning(${record.id})">Удалить</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}


// Удаление транзакции
function deletePlanning(id) {
    if (confirm('Удалить запись?')) {
        fetch(`/contribution/api/planning-records/${id}/`, { method: 'DELETE' })
            .then(() => loadPlanning());
    }
}

// Создание новой записи сотрудника
document.getElementById('createPlannigForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/contribution/api/planning-records/', {
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
        loadPlanning()
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
    if (document.getElementById('planningBody')) {
        loadPlanning();
    }
});