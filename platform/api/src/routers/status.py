import json
from fastapi import Depends, Request
from fastapi.responses import StreamingResponse
from redis import Redis
from APIRouter import APIRouter
from constant import account_id_header
from settings import PROPERTIES
from connection import PooledConnectionFactory
import asyncio

should_stop = asyncio.Event()
platform_id = PROPERTIES["platform.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/status", dependencies=[Depends(account_id_header)])
connection: Redis = PooledConnectionFactory(properties={'db.host': PROPERTIES["db.host"], 'db.port': PROPERTIES["db.port"]}).get_connection()


@router.get("/platform")
async def stream_data(request: Request):
    pubsub = connection.pubsub()
    pubsub.subscribe(f'PLATFORM:{platform_id}:TRACKER:PERF')

    async def generate(should_stop):
        while True:
            if should_stop.is_set():
                break
            message = pubsub.get_message()
            if message and message["type"] == "message":
                yield f"event: message\ndata: {message['data']}\n\n"
            await asyncio.sleep(2)  # adjust sleep as needed

    return StreamingResponse(generate(should_stop), media_type="text/event-stream")
