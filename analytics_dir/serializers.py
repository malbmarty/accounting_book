from rest_framework import serializers
from .models import (
    Project, Participant, PaymentSystem,
    Counterparty, Group, Item, FlowType, Variability
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

class FlowTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowType
        fields = '__all__'

class VariabilitySerializer(serializers.ModelSerializer):
    flow_type_name = serializers.CharField(source='flow_type.name', read_only=True)
    
    class Meta:
        model = Variability
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    flow_type_name = serializers.CharField(source='flow_type.name', read_only=True)
    variability_name = serializers.CharField(source='variability.name', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'name',
            'group',
            'group_name',
            'flow_type',
            'flow_type_name',
            'variability',
            'variability_name',
        ]

    def validate(self, data):
        """
        Проверяет, что выбранная изменчивость соответствует типу потока.
        """
        flow_type = data.get('flow_type', getattr(self.instance, 'flow_type', None))
        variability = data.get('variability', getattr(self.instance, 'variability', None))

        if variability and variability.flow_type != flow_type:
            raise serializers.ValidationError({
                "variability": "Тип изменчивости не соответствует выбранному типу потока."
            })
        return data
