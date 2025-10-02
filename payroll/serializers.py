from rest_framework import serializers
from .models import (
    Position, Department, Status, EmployeeType, PaymentType,
    Employee, Accrual, Payout
)

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

class EmployeeSerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source='position.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    employee_type_name = serializers.CharField(source='employee_type.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'position', 'position_name', 
            'department', 'department_name', 'status', 'status_name',
            'employee_type', 'employee_type_name', 'bank_name', 'card_number'
        ]



class AccrualSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Accrual
        fields = [
            'id', 'data', 'employee', 'employee_name', 'department', 'department_name',
            'project', 'project_name', 'hourly_pay', 'salary', 'addition_pay',
            'deduction', 'comment'
        ]

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
        
        # Проверка подкатегории
        if employee and department and employee.department != department:
            errors['employee'] = 'Выбранный сотрудник не принадлежит выбранному отделу'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs

class PayoutSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    payer_name = serializers.CharField(source='payer.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    payment_type_name = serializers.CharField(source='payment_type.name', read_only=True)

    class Meta:
        model = Payout
        fields = [
            'id', 'data', 'project', 'project_name', 'payer', 'payer_name',
            'recipient', 'recipient_name', 'department', 'department_name',
            'employee', 'employee_name', 'payment_type', 'payment_type_name',
            'amount', 'comment'
        ]

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
        
        # Проверка подкатегории
        if payer and recipient and recipient == payer:
            errors['recipient'] = 'Плательщик и получатель не могут быть одинаковыми'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs