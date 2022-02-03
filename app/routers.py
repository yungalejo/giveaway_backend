import re
from uuid import uuid4

from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder

from .models import *

router = APIRouter(prefix="/giveaways", tags=["giveaways"])


@router.post("/create")
async def create_giveaway(giveaway: Giveaway, request: Request):
    hist = request.app.mongodb.giveaway_history
    giveaway.status = "active"
    giveaway = jsonable_encoder(giveaway)
    await hist.insert_one(giveaway)
    return giveaway


@router.get("/")
async def list_giveaways(request: Request):
    collection = request.app.mongodb.giveaway_history
    giveaways = [i async for i in collection.find({})]
    return giveaways


@router.get("/{id}")
async def show_giveaway(id: str, request: Request):
    collection = request.app.mongodb.giveaway_history
    return await collection.find_one({"_id": id})


@router.delete("/{id}")
async def delete_giveaway(id: str, request: Request):
    collection = request.app.mongodb.giveaway_history
    await collection.delete_one({"_id": id})
