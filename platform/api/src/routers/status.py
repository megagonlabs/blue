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
# connection: Redis = PooledConnectionFactory(properties={'db.host': PROPERTIES["db.host"], 'db.port': PROPERTIES["db.port"]}).get_connection()
# pubsub = connection.pubsub()


@router.get("/platform")
async def stream_data(request: Request):
    async def generate(should_stop):
        # await pubsub.subscribe(f"PLATFORM:{PLATFORM_PREFIX}")
        while True:
            if should_stop.is_set():
                break
            yield f"event: platform_status\ndata: {json.dumps({'name': 'r'})}\n\n"
            await asyncio.sleep(2)
            # message = await pubsub.get_message()
            # print(message)
            # if message and message["type"] == "message":
            #     yield f"data: {message['data'].decode()}"
            #     await asyncio.sleep(2)  # adjust sleep as needed

    return StreamingResponse(generate(should_stop), media_type="text/event-stream")
