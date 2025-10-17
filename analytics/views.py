from django.shortcuts import render
from django.views.generic import TemplateView
import pandas as pd
from datetime import date, datetime
import json  # для работы с json.loads(request.body)
from django.http import JsonResponse  # для возврата JSON ответа
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, F, DecimalField

from .services import analytics_dept, payment_calendar, balances

from analytics_dir.models import (
    Project
)
from .models import CounterpartyOpeningBalance, ParticipantsOpeningBalance
from contribution.models import (
    OperationalAccounting, Planning
)

class PaymentCalendarPageView(TemplateView):
    template_name = 'analytics/payment_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        project_id = self.request.GET.get('project')
        period_type = self.request.GET.get('period_type') or 'quarter'

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        context['projects'] = Project.objects.all()
        context['form_values'] = {
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
            'project': int(project_id) if project_id and project_id != 'all' else 'all',
            'period_type': period_type,
        }

        if start_date and end_date:
            context.update(payment_calendar.PaymentCalendarService(start_date, end_date, project_id, period_type).build_context())

        print(context)

        return context


class DeptPageView(TemplateView):
    template_name = 'analytics/dept.html'

    def post(self, request, *args, **kwargs):
        # Сохраняет или обновляет входящий баланс.
        try:
            data = json.loads(request.body)
            CounterpartyOpeningBalance.objects.update_or_create(
                counterparty_id=data["counterparty_id"],
                year=int(data["year"]),
                defaults={"amount": Decimal(data.get("amount", 0))}
            )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', 2025))
        context.update(analytics_dept.AnalyticsDeptService(year).build_context())
        print(context)
        return context
    
class BalancesPageView(TemplateView):
    template_name = 'analytics/balances.html'

    def post(self, request, *args, **kwargs):
        # Сохраняет или обновляет входящий баланс.
        try:
            data = json.loads(request.body)
            ParticipantsOpeningBalance.objects.update_or_create(
                participant_id=data["participant_id"],
                year=int(data["year"]),
                defaults={"amount": Decimal(data.get("amount", 0))}
            )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', 2025))
        context.update(balances.BalancesService(year).build_context())
        print(context)
        return context