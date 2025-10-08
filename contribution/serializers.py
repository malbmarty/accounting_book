from rest_framework import serializers
from dateutil.relativedelta import relativedelta
from .models import (
    OperationalAccounting, Planning
)

class OperationalAccountingSerializer(serializers.ModelSerializer):
    payer_name = serializers.CharField(source='payer.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    payment_system_name = serializers.CharField(source='payment_system.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    counterparty_name = serializers.CharField(source='counterparty.name', read_only=True)

    class Meta:
        model = OperationalAccounting
        fields = [
            'id', 'payment_date', 'recognition_date',
            'payer', 'payer_name', 'recipient', 'recipient_name',
            'item', 'item_name', 'payment_system',
            'payment_system_name', 'project',
            'project_name', 'payment_amount', 'counterparty',
            'counterparty_name', 'commission_amount', 'comment',
        ]

    def validate(self, data):
        # Проверяет, что хотя бы одно из полей даты заполнено.
        payment_date = data.get('payment_date') or getattr(self.instance, 'payment_date', None)
        recognition_date = data.get('recognition_date') or getattr(self.instance, 'recognition_date', None)

        if not payment_date and not recognition_date:
            raise serializers.ValidationError({
                "non_field_errors": ["Необходимо указать хотя бы одну из дат: 'Дата платежа (ОДДС)' или 'Дата признания (ОПУ)'."]  
            })
        
        payer = data.get('payer') or getattr(self.instance, 'payer', None)
        recipient = data.get('recipient') or getattr(self.instance, 'recipient', None)

        if payer and recipient and payer == recipient:
            raise serializers.ValidationError({
                "non_field_errors": ["Плательщик и получатель не могут совпадать."]
            })
        return data
    
class PlanningSerializer(serializers.ModelSerializer):
    frequency_name = serializers.CharField(source='frequency.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    last_payment_date = serializers.SerializerMethodField()
    flow_type_name = serializers.SerializerMethodField()
    payment_dates = serializers.SerializerMethodField()
    total_payment = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        fields = [
            'id', 'date', 'project',
            'project_name', 'item', 'item_name',
            'payment_amount', 'frequency', 'frequency_name', 'comment',
            'last_payment_date', 'flow_type_name', 'payment_dates', 'total_payment'
        ]

    def get_last_payment_date(self, obj):
    
        # Возвращает дату последнего платежа 
        # Если 'разово' — возвращает исходную дату
        
        freq_name = obj.frequency.name.strip().lower()
        if freq_name == "разово":
            return obj.date

        try:
            months = int(freq_name)
            return obj.date + relativedelta(months=months - 1)
        except ValueError:
            # если в Frequency указано что-то странное, возвращаем исходную дату
            return obj.date
        
    def get_flow_type_name(self, obj):
        return obj.item.flow_type.name
    
    def get_payment_dates(self, obj):

        # Возвращает список из 12 элементов,
        # заполняя только количество, указанное в frequency
        freq_name = obj.frequency.name.strip().lower()
        payments = [None] * 12

        if freq_name == "разово":
            return payments  # нет повторов

        try:
            months = int(freq_name)
        except ValueError:
            return payments  # неверное значение частоты

        # Генерируем даты повторов, начиная со второго платежа
        for i in range(1, min(months, 13)):
            payments[i-1] = obj.date + relativedelta(months=i)

        return payments
    
    def get_total_payment(self, obj):
        freq_name = obj.frequency.name.strip().lower()
        if freq_name == "разово":
            count = 1
        else:
            try:
                count = int(freq_name)
            except ValueError:
                count = 1
        return obj.payment_amount * count