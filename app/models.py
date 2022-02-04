from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class Status(Enum):
    active = "active"
    ended = "ended"
    deleted = "deleted"
    waiting = "waiting"


class Conditions(BaseModel):
    follow: bool
    like: bool
    repost: bool
    addtl: bool


class Giveaway(BaseModel):
    id: str = Field(default_factory=uuid4, alias="_id")
    start_date: datetime = datetime.now()
    end_date: datetime
    status: Optional[Status]
    tweet: str
    discord: Optional[str]
    prizeType: str = "N/A"
    prizeAmount: float = 0
    addtl: Optional[str]
    checks: Conditions
    participants: Optional[list[str]]

    class Config:
        allow_population_by_field_name = True
