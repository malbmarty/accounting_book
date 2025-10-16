from django.shortcuts import render, redirect
from rest_framework import viewsets, filters
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django_filters import FilterSet, DateFilter
from django_filters.rest_framework import DjangoFilterBackend

from payroll.services.department_color import get_all_departments_colors 

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
        
        items = Item.objects.all()
        context['participants'] = Participant.objects.all()
        context['items'] = items
        context['payment_systems'] = PaymentSystem.objects.all()
        context['projects'] = Project.objects.all()
        context['counterparties'] = Counterparty.objects.all()

        context['column_names'] = [
            {'field': 'payment_date', 'display': 'По дате ОДДС'},
            {'field': 'recognition_date', 'display': 'По дате ОПУ'},
            {'field': 'payer__name', 'display': 'По плательщику'},
            {'field': 'recipient__name', 'display': 'По получателю'},
            {'field': 'item_name', 'display': 'По статье'},
            {'field': 'payment_system_name', 'display': 'По платежной системе'},
            {'field': 'project_name', 'display': 'По проекту'},
            {'field': 'payment_amount', 'display': 'По сумме платежа'},
            {'field': 'counterparty_name', 'display': 'По контрагенту'},
            {'field': 'commission_amount', 'display': 'По сумме комиссии'},
        ]
        context['items_colors'] = get_all_departments_colors(items)

        return context
    
    
# Страница с таблицей Планирование
class PlanningPageView(TemplateView):
    template_name = 'contribution/planning.html'

    
    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.all()
        context['items'] = items
        context['projects'] = Project.objects.all()
        context['frequency_choices'] = Frequency.objects.all()
        context['column_names'] = [
            {'field': 'date', 'display': 'По дате'},
            {'field': 'project__name', 'display': 'По проекту'},
            {'field': 'item__name', 'display': 'По статье'},
            {'field': 'payment__amount', 'display': 'По сумме платежа'},
            {'field': 'frequency__name', 'display': 'По частоте платежа'},
        ]
        context['items_colors'] = get_all_departments_colors(items)

        return context

class OperAccountingViewSet(viewsets.ModelViewSet):
    queryset = OperationalAccounting.objects.all()
    serializer_class = OperationalAccountingSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-payment_date']
    ordering_fields = [
        'payment_date',
        'recognition_date', 
        'payer__name',
        'recipient__name', 
        'item__name', 
        'payment_system__name',
        'project__name',
        'counterparty__name',
        'payment_amount',
        'commission_amount',
    ]


class PlanningViewSet(viewsets.ModelViewSet):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    ordering = ['-date']
    ordering_fields = [
        'date',
        'project__name', 
        'item__name', 
        'payment_amount',
        'frequency__name',
    ]