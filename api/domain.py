from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

Category = str


class FixedExpense(BaseModel):
    category: Category
    amount: int


class User(BaseModel):
    name: str
    email: str
    password_hash: Optional[str]


class Transaction(BaseModel):
    category: Category
    amount: int
    created_at: datetime
    title: Optional[str]
    notes: Optional[str]


class StateDefaults(BaseModel):
    monthly_income: int
    fixed_expenses: list[FixedExpense]


class MonthlyState(BaseModel):
    monthly_income: int
    fixed_expenses: list[FixedExpense]
    transactions: list[Transaction]

    def key_for_date(dt: datetime):
        return dt.strftime("%m/%y")

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
