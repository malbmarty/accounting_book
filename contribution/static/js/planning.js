function loadPlanning(sortField = '', sortDirection = '') {
    let url = `/contribution/api/planning-records/`;
    const params = new URLSearchParams();

    if (sortField) {
        params.append('ordering', sortDirection === 'desc' ? `-${sortField}` : sortField);
    }

    const queryString = params.toString();
    if (queryString) {
        url += `?${queryString}`;
    }

    fetch(url)
    .then(response => response.json())
    .then(data => {
        const columns = {
            date: document.getElementById('dateColumn'),
            project: document.getElementById('projectColumn'),
            item: document.getElementById('itemColumn'),
            payment_amount: document.getElementById('paymentAmountColumn'),
            frequency: document.getElementById('frequencyColumn'),
            last_date: document.getElementById('lastDateColumn'),
            flow_type: document.getElementById('flowTypeColumn'),
            pay2: document.getElementById('pay2Column'),
            pay3: document.getElementById('pay3Column'),
            pay4: document.getElementById('pay4Column'),
            pay5: document.getElementById('pay5Column'),
            pay6: document.getElementById('pay6Column'),
            pay7: document.getElementById('pay7Column'),
            pay8: document.getElementById('pay8Column'),
            pay9: document.getElementById('pay9Column'),
            pay10: document.getElementById('pay10Column'),
            pay11: document.getElementById('pay11Column'),
            pay12: document.getElementById('pay12Column'),
            total: document.getElementById('totalColumn'),
            edit: document.getElementById('editColumn'),
            delete: document.getElementById('deleteColumn')
        };

        // Получаем цвета из data-attribute
        const itemsColorsData = document.getElementById('itemsColorsData');
        let itemColors = {};
        
        if (itemsColorsData) {
            try {
                // Для варианта с data-attribute
                const colorsJson = itemsColorsData.getAttribute('data-colors');
                if (colorsJson) {
                    itemColors = JSON.parse(colorsJson);
                }
            } catch (e) {
                console.warn('Не удалось распарсить цвета отделов:', e);
            }
        }

        // Очищаем колонки
        Object.values(columns).forEach(col => {
            if (!col) return;
            col.querySelectorAll('.table-cell').forEach(cell => cell.remove());
        });

        data.forEach(record => {
            // Форматирование дат
            const formatDate = (dateStr) => {
                if (!dateStr) return '';
                const [year, month, day] = dateStr.split('-');
                return `${day}.${month}.${year}`;
            };

            // Дата
            columns.date.innerHTML += `
                <div class="table-cell table-cell--date">
                    <span class="cell-title" title="${formatDate(record.date)}">${formatDate(record.date)}</span>
                </div>
            `;

            // Проект
            columns.project.innerHTML += `
                <div class="table-cell table-cell--project">
                    <span class="cell-title" title="${record.project_name}">${record.project_name}</span>
                </div>
            `;

            // Статья с цветом
            // Используем стабильные цвета из data-attribute
            let colors = itemColors[record.item_name] || { 
                bg: 'rgba(128, 128, 128, 0.2)', 
                text: '#808080' 
            };
            columns.item.innerHTML += `
                <div class="table-cell table-cell--item">
                    <div class="cell-depart" style="background: ${colors.bg}; color: ${colors.text}">
                        <svg width="8" height="8" viewBox="0 0 8 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="3" cy="3" r="3" fill="${colors.text}"/>
                        </svg>
                        <span class="cell-title" title="${record.item_name}">${record.item_name}</span>
                    </div>
                </div>
            `;

            // Сумма платежа
            columns.payment_amount.innerHTML += `
                <div class="table-cell table-cell--payment-amount">
                    <span class="cell-title" title="${record.payment_amount}">${record.payment_amount}</span>
                </div>
            `;

            // Частота
            columns.frequency.innerHTML += `
                <div class="table-cell table-cell--frequency">
                    <span class="cell-title" title="${record.frequency_name}">${record.frequency_name}</span>
                </div>
            `;

            // Ежемесячно до даты
            columns.last_date.innerHTML += `
                <div class="table-cell table-cell--last-date">
                    <span class="cell-title" title="${formatDate(record.last_payment_date)}">${formatDate(record.last_payment_date)}</span>
                </div>
            `;

            // Приход/Расход
            columns.flow_type.innerHTML += `
                <div class="table-cell table-cell--flow-type">
                    <span class="cell-title" title="${record.flow_type_name}">${record.flow_type_name}</span>
                </div>
            `;

            // Платежи №2–№12
            for (let i = 0; i < 11; i++) {
                const payCol = columns[`pay${i+2}`];
                let formattedPay = '';
                const paymentDate = record.payment_dates[i];
                if (paymentDate) formattedPay = formatDate(paymentDate);
                if (payCol) {
                    payCol.innerHTML += `
                        <div class="table-cell table-cell--pay">
                            <span class="cell-title" title="${formattedPay}">${formattedPay}</span>
                        </div>
                    `;
                }
            }

            // Сумма всех платежей
            columns.total.innerHTML += `
                <div class="table-cell table-cell--total">
                    <span class="cell-title" title="${record.total_payment}">${record.total_payment}</span>
                </div>
            `;

            // Редактировать
            columns.edit.innerHTML += `
                <div class="table-cell table-cell--edit">
                    <button class="edit-button" type="button" onclick="editPlanning(${record.id})">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M7.33325 1.3335H5.99992C2.66659 1.3335 1.33325 2.66684 1.33325 6.00017V10.0002C1.33325 13.3335 2.66659 14.6668 5.99992 14.6668H9.99992C13.3333 14.6668 14.6666 13.3335 14.6666 10.0002V8.66684M9.93992 2.76684C10.3866 4.36017 11.6333 5.60684 13.2333 6.06017M10.6933 2.0135L5.43992 7.26684C5.23992 7.46684 5.03992 7.86017 4.99992 8.14684L4.71325 10.1535C4.60659 10.8802 5.11992 11.3868 5.84659 11.2868L7.85325 11.0002C8.13325 10.9602 8.52659 10.7602 8.73325 10.5602L13.9866 5.30684C14.8933 4.40017 15.3199 3.34684 13.9866 2.0135C12.6533 0.680168 11.5999 1.10684 10.6933 2.0135Z"
                                stroke="#3C56FF" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            `;

            // Удалить
            columns.delete.innerHTML += `
                <div class="table-cell table-cell--delete">
                    <button class="delete-button" type="button" onclick="deletePlanning(${record.id})">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M14 3.98634C11.78 3.76634 9.54667 3.65301 7.32 3.65301C6 3.65301 4.68 3.71967 3.36 3.85301L2 3.98634M5.66667 3.31301L5.81333 2.43967C5.92 1.80634 6 1.33301 7.12667 1.33301H8.87333C10 1.33301 10.0867 1.83301 10.1867 2.44634L10.3333 3.31301M12.5667 6.09301L12.1333 12.8063C12.06 13.853 12 14.6663 10.14 14.6663H5.86C4 14.6663 3.94 13.853 3.86667 12.8063L3.43333 6.09301M6.88667 10.9997H9.10667M6.33333 8.33301H9.66667" stroke="#BD0A37" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            `;
        });

        equalizeRowHeights();
    });
}


