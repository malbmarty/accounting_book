// Общие функции для всех справочников
function editItem(type, id, name, groupId = '', flowTypeId = '', variabilityId = '') {
    document.getElementById(`${type}Id`).value = id;
    
    if (type === 'variability') {
        // Для изменчивости используем специальную функцию
        editVariability(id, name, flowTypeId);
        return;
    }
    
    const nameInput = document.querySelector(`#${type}Form input[name="name"]`);
    if (nameInput) {
        nameInput.value = name;
    }
    
    if (type === 'item') {
        document.querySelector(`#${type}Form select[name="group"]`).value = groupId;
        document.querySelector(`#${type}Form select[name="flow_type"]`).value = flowTypeId;
        document.querySelector(`#${type}Form select[name="variability"]`).value = variabilityId;
        
        // Обновляем доступные варианты изменчивости при редактировании
        updateVariabilityOptions(flowTypeId);
    }
    
    document.querySelector(`#${type}Form`).scrollIntoView();
}

// Специальная функция для редактирования изменчивости
function editVariability(id, name, flowTypeId) {
    document.getElementById('variabilityId').value = id;
    document.querySelector('#variabilityForm input[name="name"]').value = name;
    document.querySelector('#variabilityForm select[name="flow_type"]').value = flowTypeId;
    document.querySelector('#variabilityForm').scrollIntoView();
}

// Обновление вариантов изменчивости в зависимости от выбранного типа потока
function updateVariabilityOptions(flowTypeId) {
    const variabilitySelect = document.getElementById('itemVariability');
    if (!variabilitySelect) return;
    
    const options = variabilitySelect.querySelectorAll('option');
    
    options.forEach(option => {
        if (option.value === '') {
            option.style.display = 'block'; // Всегда показывать пустой вариант
            return;
        }
        
        const optionFlowType = option.getAttribute('data-flow-type');
        if (optionFlowType === flowTypeId) {
            option.style.display = 'block';
        } else {
            option.style.display = 'none';
            // Сбрасываем значение, если текущий вариант не подходит
            if (variabilitySelect.value === option.value) {
                variabilitySelect.value = '';
            }
        }
    });
}

// Отчистка формы
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.reset();
    const hiddenInput = form.querySelector('input[type="hidden"]');
    if (hiddenInput) {
        hiddenInput.value = '';
    }
    
    // Для формы статей сбрасываем фильтрацию изменчивости
    if (formId === 'itemForm') {
        const variabilitySelect = document.getElementById('itemVariability');
        if (variabilitySelect) {
            const options = variabilitySelect.querySelectorAll('option');
            options.forEach(option => option.style.display = 'block');
        }
    }
}

// Удаление записи выбранной записи из справочника
function deleteItem(endpoint, id) {
    if (confirm('Удалить запись?')) {
        fetch(`/analytics-dir/api/${endpoint}/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
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
    const projectForm = document.getElementById('projectForm');
    if (projectForm) {
        projectForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('projects', this);
        });
    }

    // Стороны
    const participantForm = document.getElementById('participantForm');
    if (participantForm) {
        participantForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('participants', this);
        });
    }

    // Платежные системы
    const paymentSystemForm = document.getElementById('paymentSystemForm');
    if (paymentSystemForm) {
        paymentSystemForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('payment-systems', this);
        });
    }

    // Контрагенты
    const counterpartyForm = document.getElementById('counterpartyForm');
    if (counterpartyForm) {
        counterpartyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('counterparties', this);
        });
    }

    // Группы
    const groupForm = document.getElementById('groupForm');
    if (groupForm) {
        groupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('groups', this);
        });
    }

    // Частоты
    const frequencyForm = document.getElementById('frequencyForm');
    if (frequencyForm) {
        frequencyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('frequencies', this);
        });
    }


    // Тип потока
    const flowTypeForm = document.getElementById('flowTypeForm');
    if (flowTypeForm) {
        flowTypeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('flow-types', this);
        });
    }

    // Изменчивость
    const variabilityForm = document.getElementById('variabilityForm');
    if (variabilityForm) {
        variabilityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('variabilities', this);
        });
    }

    // Статьи
    const itemForm = document.getElementById('itemForm');
    if (itemForm) {
        itemForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem('items', this);
        });

        // Обработчик изменения типа потока для статей
        const flowTypeSelect = document.querySelector('#itemForm select[name="flow_type"]');
        if (flowTypeSelect) {
            flowTypeSelect.addEventListener('change', function(e) {
                updateVariabilityOptions(e.target.value);
            });
            
            // Инициализация состояния при загрузке
            const currentFlowType = flowTypeSelect.value;
            if (currentFlowType) {
                updateVariabilityOptions(currentFlowType);
            }
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

    // Для статей: фильтруем изменчивость по выбранному типу потока
    if (endpoint === 'items') {
        const selectedFlowType = data.flow_type;
        const variabilitySelect = document.getElementById('itemVariability');
        if (variabilitySelect) {
            const selectedOption = variabilitySelect.options[variabilitySelect.selectedIndex];
            const optionFlowType = selectedOption.getAttribute('data-flow-type');
            
            // Если выбранная изменчивость не соответствует типу потока, очищаем
            if (data.variability && optionFlowType !== selectedFlowType) {
                data.variability = '';
            }
        }
    }

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            return response.json().then(errorData => {
                // Обработка ошибок валидации
                const errorMessage = errorData.detail || 
                                   errorData.name || 
                                   errorData.non_field_errors || 
                                   'Ошибка сохранения';
                throw new Error(Array.isArray(errorMessage) ? errorMessage[0] : errorMessage);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при сохранении: ' + error.message);
    });
}

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

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('Analytics directory JS initialized');
    
    // Исправляем опечатку в кнопке отмены для формы изменчивости
    const variabilityCancelBtn = document.querySelector('#variabilityForm button[onclick*="categoryForm"]');
    if (variabilityCancelBtn) {
        variabilityCancelBtn.setAttribute('onclick', "clearForm('variabilityForm')");
    }
});