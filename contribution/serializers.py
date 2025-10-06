from rest_framework import serializers
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
        return data
    
class PlanningSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = Planning
        fields = [
            'id', 'date', 'project',
            'project_name', 'item', 'item_name',
            'payment_amount', 'frequency', 'frequency_display', 'comment',
        ]