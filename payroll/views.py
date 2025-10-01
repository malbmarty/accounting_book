from django.shortcuts import render
from rest_framework import viewsets
from django.views.generic import TemplateView

from .serializers import (
    PositionSerializer, DepartmentSerializer, StatusSerializer,
    EmployeeTypeSerializer, PaymentTypeSerializer
)
from .models import (
    Position, Department, Status, EmployeeType, PaymentType
)

# HTML Views
# Для главной страницы
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