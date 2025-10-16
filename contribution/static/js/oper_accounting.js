// Загрузка таблицы оперативного учета 
function loadOperAcc(sortField = '', sortDirection = '') {
    // Формируем URL с параметрами сортировки
    let url = `/contribution/api/oper-acc-records/`;
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
        // Список всех колонок (новые id без table-body)
        const columns = {
        payment_date: document.getElementById('paymentDateColumn'),
        recognition_date: document.getElementById('recognitionDateColumn'),
        payer: document.getElementById('payerColumn'),
        recipient: document.getElementById('recipientColumn'),
        item: document.getElementById('itemColumn'),
        payment_system: document.getElementById('paymentSystemColumn'),
        project: document.getElementById('projectColumn'),
        payment_amount: document.getElementById('paymentAmountColumn'),
        counterparty: document.getElementById('counterpartyColumn'),
        commission_amount: document.getElementById('commissionAmountColumn'),
        comment: document.getElementById('commentColumn'),
        edit: document.getElementById('editColumn'),
        delete: document.getElementById('deleteColumn'),
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

    // Очищаем содержимое колонок (кроме заголовков)
    Object.values(columns).forEach(col => {
        if (!col) return;
        // Удаляем все .table-cell, оставляя .table-head
        col.querySelectorAll('.table-cell').forEach(cell => cell.remove());
    });

    

    // Заполняем колонки данными
    data.forEach(record => {
        let [year, month, day] = record.payment_date.split('-');
        let formattedPaymentDate = `${day}.${month}.${year}`;

        [year, month, day] = record.recognition_date.split('-');
        let formattedRecognitionDate = `${day}.${month}.${year}`;

        columns.payment_date.innerHTML += `
          <div class="table-cell table-cell--payment-date">
            <span class="cell-title" title="${formattedPaymentDate}">${formattedPaymentDate}</span>  
          </div>
        `;

        columns.recognition_date.innerHTML += `
          <div class="table-cell table-cell--recognition-date">
            <span class="cell-title" title="${formattedRecognitionDate}">${formattedRecognitionDate}</span>  
          </div>
        `;

        columns.payer.innerHTML += `
          <div class="table-cell table-cell--payer">
            <span class="cell-title" title="${record.payer_name}">${record.payer_name}</span>  
          </div>
        `;

        columns.recipient.innerHTML += `
          <div class="table-cell table-cell--recipient">
            <span class="cell-title" title="${record.payer_name}">${record.recipient_name}</span>  
          </div>
        `;

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

        columns.payment_system.innerHTML += `
          <div class="table-cell table-cell--payment-system">
            <span class="cell-title" title="${record.payment_system_name}">${record.payment_system_name}</span>  
          </div>
        `;

        columns.project.innerHTML += `
          <div class="table-cell table-cell--project">
            <span class="cell-title" title="${record.project_name}">${record.project_name}</span>
          </div>
        `;

        columns.payment_amount.innerHTML += `
          <div class="table-cell table-cell--payment-amount">
            <span class="cell-title" title="${record.payment_amount}">${record.payment_amount}</span>
          </div>
        `;

        columns.counterparty.innerHTML += `
          <div class="table-cell table-cell--counterparty">
            <span class="cell-title" title="${record.counterparty_name}">${record.counterparty_name}</span>
          </div>
        `;

        columns.commission_amount.innerHTML += `
          <div class="table-cell table-cell--commission-amount">
            <span class="cell-title" title="${record.commission_amount}">${record.commission_amount}</span>
          </div>
        `;

        columns.comment.innerHTML += `
          <div class="table-cell table-cell--comment">
            <span class="cell-title" title="${record.comment}">${record.comment}</span>
          </div>
        `;
        

        columns.edit.innerHTML += `
          <div class="table-cell table-cell--edit">
            <button class="edit-button" type="button" onclick="editOperAcc(${record.id})">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                    xmlns="http://www.w3.org/2000/svg">
                <path d="M7.33325 1.3335H5.99992C2.66659 1.3335 1.33325 2.66684 1.33325 6.00017V10.0002C1.33325 13.3335 2.66659 14.6668 5.99992 14.6668H9.99992C13.3333 14.6668 14.6666 13.3335 14.6666 10.0002V8.66684M9.93992 2.76684C10.3866 4.36017 11.6333 5.60684 13.2333 6.06017M10.6933 2.0135L5.43992 7.26684C5.23992 7.46684 5.03992 7.86017 4.99992 8.14684L4.71325 10.1535C4.60659 10.8802 5.11992 11.3868 5.84659 11.2868L7.85325 11.0002C8.13325 10.9602 8.52659 10.7602 8.73325 10.5602L13.9866 5.30684C14.8933 4.40017 15.3199 3.34684 13.9866 2.0135C12.6533 0.680168 11.5999 1.10684 10.6933 2.0135Z"
                        stroke="#3C56FF" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
          </div>
        `;

        columns.delete.innerHTML += `
          <div class="table-cell table-cell--delete">
            <button class="delete-button" type="button" onclick="deleteOperAcc(${record.id})">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 3.98634C11.78 3.76634 9.54667 3.65301 7.32 3.65301C6 3.65301 4.68 3.71967 3.36 3.85301L2 3.98634M5.66667 3.31301L5.81333 2.43967C5.92 1.80634 6 1.33301 7.12667 1.33301H8.87333C10 1.33301 10.0867 1.83301 10.1867 2.44634L10.3333 3.31301M12.5667 6.09301L12.1333 12.8063C12.06 13.853 12 14.6663 10.14 14.6663H5.86C4 14.6663 3.94 13.853 3.86667 12.8063L3.43333 6.09301M6.88667 10.9997H9.10667M6.33333 8.33301H9.66667" stroke="#BD0A37" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
          </div>
        `;
    });

      // выравниваем высоту строк между колонками
      equalizeRowHeights();
    });
}

