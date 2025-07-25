from pydantic import BaseModel
from typing import List, Optional
import datetime

class Strategy(BaseModel):
    id: int
    name: str
    code: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

class Bundle(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

class Run(BaseModel):
    id: int
    strategy_id: int
    bundle_id: int
    start_date: datetime.date
    end_date: datetime.date
    capital_base: float
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

class Result(BaseModel):
    id: int
    run_id: int
    pnl: float
    sharpe: float
    max_drawdown: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
