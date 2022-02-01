from datetime import date
from multiprocessing import allow_connection_pickling
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Conditions(BaseModel):
    follow: bool
    like: bool
    repost: bool
    addtl: bool


class Giveaway(BaseModel):
    id: str = Field(default_factory=uuid4, alias="_id")
    date: date
    tweet: str
    discord: Optional[str]
    prizeType: str
    prizeAmount: float
    checks: Conditions

    class Config:
        allow_population_by_field_name = True