// Удаление транзакции
let deleteId = null;

// Открытие модалки удаления
function deleteOperAcc(id) {
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
    fetch(`/contribution/api/oper-acc-records/${deleteId}/`, { method: 'DELETE' })
      .then(() => {
        document.getElementById('deleteConfirmModal').style.display = 'none';
        document.getElementById('modalBackdrop').style.display = 'none';
        deleteId = null;
        loadOperAcc();
      });
  }
});

// Создание новой записи начисления
document.getElementById('createOperAccForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/contribution/api/oper-acc-records/', {
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
        document.getElementById('createOperAccModal').style.display = 'none';
        document.getElementById('modalBackdrop').style.display = 'none';
        loadOperAcc()
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
function editOperAcc(id) {
    editId = id;
    
    // Загружаем данные начисления
    fetch(`/contribution/api/oper-acc-records/${id}/`)
    .then(response => response.json())
    .then(record => {
        // Заполняем форму данными начисления
        document.querySelector('#editOperAccForm input[name="payment_date"]').value = record.payment_date || '';
        document.querySelector('#editOperAccForm input[name="recognition_date"]').value = record.recognition_date || '';
        document.querySelector('#editOperAccForm input[name="payment_amount"]').value = record.payment_amount || '';
        document.querySelector('#editOperAccForm input[name="commission_amount"]').value = record.commission_amount || '';
        document.querySelector('#editOperAccForm textarea[name="comment"]').value = record.comment || '';
        

        // Обновляем кастомные dropdown'ы в форме редактирования
        const updateDropdown = (name, value, text) => {
          const dropdown = document.querySelector(`#editOperAccForm .dropdown[data-name="${name}"]`);
          if (dropdown) {
            dropdown.querySelector('input[type="hidden"]').value = value;
            dropdown.querySelector('.dropdown-toggle').textContent = text;
          }
        };

        // Заполняем dropdown'ы
        updateDropdown('payer', record.payer, record.payer_name);
        updateDropdown('recipient', record.recipient, record.recipient_name);
        updateDropdown('item', record.item, record.item_name);
        updateDropdown('payment_system', record.payment_system, record.payment_system_name);
        updateDropdown('project', record.project, record.project_name);
        updateDropdown('counterparty', record.counterparty, record.counterparty_name);
        

        // Показываем модальное окно
        const modal = document.getElementById('editOperAccModal');
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
document.getElementById('editOperAccForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    fetch(`/contribution/api/oper-acc-records/${editId}/`, {
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
        document.getElementById('editOperAccModal').style.display = 'none';
        document.getElementById('modalBackdrop').style.display = 'none';
        editId = null;
        loadOperAcc();
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
    const createModal = document.getElementById('createOperAccModal');
    const editModal = document.getElementById('editOperAccModal');
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
          loadOperAcc(value, direction, document.querySelector('input[name="filter"]').value);
        }

        if (dropdownName === 'filter') {
          loadOperAcc(
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
    loadOperAcc();
    setupModalHandlers();
    setupDropdowns();
    
    // Открытие модального окна создания
    document.querySelector('.new-record-button').addEventListener('click', function() {
        document.getElementById('createOperAccModal').style.display = 'block';
        document.getElementById('modalBackdrop').style.display = 'block';
    });
});