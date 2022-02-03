from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from app.models import *
import json

load_dotenv()
mongo_url = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(mongo_url)

datetime.now

sample = {
    "end_date": datetime.now(),
    "tweet": "string",
    "discord": "string",
    "prizeType": "N/A",
    "prizeAmount": 0,
    "checks": {"follow": True, "like": True, "repost": True, "addtl": True},
}

test = Giveaway(**sample)

json.loads(test.json())
