import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
mongo_url = os.getenv('MONGO_URL')

app = FastAPI()

origins = ['https://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event('startup')
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(mongo_url)
    app.mongodb = app.mongodb_client['Giveaway']


@app.on_event('shutdown')
async def shutdown_db_client():
    app.mongodb_client.close()


@app.get('/')
async def root():
    names = await app.mongodb.list_collection_names()
    return names


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
