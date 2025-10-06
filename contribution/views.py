from django.shortcuts import render, redirect
from rest_framework import viewsets, filters
from django.views.generic import TemplateView

from .serializers import (
    OperationalAccountingSerializer, PlanningSerializer
)

from .models import (
    OperationalAccounting, Planning
)

class OperationalAccountingViewSet(viewsets.ModelViewSet):
    queryset = OperationalAccounting.objects.all()
    serializer_class = OperationalAccountingSerializer

class PlanningViewSet(viewsets.ModelViewSet):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer