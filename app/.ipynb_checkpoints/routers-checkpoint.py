from fastapi import APIRouter, Request, Body
from .models import *
from uuid import uuid4


router = APIRouter(prefix="/giveaways", tags=["giveaways"])



@router.post("/create")
async def create_giveaway(giveaway: Giveaway, request: Request):
    db = request.app.mongodb
    return await db.list_collection_names()


@router.get("/{id}")
async def list_giveaways(id: int, request:Request):
    collection = request.app.mongodb.giveaway_history    
    giveaways = [i for i in collection.find()]
    
    return 

@    




