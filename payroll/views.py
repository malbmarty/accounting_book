from django.shortcuts import render
from rest_framework import viewsets, filters
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django_filters import FilterSet, DateFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import OuterRef, Subquery, Sum, DecimalField
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import (
    PositionSerializer, DepartmentSerializer, StatusSerializer,
    EmployeeTypeSerializer, PaymentTypeSerializer,
    EmployeeSerializer, AccrualSerializer, PayoutSerializer
)
from .models import (
    Position, Department, Status, EmployeeType, PaymentType,
    Employee, Accrual, Payout
)

from analytics_dir.models import Project, Participant

# HTML Views
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
    
# Сотрудники
class EmployeesPageView(TemplateView):
    template_name = 'payroll/employees.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем данные в контекст
        context['positions'] = Position.objects.all()
        context['departments'] = Department.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()

        return context

class EditEmployeePageView(TemplateView):
    template_name = 'payroll/edit_employee.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_id = self.kwargs.get('pk')
        
        # Получаем транзакцию или возвращаем 404
        employee = get_object_or_404(Employee, id=employee_id)
        
        # Сериализуем данные транзакции
        serializer = EmployeeSerializer(employee)
        
        # Добавляем данные в контекст
        context['employee'] = serializer.data
        context['positions'] = Position.objects.all()
        context['departments'] = Department.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()

        return context
    
# Начисления
class AccrualsPageView(TemplateView):
    template_name = 'payroll/accruals.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем данные в контекст
        context['employees'] = Employee.objects.all()
        context['departments'] = Department.objects.all()
        context['projects'] = Project.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()

        return context
    
class EditAccrualPageView(TemplateView):
    template_name = 'payroll/edit_accrual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accrual_id = self.kwargs.get('pk')
        
        # Получаем транзакцию или возвращаем 404
        accrual = get_object_or_404(Accrual, id=accrual_id)
        
        # Сериализуем данные транзакции
        serializer = AccrualSerializer(accrual)
        
        # Добавляем данные в контекст
        context['accrual'] = serializer.data
        context['date'] = accrual.date.strftime('%Y-%m-%d')
        context['employees'] = Employee.objects.all()
        context['departments'] = Department.objects.all()
        context['projects'] = Project.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()

        return context
    
# Начисления
class PayoutsPageView(TemplateView):
    template_name = 'payroll/payouts.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем данные в контекст
        context['employees'] = Employee.objects.all()
        context['departments'] = Department.objects.all()
        context['projects'] = Project.objects.all()
        context['participants'] = Participant.objects.all()
        context['payment_types'] = PaymentType.objects.all()

        return context
    
class EditPayoutPageView(TemplateView):
    template_name = 'payroll/edit_payout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payout_id = self.kwargs.get('pk')
        
        # Получаем транзакцию или возвращаем 404
        payout = get_object_or_404(Payout, id=payout_id)
        
        # Сериализуем данные транзакции
        serializer = PayoutSerializer(payout)
        
        # Добавляем данные в контекст
        context['payout'] = serializer.data
        context['date'] = payout.date.strftime('%Y-%m-%d')
        context['employees'] = Employee.objects.all()
        context['departments'] = Department.objects.all()
        context['projects'] = Project.objects.all()
        context['participants'] = Participant.objects.all()
        context['payment_types'] = PaymentType.objects.all()

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

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EmployeesFilter

class AccrualViewSet(viewsets.ModelViewSet):
    serializer_class = AccrualSerializer
    queryset = Accrual.objects.all() 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-date']

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

        return Payout.objects.annotate(
            accrued_total_for_month=Subquery(accruals_subquery, output_field=DecimalField(max_digits=20, decimal_places=2))
        )


class SummaryPageView(TemplateView):
    template_name = 'payroll/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = 2025
        context['years'] = list(range(2025, 2030))  # диапазон лет
        context['current_year'] = current_year
        return context

from django.db.models.functions import Coalesce

class YearlyPivotDataView(APIView):
    def get(self, request, *args, **kwargs):
        year = int(request.GET.get("year", timezone.now().year))

        result = []
        employees = Employee.objects.all().select_related("department")

        for emp in employees:
            months_data = {}
            for month in range(1, 13):
                accruals = Accrual.objects.filter(
                    employee=emp,
                    date__year=year,
                    date__month=month
                ).aggregate(
                    total_accrued=Sum(
                        Coalesce(F("hourly_pay"), 0) +
                        Coalesce(F("salary"), 0) +
                        Coalesce(F("addition_pay"), 0) -
                        Coalesce(F("deduction"), 0),
                        output_field=DecimalField(max_digits=20, decimal_places=2)
                    )
                )

                payouts = Payout.objects.filter(
                    employee=emp,
                    date__year=year,
                    date__month=month
                ).aggregate(
                    total_payout=Sum(
                        Coalesce(F("amount"), 0),
                        output_field=DecimalField(max_digits=20, decimal_places=2)
                    )
                )

                accrued = accruals["total_accrued"] or 0
                payout = payouts["total_payout"] or 0
                balance = accrued - payout

                months_data[f"{month:02d}"] = {
                    "accrued": float(accrued),
                    "payout": float(payout),
                    "balance": float(balance),
                }

            result.append({
                "department": emp.department.name if emp.department else "",
                "employee": emp.full_name,
                "opening_balance": 0,  # пока руками
                "months": months_data
            })

        return Response(result)



