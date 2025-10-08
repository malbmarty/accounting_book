from django.shortcuts import render
from rest_framework import viewsets
from django.views.generic import TemplateView

from .serializers import (
    ProjectSerializer, ParticipantSerializer, PaymentSystemSerializer,
    CounterpartySerializer, GroupSerializer, FlowTypeSerializer, 
    VariabilitySerializer, ItemSerializer, FrequencySerializer 
)
from .models import (
    Project, Participant, PaymentSystem, 
    Counterparty, Group, FlowType, 
    Variability, Item, Frequency
)

# HTML Views
class AnalyticsDirPageView(TemplateView):
    template_name = 'analytics_dir/analytics_dir.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем все данные из базы и передаем в шаблон
        context['projects'] = Project.objects.all()
        context['participants'] = Participant.objects.all()
        context['payment_systems'] = PaymentSystem.objects.all()
        context['counterparties'] = Counterparty.objects.all()
        context['groups'] = Group.objects.all()
        context['frequencies'] = Frequency.objects.all()
        context['flow_types'] = FlowType.objects.all()
        context['variabilities'] = Variability.objects.all()
        context['items'] = Item.objects.all()

        return context


# API 
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

class PaymentSystemViewSet(viewsets.ModelViewSet):
    queryset = PaymentSystem.objects.all()
    serializer_class = PaymentSystemSerializer

class CounterpartyViewSet(viewsets.ModelViewSet):
    queryset = Counterparty.objects.all()
    serializer_class = CounterpartySerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class FrequencyViewSet(viewsets.ModelViewSet):
    queryset = Frequency.objects.all()
    serializer_class = FrequencySerializer

class FlowTypeViewSet(viewsets.ModelViewSet):
    queryset = FlowType.objects.all()
    serializer_class = FlowTypeSerializer

class VariabilityViewSet(viewsets.ModelViewSet):
    queryset = Variability.objects.all()
    serializer_class = VariabilitySerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer