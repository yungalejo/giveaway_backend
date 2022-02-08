from datetime import datetime
from lib2to3.pytree import Base
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
    retweet: bool
    likes_tweet: bool
    follow: bool
    addtl: bool


class data(BaseModel):
    retweeted_by: Optional[list[str]]
    liked_by: Optional[list[str]]
    followers: Optional[list[str]]
    addtl_followers: Optional[list[str]]


class user(BaseModel):
    id: str
    username: str


class Giveaway(BaseModel):
    id: str = Field(default_factory=uuid4, alias="_id")
    start_date: datetime = datetime.now()
    end_date: datetime
    status: Optional[Status]
    tweet_id: str
    discord: Optional[str]
    prizeType: str = "N/A"
    prizeAmount: float = 0
    addtl_username: Optional[str]
    conditions: Conditions
    participants_data: Optional[data]
    winner: Optional[list[user]]

    class Config:
        allow_population_by_field_name = True
