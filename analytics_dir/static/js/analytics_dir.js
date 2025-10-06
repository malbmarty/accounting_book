// Общие функции для всех справочников
function editItem(type, id, name, groupId = '', flowType = '', variability = '') {
    document.getElementById(`${type}Id`).value = id;
    document.querySelector(`#${type}Form input[name="name"]`).value = name;
    if (type === 'item') {
        document.querySelector(`#${type}Form select[name="group"]`).value = groupId;
        document.querySelector(`#${type}Form select[name="flow_type"]`).value = flowType;
        document.querySelector(`#${type}Form select[name="variability"]`).value = variability;
        
        // Показываем/скрываем поле variability в зависимости от flow_type
        toggleVariabilityField(flowType);
    }
    document.querySelector(`#${type}Form`).scrollIntoView();
}

// Отчистка формы
function clearForm(formId) {
    document.getElementById(formId).reset();
    document.getElementById(formId).querySelector('input[type="hidden"]').value = '';
    // Для формы статей дополнительно скрываем поле variability
    if (formId === 'itemForm') {
        document.querySelector('#variabilitySelect').closest('.form-group').style.display = 'none';
    }
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

// Функция для показа/скрытия поля variability
function toggleVariabilityField(flowType) {
    const variabilityField = document.getElementById('variabilitySelect');
    const variabilityGroup = variabilityField.closest('.form-group');
    
    if (flowType === 'expense') {
        variabilityGroup.style.display = 'block';
    } else {
        variabilityGroup.style.display = 'none';
        variabilityField.value = '';
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

    // Платежные системы
    document.getElementById('paymentSystemForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveItem('payment-systems', this);
    });

    // Контрагенты
    document.getElementById('counterpartyForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveItem('counterparties', this);
    });

    // Группы
    document.getElementById('groupForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveItem('groups', this);
    });

    // Статьи
    document.getElementById('itemForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveItem('items', this);
    });

    // Обработчик изменения типа потока для статей
    const flowTypeSelect = document.querySelector('#itemForm select[name="flow_type"]');
    if (flowTypeSelect) {
        flowTypeSelect.addEventListener('change', function(e) {
            toggleVariabilityField(e.target.value);
        });
        
        // Инициализация состояния при загрузке
        const currentFlowType = flowTypeSelect.value;
        if (currentFlowType) {
            toggleVariabilityField(currentFlowType);
        }
    }

});

// Загрузка и редактирование записи
function saveItem(endpoint, form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const id = data.id;
    const url = id ? `/analytics-dir/api/${endpoint}/${id}/` : `/analytics-dir/api/${endpoint}/`;
    const method = id ? 'PUT' : 'POST';

        // Для статей: если flow_type не 'expense', очищаем variability
    if (endpoint === 'items' && data.flow_type !== 'expense') {
        data.variability = '';
    }


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