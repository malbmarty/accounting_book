from collections import defaultdict
from decimal import Decimal
from django.db.models import F, Sum
from ..models import CounterpartyOpeningBalance
from analytics_dir.models import Counterparty
from contribution.models import OperationalAccounting
from django.db.models import Subquery

class AnalyticsDeptService:
    def __init__(self, year):
        self.year = year

    def build_context(self):
        counterparties = Counterparty.objects.filter(
            id__in=Subquery(
                OperationalAccounting.objects.filter(recognition_date__year=self.year).values('counterparty_id')
            )
        )
        oper_accounting_income, oper_accounting_expense = self.get_financial_data()
        balances = self.get_balances()

        data = self.build_summary(counterparties, oper_accounting_income, oper_accounting_expense, balances)
        data.update({
            'years': range(2025, 2030),
            'current_year': self.year,
            'months': range(1, 13),
            'months_name': self.get_month_names(),
        })
        return data

    @staticmethod
    def get_month_names():
        return [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

    def get_financial_data(self):
        records_income = OperationalAccounting.objects.filter(recognition_date__year=self.year, item__flow_type__name="Приход").values(
            'counterparty_id', 'recognition_date__month'
        ).annotate(total=Sum('payment_amount'))

        records_expense = OperationalAccounting.objects.filter(recognition_date__year=self.year, item__flow_type__name ="Расход").values(
            'counterparty_id', 'recognition_date__month'
        ).annotate(total=Sum('payment_amount'))


        return self.to_dict(records_income), self.to_dict(records_expense)

    @staticmethod
    def to_dict(qs):
        data = defaultdict(lambda: defaultdict(Decimal))
        for item in qs:
            key = item['counterparty_id']
            data[key][item['recognition_date__month']] = item['total'] or Decimal('0.00')
        return data

    def get_balances(self):
        return {b.counterparty_id: b.amount for b in CounterpartyOpeningBalance.objects.filter(year=self.year)}

    def build_summary(self, counterparties, oper_accounting_income, oper_accounting_expense, balances):

        counterparties_data = defaultdict(list)
        for counterparty in counterparties:
            counterparty_data = self.build_counterparty_summary(counterparty, oper_accounting_income, oper_accounting_expense, balances)
            counterparties_data[counterparty.name] = counterparty_data


        return {
            'counterparties_data': dict(counterparties_data),
        }

    def build_counterparty_summary(self, counterparty, oper_accounting_income, oper_accounting_expense, balances):
        incoming_balance = balances.get(counterparty.id, Decimal('0.00'))
        running_balance = incoming_balance
        key = (counterparty.id)
        total_accrued = total_paid = Decimal('0.00')

        counterparty_data = {'counterparty': counterparty, 'monthly': {}, 'incoming_balance': incoming_balance}

        for month in range(1, 13):
            accrued = oper_accounting_expense[key][month] - oper_accounting_income[key][month] 
            paid = oper_accounting_income[key][month] - oper_accounting_expense[key][month]
            running_balance += accrued + paid
            total_accrued += accrued
            total_paid += paid

            counterparty_data['monthly'][month] = {'accrued': accrued, 'paid': paid, 'balance': running_balance}
            

        counterparty_data['year_total'] = {
            'accrued': total_accrued,
            'paid': total_paid,
            'balance': total_accrued + total_paid # Здесь опять вопрос про входящий остаток
        }

        return counterparty_data