// Удаление транзакции
let deleteId = null;

// Открытие модалки удаления
function deletePlanning(id) {
  const modal = document.getElementById('deleteConfirmModal');
  modal.style.display = 'flex';
  const backdrop = document.getElementById('modalBackdrop');
  backdrop.style.display = 'block'
  deleteId = id;
}

// Кнопка "Отмена"
document.getElementById('cancelDelete').addEventListener('click', () => {
  document.getElementById('deleteConfirmModal').style.display = 'none';
  document.getElementById('modalBackdrop').style.display = 'none';
  deleteId = null;
});

// Кнопка "Удалить"
document.getElementById('confirmDelete').addEventListener('click', () => {
  if (deleteId) {
    fetch(`/contribution/api/planning-records/${deleteId}/`, { method: 'DELETE' })
      .then(() => {
        document.getElementById('deleteConfirmModal').style.display = 'none';
        document.getElementById('modalBackdrop').style.display = 'none';
        deleteId = null;
        loadPlanning();
      });
  }
});

// Создание новой записи начисления
document.getElementById('createPlanningForm').addEventListener('submit', function(e) {
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
        this.reset(); // Очищаем форму
        this.querySelectorAll('.dropdown').forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const hiddenInput = dropdown.querySelector('input[type="hidden"]');
            
            // Сброс значения
            if (hiddenInput) hiddenInput.value = '';

            // Восстановление исходного текста
            const placeholder = toggle.dataset.placeholder || 'Выберите из списка';
            toggle.textContent = placeholder;
        });
        // Закрываем модальное окно
        document.getElementById('createPlanningModal').style.display = 'none';
        document.getElementById('modalBackdrop').style.display = 'none';
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

// Редактирование начисления
let editId = null;

