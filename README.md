# Приложение для бухгалтерского учета Accounting book

## Описание приложений
payroll - зарплатная ведомость
analytics_dir - справочник для Аналитики

### API для payroll:
    Должности: http://127.0.0.1:8000/payroll/api/positions/
    Отделы: http://127.0.0.1:8000/payroll/api/departments/
    Статусы: http://127.0.0.1:8000/payroll/api/statuses/
    Типы сотрудников: http://127.0.0.1:8000/payroll/api/employee-types/
    Типы выплаты: http://127.0.0.1:8000/payroll/api/payment-types/

### API для analytics_dir:
    Проекты: http://127.0.0.1:8000/analytics-dir/api/projects/
    Стороны (Плательщик/получатель): http://127.0.0.1:8000/analytics-dir/api/participants/
### Установка и запуск
1. Клонировать репозиторий:
   ```
   git clone https://github.com/malbmarty/accounting_book.git
   cd accounting_book

2. Создать и активировать вирутальное окружение:
    ```
    python -m venv venv
    source venv/bin/activate       # Linux / macOS
    venv\Scripts\activate          # Windows

3. Установить зависимости:
    ```
    pip install -r requirements.txt
4. Применить миграции:
    ```
    python manage.py migrate
  
5. Запустить сервер:
    ```
    python manage.py runserver
    ```