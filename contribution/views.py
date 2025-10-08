from django.shortcuts import render, redirect
from rest_framework import viewsets, filters
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django_filters import FilterSet, DateFilter
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    OperationalAccountingSerializer, PlanningSerializer
)

from .models import (
    OperationalAccounting, Planning
)
from analytics_dir.models import (
        Project, Participant, Frequency,
        Item, PaymentSystem, Counterparty
)

# Страница с таблицей Оперативный учет
class OperAccountingPageView(TemplateView):
    template_name = 'contribution/oper_accounting.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['participants'] = Participant.objects.all()
        context['items'] = Item.objects.all()
        context['payment_systems'] = PaymentSystem.objects.all()
        context['projects'] = Project.objects.all()
        context['counterparties'] = Counterparty.objects.all()

        return context
    
# Страница с формой изменения записи в таблице Оперативный учет
class EditOperAccountingPageView(TemplateView):
    template_name = 'contribution/edit_oper_accounting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record_id = self.kwargs.get('pk')
        
        # Получаем транзакцию или возвращаем 404
        record = get_object_or_404(OperationalAccounting, id=record_id)
        
        # Сериализуем данные транзакции
        serializer = OperationalAccountingSerializer(record)
        
        # Добавляем данные в контекст
        context['record'] = serializer.data
        context['payment_date'] = record.payment_date.strftime('%Y-%m-%d')
        context['recognition_date'] = record.recognition_date.strftime('%Y-%m-%d')
        context['participants'] = Participant.objects.all()
        context['items'] = Item.objects.all()
        context['payment_systems'] = PaymentSystem.objects.all()
        context['projects'] = Project.objects.all()
        context['counterparties'] = Counterparty.objects.all()
        

        return context
    
# Страница с таблицей Планирование
class PlanningPageView(TemplateView):
    template_name = 'contribution/planning.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['items'] = Item.objects.all()
        context['projects'] = Project.objects.all()
        context['frequency_choices'] = Frequency.objects.all()

        return context
    
# Страница с формой изменения записи в таблице Планирование
class EditPlanningPageView(TemplateView):
    template_name = 'contribution/edit_planning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record_id = self.kwargs.get('pk')
        
        # Получаем транзакцию или возвращаем 404
        record = get_object_or_404(Planning, id=record_id)
        
        # Сериализуем данные транзакции
        serializer = PlanningSerializer(record)
        
        # Добавляем данные в контекст
        context['record'] = serializer.data
        context['date'] = record.date.strftime('%Y-%m-%d')
        context['items'] = Item.objects.all()
        context['projects'] = Project.objects.all()
        context['frequency_choices'] = Frequency.objects.all()

        return context

class OperAccountingViewSet(viewsets.ModelViewSet):
    queryset = OperationalAccounting.objects.all()
    serializer_class = OperationalAccountingSerializer

class PlanningViewSet(viewsets.ModelViewSet):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer