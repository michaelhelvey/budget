from pydantic import BaseModel

from datetime import datetime
from typing import Optional, Dict

Category = str


class FixedExpense(BaseModel):
    category: Category
    amount: int


class User(BaseModel):
    email: str
    password_hash: Optional[str]


class Transaction(BaseModel):
    category: Category
    amount: int
    created_at: datetime
    title: Optional[str]
    notes: Optional[str]


class MonthlyState(BaseModel):
    monthly_income: int
    fixed_expenses: list[FixedExpense]
    transactions: list[Transaction]


class ApplicationState(BaseModel):
    users = list[User]
    last_accessed: datetime
    variable_categories: list[str]
    fixed_categories: list[str]
    state: Dict[str, MonthlyState]
