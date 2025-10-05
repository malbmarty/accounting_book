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
        
        context['positions'] = Position.objects.all()
        context['departments'] = Department.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()

        return context

# Страница с формой изменения записи в таблице Сотрудники
class EditEmployeePageView(TemplateView):
    template_name = 'payroll/edit_employee.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_id = self.kwargs.get('pk')
        
        # Получаем объект или возвращаем 404
        employee = get_object_or_404(Employee, id=employee_id)
        
        # Сериализуем данные 
        serializer = EmployeeSerializer(employee)
        
        # Добавляем данные в контекст
        context['employee'] = serializer.data
        context['positions'] = Position.objects.all()
        context['departments'] = Department.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()

        return context
    
# Страница с таблицей Начисления
class AccrualsPageView(TemplateView):
    template_name = 'payroll/accruals.html'

    # Добавляем данные в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['employees'] = Employee.objects.all()
        context['departments'] = Department.objects.all()
        context['projects'] = Project.objects.all()
        context['statuses'] = Status.objects.all()
        context['employee_types'] = EmployeeType.objects.all()

        return context
    
# Страница с формой изменения записи в таблице Начисления
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
    
# Страница с таблицей Выплаты
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
    
# Страница с формой изменения записи в таблице ВЫПЛАТЫ
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

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-date']

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

class SummaryPageView(TemplateView):
    template_name = 'payroll/summary.html'

    def post(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
            employee_id = data.get("employee_id")
            amount = Decimal(data.get("amount", 0))
            year = int(data.get("year"))


            OpeningBalance.objects.update_or_create(
                employee_id=employee_id,
                year=year,
                defaults={"amount": amount}
            )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = int(self.request.GET.get('year', 2025))
        context['years'] = list(range(2025, 2030))
        context['current_year'] = current_year
        context['months'] = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        # Все сотрудники с отделами
        employees = Employee.objects.select_related('department').all()
        context['employees'] = employees

        # Получаем все начисления и выплаты за год
        accruals_qs = Accrual.objects.filter(date__year=current_year)
        payouts_qs = Payout.objects.filter(date__year=current_year)

        # Группировка начислений по (сотрудник, отдел, месяц)
        accruals = accruals_qs.values('employee_id', 'department_id', 'date__month').annotate(
            total=Sum(F('hourly_pay') + F('salary') + F('addition_pay') - F('deduction'))
        )
        accrual_dict = defaultdict(lambda: defaultdict(Decimal))
        for a in accruals:
            key = (a['employee_id'], a['department_id'])
            accrual_dict[key][a['date__month']] = a['total'] or Decimal('0.00')

        # Группировка выплат по (сотрудник, отдел, месяц)
        payouts = payouts_qs.values('employee_id', 'department_id', 'date__month').annotate(
            total=Sum('amount')
        )
        payout_dict = defaultdict(lambda: defaultdict(Decimal))
        for p in payouts:
            key = (p['employee_id'], p['department_id'])
            payout_dict[key][p['date__month']] = p['total'] or Decimal('0.00')

        # Входящие остатки всех сотрудников за выбранный год
        balances = OpeningBalance.objects.filter(year=current_year)
        balance_dict = {b.employee_id: b.amount for b in balances}

        # Формируем сводку по отделам
        department_data = defaultdict(list)
        department_totals = defaultdict(lambda: {
            'monthly': defaultdict(lambda: {'accrued': Decimal('0.00'),
                                            'paid': Decimal('0.00'),
                                            'balance': Decimal('0.00')}),
            'year_total': {'accrued': Decimal('0.00'),
                        'paid': Decimal('0.00'),
                        'balance': Decimal('0.00')}
        })

        for emp in employees:
            incoming_balance = balance_dict.get(emp.id, Decimal('0.00'))
            running_balance = incoming_balance

            emp_data = {
                'employee': emp,
                'monthly': {},
                'incoming_balance': incoming_balance
            }

            key = (emp.id, emp.department_id)
            total_accrued = Decimal('0.00')
            total_paid = Decimal('0.00')

            for month in range(1, 13):
                month_accrued = accrual_dict[key][month]
                month_paid = payout_dict[key][month]

                running_balance += month_accrued - month_paid
                total_accrued += month_accrued
                total_paid += month_paid

                emp_data['monthly'][month] = {
                    'accrued': month_accrued,
                    'paid': month_paid,
                    'balance': running_balance
                }

                # Итоги по отделу
                dept_name = emp.department.name if emp.department else 'Без отдела'
                dept_tot = department_totals[dept_name]
                dept_tot['monthly'][month]['accrued'] += month_accrued
                dept_tot['monthly'][month]['paid'] += month_paid
                dept_tot['monthly'][month]['balance'] += running_balance

            # Итоги за год для сотрудника
            year_balance = incoming_balance + total_accrued - total_paid
            emp_data['year_total'] = {
                'accrued': total_accrued,
                'paid': total_paid,
                'balance': year_balance
            }

            # Итоги по отделу за год
            dept_tot['year_total']['accrued'] += total_accrued
            dept_tot['year_total']['paid'] += total_paid
            dept_tot['year_total']['balance'] += year_balance

            dept_name = emp.department.name if emp.department else 'Без отдела'
            department_data[dept_name].append(emp_data)

        # Итоги по компании
        company_totals = {
            'monthly': defaultdict(lambda: {'accrued': Decimal('0.00'),
                                            'paid': Decimal('0.00'),
                                            'balance': Decimal('0.00')}),
            'year_total': {'accrued': Decimal('0.00'),
                        'paid': Decimal('0.00'),
                        'balance': Decimal('0.00')}
        }

        for dept_name, dept_data in department_totals.items():
            for month, month_data in dept_data['monthly'].items():
                company_totals['monthly'][month]['accrued'] += month_data['accrued']
                company_totals['monthly'][month]['paid'] += month_data['paid']
                company_totals['monthly'][month]['balance'] += month_data['balance']

            company_totals['year_total']['accrued'] += dept_data['year_total']['accrued']
            company_totals['year_total']['paid'] += dept_data['year_total']['paid']
            company_totals['year_total']['balance'] += dept_data['year_total']['balance']

        # Добавляем всё в контекст
        context['department_data'] = {k: v for k, v in department_data.items()}
        context['department_totals'] = {k: {
            'monthly': dict(v['monthly']),
            'year_total': v['year_total']
        } for k, v in department_totals.items()}
        context['company_totals'] = {
            'monthly': dict(company_totals['monthly']),
            'year_total': company_totals['year_total']
        }

        return context





