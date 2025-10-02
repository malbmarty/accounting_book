from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class EmployeeType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class PaymentType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Employee(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    position = models.ForeignKey(Position, on_delete=models.PROTECT, verbose_name="Должность")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name="Отдел")
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name="Статус сотрудника")
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.PROTECT, verbose_name="Тип сотрудника")
    bank_name = models.CharField(max_length=150, verbose_name="Банк")
    card_number = models.CharField(max_length=20, verbose_name="Номер карты")

    def __str__(self):
        return self.full_name

class Accrual(models.Model):
    data = models.DateField(verbose_name="Дата начисления")
    employee =  models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Сотрудник")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name="Отдел")
    project = models.ForeignKey('analytics_dir.Project', on_delete=models.PROTECT, verbose_name="Проект")
    hourly_pay = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank = True, verbose_name="Почасовая")
    salary = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank = True, verbose_name="Оклад")
    addition_pay = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank = True, verbose_name="Премия/доплаты")
    deduction = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank = True, verbose_name="Возвраты/вычеты")
    comment = models.CharField(max_length=100, null=True, blank=True, verbose_name="Комментарий")

    # Проверка выполнения бизнес-правил
    def clean(self):
        # Проверка, что сотрудник принадлежит выбранному отделу
        if self.employee.department != self.department:
            raise ValidationError({
                'employee': 'Выбранный сотрудник не принадлежит выбранному отделу'
            })
    
    def save(self, *args, **kwargs):
        """Переопределение save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)

class Payout(models.Model):
    data = models.DateField(verbose_name="Дата ОДДС")
    project = models.ForeignKey('analytics_dir.Project', on_delete=models.PROTECT, verbose_name="Проект")
    payer = models.ForeignKey(
        'analytics_dir.Participant', 
        on_delete=models.PROTECT, 
        verbose_name="Плательщик ОТ КУДА", 
        related_name='payouts_as_payer'
        )
    recipient = models.ForeignKey(
        'analytics_dir.Participant', 
        on_delete=models.PROTECT, 
        verbose_name="Получатель КУДА", 
        related_name='payouts_as_recipient'
        )
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name="Отдел")
    employee =  models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Сотрудник")
    payment_type = models.ForeignKey(PaymentType, on_delete=models.PROTECT, verbose_name="Тип выплаты")
    amount = models.DecimalField(
        decimal_places=2, 
        max_digits=20, 
        validators=[MinValueValidator(0.01)], 
        verbose_name="Сумма выплаты")
    comment = models.CharField(max_length=100, null=True, blank=True, verbose_name="Комментарий")

    # Проверка выполнения бизнес-правил
    def clean(self):
        
        if self.payer == self.recipient:
            raise ValidationError({
                'recipient': 'Плательщик и получатель не могут быть одинаковыми'
                })
        
    def save(self, *args, **kwargs):
        """Переопределение save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)


