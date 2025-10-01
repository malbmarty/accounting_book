// Общие функции для всех справочников
function editItem(type, id, name) {
    document.getElementById(`${type}Id`).value = id;
    document.querySelector(`#${type}Form input[name="name"]`).value = name;
    document.querySelector(`#${type}Form`).scrollIntoView();
}

// Отчистка формы
function clearForm(formId) {
    document.getElementById(formId).reset();
    document.getElementById(formId).querySelector('input[type="hidden"]').value = '';
}

// Удаление записи выбранной записи из справочника
function deleteItem(endpoint, id) {
    if (confirm('Удалить запись?')) {
        fetch(`/analytics-dir/api/${endpoint}/${id}/`, {
            method: 'DELETE',
            // headers: {
            //     'X-CSRFToken': getCookie('csrftoken')
            // }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Ошибка при удалении');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при удалении');
        });
    }
}


// Обработчики форм
document.addEventListener('DOMContentLoaded', function() {
    // Проекты
    document.getElementById('projectForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveItem('projects', this);
    });

    // Стороны
    document.getElementById('participantForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveItem('participants', this);
    });



});

// Загрузка и редактирование записи
function saveItem(endpoint, form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const id = data.id;
    const url = id ? `/analytics-dir/api/${endpoint}/${id}/` : `/analytics-dir/api/${endpoint}/`;
    const method = id ? 'PUT' : 'POST';


    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            // 'X-CSRFToken': getCSRFToken(),
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            return response.json().then(errorData => {
                throw new Error(errorData.detail || 'Ошибка сохранения');
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при сохранении: ' + error.message);
    });
}

// function getCSRFToken() {
//     return document.querySelector('[name=csrfmiddlewaretoken]').value;
// }

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

Инициализация
document.addEventListener('DOMContentLoaded', function() {

});