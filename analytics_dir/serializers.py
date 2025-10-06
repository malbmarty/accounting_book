from rest_framework import serializers
from .models import (
    Project, Participant, PaymentSystem,
    Counterparty, Group, Item
)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

class PaymentSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSystem
        fields = '__all__'

class CounterpartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    flow_type_display = serializers.CharField(source='get_flow_type_display', read_only=True)
    variability_display = serializers.CharField(source='get_variability_display', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'name',
            'group',
            'group_name',
            'flow_type',
            'flow_type_display',
            'variability',
            'variability_display',
        ]

    def validate(self, data):
        flow_type = data.get('flow_type', getattr(self.instance, 'flow_type', None))
        variability = data.get('variability', getattr(self.instance, 'variability', None))

        if flow_type == "income" and variability:
            raise serializers.ValidationError({
                "variability": "Поле «Постоянные/переменные» можно указывать только для расходов."
            })
        return data
