from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import reduce

from pydantic import BaseModel


class FixedExpense(BaseModel):
    category: str
    amount: int


class User(BaseModel):
    name: str
    email: str
    password_hash: Optional[str]


class Transaction(BaseModel):
    category: str
    amount: int
    created_at: datetime
    user: str
    title: Optional[str]
    notes: Optional[str]


class StateDefaults(BaseModel):
    monthly_income: int
    fixed_expenses: list[FixedExpense]


class MonthlyState(BaseModel):
    monthly_income: int
    fixed_expenses: list[FixedExpense]
    transactions: list[Transaction]

    _DATE_FORMAT = "%m/%y"

    @staticmethod
    def key_for_date(dt: datetime):
        return dt.strftime(MonthlyState._DATE_FORMAT)

    @staticmethod
    def date_for_key(key: str):
        return datetime.strptime(key, MonthlyState._DATE_FORMAT)

    @staticmethod
    def new_from_defaults(defaults: StateDefaults) -> MonthlyState:
        return MonthlyState(
            monthly_income=defaults.monthly_income,
            fixed_expenses=defaults.fixed_expenses,
            transactions=[],
        )


class ApplicationState(BaseModel):
    users: list[User]
    last_accessed: datetime
    defaults: StateDefaults
    variable_categories: list[str]
    fixed_categories: list[str]
    state: Dict[str, MonthlyState]

    def get_current_state(self, get_now=datetime.now) -> MonthlyState:
        key = MonthlyState.key_for_date(get_now())
        if not self.state.get(key):
            self.state[key] = MonthlyState.new_from_defaults(self.defaults)

        return self.state[key]


"""
REPORTING
"""


class MonthlyTotals(BaseModel):
    income: int
    spent: int
    remaining: int
    unallocated: int


class MonthlyCategoryReport(BaseModel):
    category: str
    total: int
    vs_previous_month: float
    transactions: list[Transaction]


class MonthlyReport(BaseModel):
    totals: MonthlyTotals
    categories: Dict[str, MonthlyCategoryReport]


def get_previous_month(dt: datetime):
    if dt.month == 1:
        previous_month = 12
    else:
        previous_month = dt.month - 1

    return datetime(dt.year, previous_month, 1)


def get_monthly_report(
    db: ApplicationState, state: MonthlyState, end_time: datetime
) -> MonthlyReport:
    total_spent = sum(map(lambda t: t.amount, state.transactions))
    total_remaining = state.monthly_income - total_spent

    unallocated = sum(map(lambda x: x.amount, state.fixed_expenses))

    totals = MonthlyTotals(
        income=state.monthly_income,
        spent=total_spent,
        remaining=total_remaining,
        unallocated=unallocated,
    )

    categories: dict[str, MonthlyCategoryReport] = {}
    for transaction in state.transactions:
        # only select transactions up until the given "end of report" date
        if transaction.created_at > end_time:
            continue

        if categories.get(transaction.category) is None:
            # if we don't have one already, create a new one initialized with the first transaction
            category_report = MonthlyCategoryReport(
                category=transaction.category,
                total=transaction.amount,
                vs_previous_month=0,
                transactions=[transaction],
            )
            categories[transaction.category] = category_report
        else:
            # we already have a category, append
            category_report = categories.get(transaction.category)

            category_report.transactions.append(transaction)
            category_report.total += transaction.amount

    # now we have a mapping of all categories, and we need to calculate the vs. previous months
    previous_month_key = state.key_for_date(get_previous_month(end_time))
    if not db.state.get(previous_month_key):
        # don't bother summing, because we have nothing to do
        return MonthlyReport(totals=totals, categories=categories)

    previous_month_state = db.state.get(previous_month_key)

    day_count = end_time.day
    for category in categories.values():
        previous_sum = 0

        # Yes, this is O(n^2), but you know what else isn't optimal?  You.
        for transaction in previous_month_state.transactions:
            if transaction.created_at.day > day_count:
                break

            if transaction.category != category.category:
                continue

            previous_sum += transaction.amount

        # category: MonthlyCategoryReport
        if previous_sum:
            result = category.total / previous_sum  # e.g. 100 / 90 = 1.11
            result = result * 100  # e.g. 111
            category.vs_previous_month = result - 100  # e.g. 111-100 = 11%

    return MonthlyReport(totals=totals, categories=categories)
