from collections import defaultdict
from decimal import Decimal
from django.db.models import F, Sum
from ..models import ParticipantsOpeningBalance
from analytics_dir.models import Participant
from contribution.models import OperationalAccounting
from payroll.models import Payout
from django.db.models import Subquery

class BalancesService:
    def __init__(self, year):
        self.year = year

    def build_context(self):
        participants = Participant.objects.all()
        finance_income, finance_expense = self.get_financial_data()
        balances = self.get_balances()

        data = self.build_summary(participants, finance_income, finance_expense, balances)
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
        # Доходы из операционного учета
        oper_acc_income = OperationalAccounting.objects.filter(
            payment_date__year=self.year, 
            item__flow_type__name="Приход"
        ).values(
            participant_id=F('recipient_id'),
            month=F('payment_date__month')
        ).annotate(total=Sum('payment_amount'))
        
        # Выплаты
        payouts = Payout.objects.filter(date__year=self.year).values(
            participant_id=F('recipient_id'),
            month=F('date__month')
        ).annotate(total=Sum('amount'))
        
        # Объединяем доходы и выплаты
        combined_income = list(oper_acc_income) + list(payouts)
        
        # Расходы из операционного учета
        oper_acc_expense = OperationalAccounting.objects.filter(
            payment_date__year=self.year, 
            item__flow_type__name="Расход"
        ).values(
            participant_id=F('payer_id'),
            month=F('payment_date__month')
        ).annotate(total=Sum(F('payment_amount')+F('commission_amount')))
        
        return self.to_dict(combined_income), self.to_dict(oper_acc_expense)

    @staticmethod
    def to_dict(qs):
        data = defaultdict(lambda: defaultdict(Decimal))
        for item in qs:
            key = item['participant_id']
            month = item['month']
            data[key][month] = item['total'] or Decimal('0.00')
        return data

    def get_balances(self):
        return {b.participant_id: b.amount for b in ParticipantsOpeningBalance.objects.filter(year=self.year)}

    def build_summary(self, participants, finance_income, finance_expense, balances):

        participants_data = defaultdict(list)
        for participant in participants:
            participant_data = self.build_participant_summary(participant, finance_income, finance_expense, balances)
            participants_data[participant.name] = participant_data


        return {
            'participants_data': dict(participants_data),
        }

    def build_participant_summary(self, participant, finance_income, finance_expense, balances):
        incoming_balance = balances.get(participant.id, Decimal('0.00'))
        running_balance = incoming_balance
        key = (participant.id)
        total_income = total_expense = Decimal('0.00')

        participant_data = {'participant': participant, 'monthly': {}, 'incoming_balance': incoming_balance}

        for month in range(1, 13):
            income = finance_income[key][month] 
            expense = finance_expense[key][month]
            running_balance = income - expense
            total_income += income
            total_expense += expense

            participant_data['monthly'][month] = {'income': income, 'expense': expense, 'balance': running_balance}
            

        participant_data['year_total'] = {
            'income': total_income,
            'expense': total_expense,
            'balance': total_income - total_expense # Здесь опять вопрос про входящий остаток
        }

        return participant_data