// Открытие модалки редактирования с загрузкой данных
function editPlanning(id) {
    editId = id;
    
    // Загружаем данные начисления
    fetch(`/contribution/api/planning-records/${id}/`)
    .then(response => response.json())
    .then(record => {
        // Заполняем форму данными начисления
        document.querySelector('#editPlanningForm input[name="date"]').value = record.date || '';
        document.querySelector('#editPlanningForm input[name="payment_amount"]').value = record.payment_amount || '';
        document.querySelector('#editPlanningForm textarea[name="comment"]').value = record.comment || '';
        

        // Обновляем кастомные dropdown'ы в форме редактирования
        const updateDropdown = (name, value, text) => {
          const dropdown = document.querySelector(`#editPlanningForm .dropdown[data-name="${name}"]`);
          if (dropdown) {
            dropdown.querySelector('input[type="hidden"]').value = value;
            dropdown.querySelector('.dropdown-toggle').textContent = text;
          }
        };

        // Заполняем dropdown'ы
        updateDropdown('item', record.item, record.item_name);
        updateDropdown('project', record.project, record.project_name);
        updateDropdown('frequency', record.frequency, record.frequency_name);
        

        // Показываем модальное окно
        const modal = document.getElementById('editPlanningModal');
        modal.style.display = 'flex';
        const backdrop = document.getElementById('modalBackdrop');
        backdrop.style.display = 'block';
    })
    .catch(error => {
        console.error('Ошибка при загрузке данных начисления:', error);
        alert('Не удалось загрузить данные начисления');
    });
}

// Обработчик формы редактирования
document.getElementById('editPlanningForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    fetch(`/contribution/api/planning-records/${editId}/`, {
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
        // Закрываем модальное окно
        document.getElementById('editPlanningModal').style.display = 'none';
        document.getElementById('modalBackdrop').style.display = 'none';
        editId = null;
        loadPlanning();
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

// Закрытие модальных окон
function setupModalHandlers() {
    const backdrop = document.getElementById('modalBackdrop');
    const createModal = document.getElementById('createPlanningModal');
    const editModal = document.getElementById('editPlanningModal');
    const deleteModal = document.getElementById('deleteConfirmModal');
    
    // Кнопки закрытия для всех модальных окон
    document.querySelectorAll('.modal-close, .button-cancel').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                backdrop.style.display = 'none';
            }
        });
    });
    
    // Закрытие по клику на backdrop
    backdrop.addEventListener('click', function() {
        createModal.style.display = 'none';
        editModal.style.display = 'none';
        deleteModal.style.display = 'none';
        backdrop.style.display = 'none';
    });
    
    // Закрытие по клику вне модального окна
    window.addEventListener('click', function(event) {
        if (event.target === createModal) {
            createModal.style.display = 'none';
            backdrop.style.display = 'none';
        }
        if (event.target === editModal) {
            editModal.style.display = 'none';
            backdrop.style.display = 'none';
        }
        if (event.target === deleteModal) {
            deleteModal.style.display = 'none';
            backdrop.style.display = 'none';
        }
    });
}

// Универсальная логика кастомных dropdown'ов с поддержкой сортировки
function setupDropdowns() {
  document.querySelectorAll('.dropdown').forEach(dropdown => {
    const toggle = dropdown.querySelector('.dropdown-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');
    const hiddenInput = dropdown.querySelector('input[type="hidden"]');
    const items = dropdown.querySelectorAll('.dropdown-item');
    const dropdownName = dropdown.dataset.name;

    toggle.addEventListener('click', () => {
      menu.classList.toggle('open');
      toggle.classList.toggle('active');
    });

    items.forEach(item => {
      item.addEventListener('click', () => {
        const value = item.dataset.value;
        const text = item.textContent.trim();

        hiddenInput.value = value;
        toggle.textContent = text;

        menu.classList.remove('open');
        toggle.classList.remove('active');

        if (dropdownName === 'sort') {
          const direction = item.dataset.direction || 'asc';
          document.querySelector('input[name="sort_direction"]').value = direction;
          loadPlanning(value, direction, document.querySelector('input[name="filter"]').value);
        }

        if (dropdownName === 'filter') {
          loadPlanning(
            document.querySelector('input[name="column_name"]').value,
            document.querySelector('input[name="sort_direction"]').value,
            value
          );
        }
      });
    });

    document.addEventListener('click', e => {
      if (!dropdown.contains(e.target)) {
        menu.classList.remove('open');
        toggle.classList.remove('active');
      }
    });
  });
}



// Загружаем данные при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadPlanning();
    setupModalHandlers();
    setupDropdowns();
    
    // Открытие модального окна создания
    document.querySelector('.new-record-button').addEventListener('click', function() {
        document.getElementById('createPlanningModal').style.display = 'block';
        document.getElementById('modalBackdrop').style.display = 'block';
    });
});