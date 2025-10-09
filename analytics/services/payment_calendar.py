import pandas as pd
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from analytics_dir.models import (
    Project
)
from ..models import CounterpartyOpeningBalance
from contribution.models import (
    OperationalAccounting, Planning
)


class PaymentCalendarService:
    def __init__(self, start_date, end_date, project_id=None, period_type='quarter'):
        self.start_date = start_date
        self.end_date = end_date
        self.project_id = project_id
        self.period_type = period_type

    def build_context(self):
        project_filter = self._get_project_filter()
        
        plan_qs = Planning.objects.filter(**project_filter)
        fact_qs = OperationalAccounting.objects.filter(payment_date__range=[self.start_date, self.end_date], **project_filter)

        plan_df = self._build_plan_dataframe(plan_qs)
        fact_df = self._build_fact_dataframe(fact_qs)
        
        df = self._merge_and_process_data(plan_df, fact_df)
        grouped = self._group_data_by_period(df)
        
        headers = self._build_headers()
        calendar_data = self._build_calendar_data(grouped)
        flow_totals = self._calculate_flow_totals(calendar_data, headers)
        
        initial_plan_balance, initial_fact_balance = self._calculate_initial_balances(plan_qs, fact_qs)
        cash_flow_calendar = self._build_cash_flow_calendar(df, headers, initial_plan_balance, initial_fact_balance)

        return {
            'headers': headers,
            'calendar_data': calendar_data,
            'flow_totals': flow_totals,
            'cash_flow_calendar': cash_flow_calendar,
            'cash_flow_indicators': [
                'Остаток на начало',
                'Положительный денежный поток',
                'Отрицательный денежный поток',
                'Чистый денежный поток',
                'Остаток на конец'
            ]
        }

    def _get_project_filter(self):
        project_filter = {}
        if self.project_id and self.project_id != 'all':
            project_filter['project_id'] = int(self.project_id)
        return project_filter

    def _build_plan_dataframe(self, plan_qs):
        plan_records = []
        for p in plan_qs:
            if self.start_date <= p.date <= self.end_date:
                plan_records.append({
                    'period': p.date,
                    'item__name': p.item.name,
                    'item__flow_type__name': p.item.flow_type.name,
                    'plan': p.payment_amount
                })
            freq_name = p.frequency.name.strip().lower()
            if freq_name != "разово":
                try:
                    months = int(freq_name)
                    for i in range(1, months):
                        next_date = p.date + relativedelta(months=i)
                        if self.start_date <= next_date <= self.end_date:
                            plan_records.append({
                                'period': next_date,
                                'item__name': p.item.name,
                                'item__flow_type__name': p.item.flow_type.name,
                                'plan': p.payment_amount
                            })
                except ValueError:
                    pass

        plan_df = pd.DataFrame(plan_records)
        if plan_df.empty:
            plan_df = pd.DataFrame(columns=['period', 'item__name', 'item__flow_type__name', 'plan'])
        return plan_df

    def _build_fact_dataframe(self, fact_qs):
        fact_df = pd.DataFrame(fact_qs.values('payment_date', 'item__name', 'item__flow_type__name', 'payment_amount'))
        if not fact_df.empty:
            fact_df.rename(columns={'payment_date': 'period', 'payment_amount': 'fact'}, inplace=True)
        else:
            fact_df = pd.DataFrame(columns=['period', 'item__name', 'item__flow_type__name', 'fact'])
        return fact_df

    def _merge_and_process_data(self, plan_df, fact_df):
        df = pd.merge(plan_df, fact_df, on=['period', 'item__name', 'item__flow_type__name'], how='outer')
        df['plan'] = df['plan'].fillna(0)
        df['fact'] = df['fact'].fillna(0)
        df['variance'] = df['fact'] - df['plan']
        return df

    def _group_data_by_period(self, df):
        df['period'] = pd.to_datetime(df['period'])
        if self.period_type == 'day':
            df['period_group'] = df['period'].dt.to_period('D').dt.to_timestamp()
        elif self.period_type == 'month':
            df['period_group'] = df['period'].dt.to_period('M').dt.to_timestamp()
        elif self.period_type == 'quarter':
            df['period_group'] = df['period'].dt.to_period('Q').dt.to_timestamp()
        elif self.period_type == 'year':
            df['period_group'] = df['period'].dt.to_period('Y').dt.to_timestamp()

        grouped = df.groupby(['item__flow_type__name', 'item__name', 'period_group']).agg({
            'plan': 'sum', 'fact': 'sum', 'variance': 'sum'
        }).reset_index()
        return grouped

    def _build_headers(self):
        headers = []
        if self.period_type == 'day':
            periods = pd.date_range(self.start_date, self.end_date, freq='D')
            for d in periods:
                label = d.strftime("%d.%m.%Y")
                headers.append({'key': d.date(), 'start': label, 'end': label, 'label': label})
        elif self.period_type == 'month':
            periods = pd.period_range(self.start_date, self.end_date, freq='M')
            for p in periods:
                start = p.start_time.date()
                end = p.end_time.date()
                label = p.strftime("%b %Y").capitalize()
                headers.append({'key': start, 'start': start.strftime("%d.%m.%Y"), 'end': end.strftime("%d.%m.%Y"), 'label': label})
        elif self.period_type == 'quarter':
            periods = pd.period_range(self.start_date, self.end_date, freq='Q')
            for p in periods:
                start = p.start_time.date()
                end = p.end_time.date()
                q = p.quarter
                yy = str(p.year)[2:]
                label = f"{q} кв {yy}"
                headers.append({'key': start, 'start': start.strftime("%d.%m.%Y"), 'end': end.strftime("%d.%m.%Y"), 'label': label})
        elif self.period_type == 'year':
            periods = pd.period_range(self.start_date, self.end_date, freq='Y')
            for p in periods:
                start = p.start_time.date()
                end = p.end_time.date()
                label = f"{p.year} год"
                headers.append({'key': start, 'start': start.strftime("%d.%m.%Y"), 'end': end.strftime("%d.%m.%Y"), 'label': label})
        return headers

    def _build_calendar_data(self, grouped):
        calendar_data = {}
        for _, row in grouped.iterrows():
            flow_type = row['item__flow_type__name']
            item = row['item__name']
            period = row['period_group'].date()
            if flow_type not in calendar_data:
                calendar_data[flow_type] = {}
            if item not in calendar_data[flow_type]:
                calendar_data[flow_type][item] = {}
            calendar_data[flow_type][item][period] = {'plan': round(row['plan'],2), 'fact': round(row['fact'],2), 'var': round(row['variance'],2)}
        return calendar_data

    def _calculate_flow_totals(self, calendar_data, headers):
        flow_totals = {}
        for flow_type, items in calendar_data.items():
            flow_totals[flow_type] = {}
            for h in headers:
                plan_sum = sum(values.get(h['key'], {}).get('plan',0) for values in items.values())
                fact_sum = sum(values.get(h['key'], {}).get('fact',0) for values in items.values())
                var_sum = fact_sum - plan_sum
                flow_totals[flow_type][h['key']] = {'plan': round(plan_sum,2), 'fact': round(fact_sum,2), 'var': round(var_sum,2)}
        return flow_totals

    def _calculate_initial_balances(self, plan_qs, fact_qs):
        initial_plan_balance = 0
        initial_fact_balance = fact_qs.filter(payment_date__lt=self.start_date).aggregate(total=Sum('payment_amount'))['total'] or 0
        for p in plan_qs:
            if p.date < self.start_date:
                initial_plan_balance += p.payment_amount or 0
            freq_name = p.frequency.name.strip().lower()
            if freq_name != "разово":
                try:
                    months = int(freq_name)
                    for i in range(1, months):
                        next_date = p.date + relativedelta(months=i)
                        if next_date < self.start_date:
                            initial_plan_balance += p.payment_amount or 0
                except ValueError:
                    pass
        return initial_plan_balance, initial_fact_balance

    def _build_cash_flow_calendar(self, df, headers, initial_plan_balance, initial_fact_balance):
        periods = [h['key'] for h in headers]
        cash_flow_calendar = {}
        prev_plan_balance = initial_plan_balance
        prev_fact_balance = initial_fact_balance
        for p in periods:
            period_key = pd.Timestamp(p)
            period_data = df[df['period_group'] == period_key]
            inflow_plan = period_data[period_data['item__flow_type__name']=='Приход']['plan'].sum()
            inflow_fact = period_data[period_data['item__flow_type__name']=='Приход']['fact'].sum()
            outflow_plan = period_data[period_data['item__flow_type__name']=='Расход']['plan'].sum()
            outflow_fact = period_data[period_data['item__flow_type__name']=='Расход']['fact'].sum()
            net_plan = inflow_plan - outflow_plan
            net_fact = inflow_fact - outflow_fact
            closing_plan = net_plan
            closing_fact = net_fact
            cash_flow_calendar[p] = {
                'Остаток на начало': {'plan': round(prev_plan_balance,2),'fact': round(prev_fact_balance,2),'var': round(prev_fact_balance-prev_plan_balance,2)},
                'Положительный денежный поток': {'plan': round(inflow_plan,2),'fact': round(inflow_fact,2),'var': round(inflow_fact-inflow_plan,2)},
                'Отрицательный денежный поток': {'plan': round(outflow_plan,2),'fact': round(outflow_fact,2),'var': round(outflow_fact-outflow_plan,2)},
                'Чистый денежный поток': {'plan': round(net_plan,2),'fact': round(net_fact,2),'var': round(net_fact-net_plan,2)},
                'Остаток на конец': {'plan': round(closing_plan,2),'fact': round(closing_fact,2),'var': round(closing_fact-closing_plan,2)}
            }
            prev_plan_balance = closing_plan
            prev_fact_balance = closing_fact
        return cash_flow_calendar