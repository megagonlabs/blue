import json
from fastapi import Depends
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


@router.get("/")
async def stream_data():
    pubsub = connection.pubsub()
    pubsub.psubscribe("*:TRACKER:PERF")

    async def generate(should_stop):
        while True:
            if should_stop.is_set():
                break
            message = pubsub.get_message()
            if message and message["type"] == "pmessage":
                data = {'data': json.loads(message['data']), 'channel': message['channel']}
                yield f"event: message\ndata: {json.dumps(data)}\n\n"
            await asyncio.sleep(2)  # adjust sleep as needed

    return StreamingResponse(generate(should_stop), media_type="text/event-stream")
