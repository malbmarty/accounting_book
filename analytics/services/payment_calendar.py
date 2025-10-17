
from collections import defaultdict
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from analytics_dir.models import Project
from contribution.models import OperationalAccounting, Planning


class PaymentCalendarService:
    def __init__(self, start_date, end_date, project_id=None, period_type='quarter'):
        self.start_date = start_date
        self.end_date = end_date
        self.project_id = project_id
        self.period_type = period_type

    def build_context(self):
        project_filter = self.get_project_filter()

        plan_qs = Planning.objects.filter(**project_filter)
        fact_qs = OperationalAccounting.objects.filter(
            payment_date__range=[self.start_date, self.end_date], **project_filter
        )

        plans = self.get_plan_data(plan_qs)
        facts = self.get_fact_data(fact_qs)

        grouped = self.group_data(plans, facts)
        headers = self.build_headers()

        calendar_data = self.build_calendar_data(grouped)
        calendar_data = self.order_flows(calendar_data) 
        flow_totals = self.build_flow_totals(calendar_data, headers)
        flow_totals = self.order_flows(flow_totals)

        initial_plan, initial_fact = self.get_initial_balances(plan_qs, fact_qs)
        cash_flow_calendar = self.build_cash_flow_calendar(grouped, headers, initial_plan, initial_fact)

        return {
            "headers": headers,
            "calendar_data": self.to_dict(calendar_data),
            "flow_totals": self.to_dict(flow_totals),
            "cash_flow_calendar": self.to_dict(cash_flow_calendar),
            "cash_flow_indicators": [
                "Остаток на начало",
                "Положительный денежный поток",
                "Отрицательный денежный поток",
                "Чистый денежный поток",
                "Остаток на конец",
            ],
        }
    
    @staticmethod
    def order_flows(data):
        order = ["Приход", "Расход"]
        ordered = {}
        for key in order:
            if key in data:
                ordered[key] = data[key]
        for key in data:
            if key not in ordered:
                ordered[key] = data[key]
        return ordered

    @staticmethod
    def to_dict(obj):
        # Рекурсивное приведение defaultdict → dict
        if isinstance(obj, dict):
            return {k: PaymentCalendarService.to_dict(v) for k, v in obj.items()}
        return obj

    def get_project_filter(self):
        if self.project_id and self.project_id != "all":
            return {"project_id": int(self.project_id)}
        return {}

    def get_plan_data(self, qs):
        # Создание записей планов с учетом частоты
        records = []
        for p in qs:
            if self.start_date <= p.date <= self.end_date:
                records.append(self._record(p.date, p))
            freq_name = p.frequency.name.strip().lower()
            if freq_name != "разово":
                try:
                    months = int(freq_name)
                    for i in range(1, months):
                        next_date = p.date + relativedelta(months=i)
                        if self.start_date <= next_date <= self.end_date:
                            records.append(self._record(next_date, p))
                except ValueError:
                    continue
        return records

    def get_fact_data(self, qs):
        # Фактические записи по оплатам
        return [
            {
                "period": f.payment_date,
                "item__name": f.item.name,
                "item__flow_type__name": f.item.flow_type.name,
                "fact": Decimal(f.payment_amount or 0),
            }
            for f in qs
        ]

    @staticmethod
    def _record(date, plan):
        return {
            "period": date,
            "item__name": plan.item.name,
            "item__flow_type__name": plan.item.flow_type.name,
            "plan": Decimal(plan.payment_amount or 0),
        }

    def group_data(self, plans, facts):
        # Объединение плановых и фактических данных по периодам
        grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"plan": Decimal("0.00"), "fact": Decimal("0.00")})))

        for p in plans:
            period_key = self._get_period_key(p["period"])
            item = p["item__name"]
            flow_type = p["item__flow_type__name"]
            grouped[flow_type][item][period_key]["plan"] += p["plan"]

        for f in facts:
            period_key = self._get_period_key(f["period"])
            item = f["item__name"]
            flow_type = f["item__flow_type__name"]
            grouped[flow_type][item][period_key]["fact"] += f["fact"]

        # добавляем разницу
        for flow_type, items in grouped.items():
            for item, periods in items.items():
                for period_key, values in periods.items():
                    values["var"] = values["fact"] - values["plan"]

        return grouped

    def _get_period_key(self, date):
        # Группировка по выбранному типу периода
        if self.period_type == "day":
            return date
        elif self.period_type == "month":
            return date.replace(day=1)
        elif self.period_type == "quarter":
            month = ((date.month - 1) // 3) * 3 + 1
            return date.replace(month=month, day=1)
        elif self.period_type == "year":
            return date.replace(month=1, day=1)
        return date

    def build_headers(self):
        headers = []
        current = self.start_date

        while current <= self.end_date:
            if self.period_type == "day":
                start, end = current, current
                label = current.strftime("%d.%m.%Y")
                step = relativedelta(days=1)

            elif self.period_type == "month":
                start = current.replace(day=1)
                end = (start + relativedelta(months=1)) - relativedelta(days=1)
                label = start.strftime("%b %Y").capitalize()
                step = relativedelta(months=1)

            elif self.period_type == "quarter":
                q = (current.month - 1) // 3 + 1
                start = current.replace(month=(q - 1) * 3 + 1, day=1)
                end = start + relativedelta(months=3, days=-1)
                label = f"{q} кв {str(start.year)[2:]}"
                step = relativedelta(months=3)

            elif self.period_type == "year":
                start = current.replace(month=1, day=1)
                end = current.replace(month=12, day=31)
                label = f"{start.year} год"
                step = relativedelta(years=1)

            headers.append({
                "key": start,
                "start": start.strftime("%d.%m.%Y"),
                "end": end.strftime("%d.%m.%Y"),
                "label": label,
            })
            current += step

        return headers

    def build_calendar_data(self, grouped):
        # Формирует таблицу вида: {flow_type: {item: {period: {...}}}}
        calendar_data = defaultdict(lambda: defaultdict(dict))
        for flow_type, items in grouped.items():
            for item, periods in items.items():
                for period, values in periods.items():
                    calendar_data[flow_type][item][period] = {
                        "plan": round(values["plan"], 2),
                        "fact": round(values["fact"], 2),
                        "var": round(values["var"], 2),
                    }
        return dict(calendar_data)

    def build_flow_totals(self, calendar_data, headers):
        flow_totals = defaultdict(dict)
        for flow_type, items in calendar_data.items():
            for h in headers:
                key = h["key"]
                plan_sum = sum(values.get(key, {}).get("plan", 0) for values in items.values())
                fact_sum = sum(values.get(key, {}).get("fact", 0) for values in items.values())
                flow_totals[flow_type][key] = {
                    "plan": round(plan_sum, 2),
                    "fact": round(fact_sum, 2),
                    "var": round(fact_sum - plan_sum, 2),
                }
        return dict(flow_totals)

    def get_initial_balances(self, plan_qs, fact_qs):
        plan_balance = Decimal("0.00")
        fact_balance = Decimal(fact_qs.filter(payment_date__lt=self.start_date)
                               .aggregate(total=Sum("payment_amount"))["total"] or 0)

        for p in plan_qs:
            freq_name = p.frequency.name.strip().lower()
            if p.date < self.start_date:
                plan_balance += Decimal(p.payment_amount or 0)
            if freq_name != "разово":
                try:
                    months = int(freq_name)
                    for i in range(1, months):
                        next_date = p.date + relativedelta(months=i)
                        if next_date < self.start_date:
                            plan_balance += Decimal(p.payment_amount or 0)
                except ValueError:
                    continue
        return plan_balance, fact_balance

    def build_cash_flow_calendar(self, grouped, headers, init_plan, init_fact):
        periods = [h["key"] for h in headers]
        cash_calendar = {}

        prev_plan = init_plan
        prev_fact = init_fact

        for p in periods:
            inflow_plan = self._sum_by_flow_type(grouped, "Приход", p, "plan")
            inflow_fact = self._sum_by_flow_type(grouped, "Приход", p, "fact")
            outflow_plan = self._sum_by_flow_type(grouped, "Расход", p, "plan")
            outflow_fact = self._sum_by_flow_type(grouped, "Расход", p, "fact")

            net_plan = inflow_plan - outflow_plan
            net_fact = inflow_fact - outflow_fact

            cash_calendar[p] = {
                "Остаток на начало": self._balance_record(prev_plan, prev_fact),
                "Положительный денежный поток": self._balance_record(inflow_plan, inflow_fact),
                "Отрицательный денежный поток": self._balance_record(outflow_plan, outflow_fact),
                "Чистый денежный поток": self._balance_record(net_plan, net_fact),
                "Остаток на конец": self._balance_record(net_plan, net_fact),
            }

            prev_plan = net_plan
            prev_fact = net_fact

        return cash_calendar

    @staticmethod
    def _sum_by_flow_type(grouped, flow_type, period, field):
        # Суммирует значения по типу потока (Приход/Расход)
        total = Decimal("0.00")
        if flow_type not in grouped:
            return total
        for item_data in grouped[flow_type].values():
            total += item_data.get(period, {}).get(field, Decimal("0.00"))
        return total

    @staticmethod
    def _balance_record(plan, fact):
        return {
            "plan": round(plan, 2),
            "fact": round(fact, 2),
            "var": round(fact - plan, 2),
        }

