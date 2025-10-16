from django.shortcuts import render, redirect
from rest_framework import viewsets, filters
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django_filters import FilterSet, DateFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import OuterRef, Subquery, Sum, DecimalField
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
import json  # для работы с json.loads(request.body)
from django.http import JsonResponse  # для возврата JSON ответа
from collections import defaultdict
from decimal import Decimal

from .serializers import (
    PositionSerializer, DepartmentSerializer, StatusSerializer,
    EmployeeTypeSerializer, PaymentTypeSerializer,
    EmployeeSerializer, AccrualSerializer, PayoutSerializer
)
from .models import (
    Position, Department, Status, EmployeeType, PaymentType,
    Employee, Accrual, Payout, OpeningBalance
)

from analytics_dir.models import Project, Participant
from .services.payroll_summary import PayrollSummaryService
from .services.department_color import get_all_departments_colors 

# HTML VIEWS
# Справочник ЗП ведомости
class PayrollDirPageView(TemplateView):
    template_name = 'payroll/payroll_dir.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем все данные из базы и передаем в шаблон
        context['positions'] = Position.objects.all()
        context['departments'] = Department.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()
        context['payment_types'] = PaymentType.objects.all()
        
        return context
    
# Страница с таблицей Сотрудники
class EmployeesPageView(TemplateView):
    template_name = 'payroll/employees.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        departments = Department.objects.all()
        context['positions'] = Position.objects.all()
        context['departments'] = departments
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()
        context['column_names'] = [
            {'field': 'full_name', 'display': 'По ФИО'},
            {'field': 'position__name', 'display': 'По должности'},
            {'field': 'department__name', 'display': 'По отделу'},
            {'field': 'status__name', 'display': 'По статусу'},
            {'field': 'employee_type__name', 'display': 'По типу'},
            {'field': 'bank_name', 'display': 'По банку'},
        ]
        context['department_colors'] = get_all_departments_colors(departments)

        return context

    
# Страница с таблицей Начисления
class AccrualsPageView(TemplateView):
    template_name = 'payroll/accruals.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        departments = Department.objects.all()
        context['employees'] = Employee.objects.all()
        context['departments'] = departments
        context['projects'] = Project.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()
        context['column_names'] = [
            {'field': 'date', 'display': 'По дате'},
            {'field': 'project__name', 'display': 'По проекту'},
            {'field': 'department__name', 'display': 'По отделу'},
            {'field': 'employee__full_name', 'display': 'По сотруднику'},
            {'field': 'hourly_pay', 'display': 'По почасовой'},
            {'field': 'salary', 'display': 'По окладу'},
            {'field': 'addition_pay', 'display': 'По доплатам'},
            {'field': 'deduction', 'display': 'По возвратам'},
        ]
        context['department_colors'] = get_all_departments_colors(departments)

        return context
    

    
# Страница с таблицей Выплаты
class PayoutsPageView(TemplateView):
    template_name = 'payroll/payouts.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        departments = Department.objects.all()
        # Добавляем данные в контекст
        context['employees'] = Employee.objects.all()
        context['departments'] = departments
        context['projects'] = Project.objects.all()
        context['participants'] = Participant.objects.all()
        context['payment_types'] = PaymentType.objects.all()
        context['column_names'] = [
            {'field': 'date', 'display': 'По дате'},
            {'field': 'project__name', 'display': 'По проекту'},
            {'field': 'payer__name', 'display': 'По плательщику'},
            {'field': 'recipient__name', 'display': 'По получателю'},
            {'field': 'department__name', 'display': 'По отделу'},
            {'field': 'employee__full_name', 'display': 'По сотруднику'},
            {'field': 'payment_type__name', 'display': 'По типу выплаты'},
            {'field': 'amount', 'display': 'По сумме выплаты'},
        ]
        context['department_colors'] = get_all_departments_colors(departments)

        return context
    
    
