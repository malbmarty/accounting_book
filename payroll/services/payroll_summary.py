from collections import defaultdict
from decimal import Decimal
from django.db.models import F, Sum
from ..models import Employee, Accrual, Payout, OpeningBalance

class PayrollSummaryService:
    def __init__(self, year):
        self.year = year

    def build_context(self):
        employees = Employee.objects.select_related('department').all()
        accruals, payouts = self.get_financial_data()
        balances = self.get_balances()

        data = self.build_summary(employees, accruals, payouts, balances)
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
        accruals = Accrual.objects.filter(date__year=self.year).values(
            'employee_id', 'department_id', 'date__month'
        ).annotate(total=Sum(F('hourly_pay') + F('salary') + F('addition_pay') - F('deduction')))

        payouts = Payout.objects.filter(date__year=self.year).values(
            'employee_id', 'department_id', 'date__month'
        ).annotate(total=Sum('amount'))

        return self.to_dict(accruals), self.to_dict(payouts)

    @staticmethod
    def to_dict(qs):
        data = defaultdict(lambda: defaultdict(Decimal))
        for item in qs:
            key = (item['employee_id'], item['department_id'])
            data[key][item['date__month']] = item['total'] or Decimal('0.00')
        return data

    def get_balances(self):
        return {b.employee_id: b.amount for b in OpeningBalance.objects.filter(year=self.year)}

    def build_summary(self, employees, accruals, payouts, balances):
        dept_data = defaultdict(list)
        dept_totals = defaultdict(lambda: {
            'monthly': defaultdict(lambda: {'accrued': Decimal('0.00'),
                                            'paid': Decimal('0.00'),
                                            'balance': Decimal('0.00')}),
            'year_total': {'accrued': Decimal('0.00'),
                           'paid': Decimal('0.00'),
                           'balance': Decimal('0.00')}
        })

        for emp in employees:
            emp_data = self.build_employee_summary(emp, accruals, payouts, balances, dept_totals)
            dept_name = emp.department.name if emp.department else 'Без отдела'
            dept_data[dept_name].append(emp_data)

        company_totals = self.aggregate_company_totals(dept_totals)

        return {
            'department_data': dict(dept_data),
            'department_totals': {k: {'monthly': dict(v['monthly']), 'year_total': v['year_total']}
                                  for k, v in dept_totals.items()},
            'company_totals': company_totals
        }

    def build_employee_summary(self, emp, accruals, payouts, balances, dept_totals):
        incoming_balance = balances.get(emp.id, Decimal('0.00'))
        running_balance = incoming_balance
        key = (emp.id, emp.department_id)
        total_accrued = total_paid = Decimal('0.00')
        dept_name = emp.department.name if emp.department else 'Без отдела'

        emp_data = {'employee': emp, 'monthly': {}, 'incoming_balance': incoming_balance}

        for month in range(1, 13):
            accrued = accruals[key][month]
            paid = payouts[key][month]
            running_balance += accrued - paid
            total_accrued += accrued
            total_paid += paid

            emp_data['monthly'][month] = {'accrued': accrued, 'paid': paid, 'balance': running_balance}
            self._update_dept_totals(dept_totals[dept_name]['monthly'][month], accrued, paid, running_balance)

        emp_data['year_total'] = {
            'accrued': total_accrued,
            'paid': total_paid,
            'balance': incoming_balance + total_accrued - total_paid
        }

        self._update_dept_totals(dept_totals[dept_name]['year_total'], total_accrued, total_paid,
                                 emp_data['year_total']['balance'])
        return emp_data

    @staticmethod
    def _update_dept_totals(target, accrued, paid, balance):
        target['accrued'] += accrued
        target['paid'] += paid
        target['balance'] += balance

    @staticmethod
    def aggregate_company_totals(dept_totals):
        company = {
            'monthly': defaultdict(lambda: {'accrued': Decimal('0.00'),
                                            'paid': Decimal('0.00'),
                                            'balance': Decimal('0.00')}),
            'year_total': {'accrued': Decimal('0.00'),
                           'paid': Decimal('0.00'),
                           'balance': Decimal('0.00')}
        }

        for dept in dept_totals.values():
            for m, data in dept['monthly'].items():
                for k in ['accrued', 'paid', 'balance']:
                    company['monthly'][m][k] += data[k]
            for k in ['accrued', 'paid', 'balance']:
                company['year_total'][k] += dept['year_total'][k]

        return {'monthly': dict(company['monthly']), 'year_total': company['year_total']}