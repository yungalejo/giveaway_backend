from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from app.models import *

load_dotenv()
mongo_url = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(mongo_url)

sample = {
  "date": datetime.now,
  "tweet": "string",
  "discord": "string",
  "prizeType": "N/A",
  "prizeAmount": 0,
  "checks": {
    "follow": True,
    "like": True,
    "repost": True,
    "addtl": True
  }
}

test = Giveaway(**sample)

test.status = 'active'

test.status

test