class SummaryPageView(TemplateView):
    template_name = 'payroll/summary.html'

    def post(self, request, *args, **kwargs):
        # Сохраняет или обновляет входящий баланс.
        try:
            data = json.loads(request.body)
            OpeningBalance.objects.update_or_create(
                employee_id=data["employee_id"],
                year=int(data["year"]),
                defaults={"amount": Decimal(data.get("amount", 0))}
            )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', 2025))
        context.update(PayrollSummaryService(year).build_context())
        departments = Department.objects.all()
        context['department_colors'] = get_all_departments_colors(departments)
        
        return context


# Фильтр для сотрудников
class EmployeesFilter(FilterSet):
    
    class Meta:
        model = Employee
        fields = {
            'department': ['exact'],
        }

# API 
class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

class EmployeeTypeViewSet(viewsets.ModelViewSet):
    queryset = EmployeeType.objects.all()
    serializer_class = EmployeeTypeSerializer

class PaymentTypeViewSet(viewsets.ModelViewSet):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EmployeesFilter
    ordering_fields = [
        'full_name', 
        'position__name', 
        'department__name', 
        'status__name',
        'employee_type__name',
        'bank_name',
        'card_number'
    ]
    ordering = ['full_name']  # сортировка по умолчанию

class AccrualViewSet(viewsets.ModelViewSet):
    serializer_class = AccrualSerializer
    queryset = Accrual.objects.all() 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-date']
    ordering_fields = [
        'date', 
        'project__name', 
        'department__name', 
        'employee__full_name',
        'hourly_pay',
        'salary',
        'addition_pay',
        'deduction'
    ]

    def get_queryset(self):
        # подзапрос для суммы по комбинации date+department+employee
        subquery = Accrual.objects.filter(
            date=OuterRef('date'),
            department=OuterRef('department'),
            employee=OuterRef('employee')
        ).values('date').annotate(total=Sum('hourly_pay')).values('total')

        return Accrual.objects.annotate(
            hourly_sum_for_employee=Subquery(subquery, output_field=DecimalField(max_digits=20, decimal_places=2))
        )

class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-date']
    ordering_fields = [
        'date', 
        'project__name',
        'payer__name',
        'recipient__name', 
        'department__name', 
        'employee__full_name',
        'payment_type__name'
        'amount',
    ]

    def get_queryset(self):
        # подзапрос для суммы начислений за месяц
        accruals_subquery = Accrual.objects.filter(
            employee=OuterRef('employee'),
            department=OuterRef('department'),
            date__year=OuterRef('date__year'),
            date__month=OuterRef('date__month')
        ).values('employee').annotate(
            total=Sum(F('hourly_pay') + F('salary') + F('addition_pay') - F('deduction'), output_field=DecimalField(max_digits=20, decimal_places=2))
        ).values('total')
    
        # Сумма выплат за месяц 
        payouts_subquery = Payout.objects.filter(
            employee=OuterRef('employee'),
            department=OuterRef('department'),
            date__year=OuterRef('date__year'),
            date__month=OuterRef('date__month')
        ).values('employee').annotate(
            total=Sum('amount', output_field=DecimalField(max_digits=20, decimal_places=2))
        ).values('total')

        # Сумма начислений за всё время 
        accruals_all_time = Accrual.objects.filter(
            employee=OuterRef('employee'),
            department=OuterRef('department')
        ).values('employee').annotate(
            total=Sum(
                F('hourly_pay') + F('salary') + F('addition_pay') - F('deduction'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        ).values('total')

        # Сумма выплат за всё время 
        payouts_all_time = Payout.objects.filter(
            employee=OuterRef('employee'),
            department=OuterRef('department')
        ).values('employee').annotate(
            total=Sum('amount', output_field=DecimalField(max_digits=20, decimal_places=2))
        ).values('total')

        return Payout.objects.annotate(
            accrued_total_for_month=Subquery(accruals_subquery, output_field=DecimalField(max_digits=20, decimal_places=2)),
            total_paid_for_month=Subquery(payouts_subquery, output_field=DecimalField(max_digits=20, decimal_places=2)),
            accrued_total_for_all_time=Subquery(accruals_all_time, output_field=DecimalField(max_digits=20, decimal_places=2)),
            total_paid_for_all_time=Subquery(payouts_all_time, output_field=DecimalField(max_digits=20, decimal_places=2))
        )







