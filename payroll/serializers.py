from rest_framework import serializers
from django.db.models import Sum, F, DecimalField
from .models import (
    Position, Department, Status, EmployeeType, PaymentType,
    Employee, Accrual, Payout
)

import locale

# Сериализаторы для справочников

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = '__all__'

class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = '__all__'

# Сериализатор для таблицы Сотрудники
class EmployeeSerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source='position.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    employee_type_name = serializers.CharField(source='employee_type.name', read_only=True)
    bank_name = serializers.CharField(allow_blank=True, required=False)
    card_number = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'position', 'position_name', 
            'department', 'department_name', 'status', 'status_name',
            'employee_type', 'employee_type_name', 'bank_name', 'card_number'
        ]


# Сериализатор для таблицы Начисления
class AccrualSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    # Новые вычисляемые поля
    hourly_sum_for_employee = serializers.SerializerMethodField()
    total_amount_to_pay = serializers.SerializerMethodField()
    monthly_period = serializers.SerializerMethodField()

    class Meta:
        model = Accrual
        fields = [
            'id', 'date', 'employee', 'employee_name', 'department', 'department_name',
            'project', 'project_name', 'hourly_pay', 'salary', 'addition_pay',
            'deduction', 'comment',  'hourly_sum_for_employee', 'total_amount_to_pay', 'monthly_period' 
        ]

    def get_hourly_sum_for_employee(self, obj):
        # если аннотированное поле есть (GET списка), используем его
        if hasattr(obj, 'hourly_sum_for_employee'):
            return obj.hourly_sum_for_employee or 0

        # иначе (POST/PUT/PATCH) считаем через ORM
        if obj.date and obj.department and obj.employee:
            return Accrual.objects.filter(
                date=obj.date,
                department=obj.department,
                employee=obj.employee
            ).aggregate(total=Sum('hourly_pay'))['total'] or 0

        # fallback
        return 0

    def get_total_amount_to_pay(self, obj):
        hourly_sum = self.get_hourly_sum_for_employee(obj) or 0
        salary = obj.salary or 0
        addition = obj.addition_pay or 0
        deduction = obj.deduction or 0
        return hourly_sum + salary + addition - deduction

    def get_monthly_period(self, obj):
        if not obj.date:
            return ""
        # locale.setlocale(locale.LC_TIME,'Russian_Russia') 
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8') 
        return obj.date.strftime("%B %y")
    
        # Проверка выполнения бизнес-правил
    def validate(self, attrs):
        # Комплексная проверка для всех HTTP-методов
        instance = getattr(self, 'instance', None)
        
        employee = attrs.get('employee')
        department = attrs.get('department')

        if instance:
            if employee is None:
                employee = instance.employee
            if department is None:
                department = instance.department
        
        errors = {}
        
        # Проверка сотрудника и отдела
        if employee and department and employee.department != department:
            errors['employee'] = 'Выбранный сотрудник не принадлежит выбранному отделу'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs

# Сериализатор для таблицы Выплаты
class PayoutSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    payer_name = serializers.CharField(source='payer.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    payment_type_name = serializers.CharField(source='payment_type.name', read_only=True)

    accrued_total_for_month = serializers.SerializerMethodField()
    net_amount_to_pay = serializers.SerializerMethodField()
    monthly_period = serializers.SerializerMethodField()
    accrued_total_for_all_time = serializers.SerializerMethodField()
    net_accrued_total_for_all_time = serializers.SerializerMethodField()

    class Meta:
        model = Payout
        fields = [
            'id', 'date', 'project', 'project_name', 'payer', 'payer_name',
            'recipient', 'recipient_name', 'department', 'department_name',
            'employee', 'employee_name', 'payment_type', 'payment_type_name',
            'amount', 'comment', 'accrued_total_for_month', 'net_amount_to_pay', 'monthly_period', 'accrued_total_for_all_time', 'net_accrued_total_for_all_time'
        ]

    def get_accrued_total_for_month(self, obj):
        # Если поле уже аннотировано (при GET), берём его
        if hasattr(obj, 'accrued_total_for_month'):
            return obj.accrued_total_for_month or 0

        # Если POST/PUT — считаем вручную
        if not obj.date or not obj.employee or not obj.department:
            return 0
        return Accrual.objects.filter(
            employee=obj.employee,
            department=obj.department,
            date__year=obj.date.year,
            date__month=obj.date.month
        ).aggregate(
            total=Sum(
                F('hourly_pay') + F('salary') + F('addition_pay') - F('deduction'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )['total'] or 0

    
    def get_net_amount_to_pay(self, obj):
        accrued = getattr(obj, 'accrued_total_for_month', None)
        if accrued is None:
            accrued = self.get_accrued_total_for_month(obj)

        total_paid = getattr(obj, 'total_paid_for_month', None)
        if total_paid is None and obj.date and obj.employee and obj.department:
            total_paid = Payout.objects.filter(
                employee=obj.employee,
                department=obj.department,
                date__year=obj.date.year,
                date__month=obj.date.month
            ).aggregate(
                total=Sum('amount', output_field=DecimalField(max_digits=20, decimal_places=2))
            )['total'] or 0

        return accrued - (total_paid or 0)
    
    def get_monthly_period(self, obj):
        if not obj.date:
            return ""
        # locale.setlocale(locale.LC_TIME,'Russian_Russia') 
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8') 
        return obj.date.strftime("%B %y")
    
    def get_accrued_total_for_all_time(self, obj):
        # Если поле уже аннотировано (при GET), берём его
        if hasattr(obj, 'accrued_total_for_all_time'):
            return obj.accrued_total_for_all_time or 0

        if obj.employee and obj.department:
            return Accrual.objects.filter(
                employee=obj.employee,
                department=obj.department
            ).aggregate(
                total=Sum(
                    F('hourly_pay') + F('salary') + F('addition_pay') - F('deduction'),
                    output_field=DecimalField(max_digits=20, decimal_places=2)
                )
            )['total'] or 0
        return 0
    
    def get_net_accrued_total_for_all_time(self, obj):
        accrued = getattr(obj, 'accrued_total_for_all_time', None)
        if accrued is None:
            accrued = self.get_accrued_total_for_all_time(obj)

        total_paid = getattr(obj, 'total_paid_for_all_time', None)
        if total_paid is None and obj.employee and obj.department:
            total_paid = Payout.objects.filter(
                employee=obj.employee,
                department=obj.department
            ).aggregate(
                total=Sum('amount', output_field=DecimalField(max_digits=20, decimal_places=2))
            )['total'] or 0

        if accrued == 0:
            return None
        return accrued - total_paid

        # Проверка выполнения бизнес-правил
    def validate(self, attrs):
        # Комплексная проверка для всех HTTP-методов
        instance = getattr(self, 'instance', None)
        
        payer = attrs.get('payer')
        recipient = attrs.get('recipient')

        if instance:
            if payer is None:
                payer = instance.payer
            if recipient is None:
                recipient = instance.recipient
        
        errors = {}
        
        # Проверка плательщика и получателя
        if payer and recipient and recipient == payer:
            errors['recipient'] = 'Плательщик и получатель не могут быть одинаковыми'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs