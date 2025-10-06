import json
import time
from fastapi import Depends, Request
from fastapi.responses import StreamingResponse
from redis import Redis
from APIRouter import APIRouter
from constant import END_OF_EVENT_SIGNAL
from authorizations.utils import account_id_header, acl_enforce
from blue.properties import PROPERTIES
from blue.connection import PooledConnectionFactory
import asyncio
from server import should_stop

platform_id = PROPERTIES["platform.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/status", dependencies=[Depends(account_id_header)])
connection: Redis = PooledConnectionFactory(properties={'db.host': PROPERTIES["db.host"], 'db.port': PROPERTIES["db.port"]}).get_connection()


@router.get("/")
async def stream_data(request: Request):
    acl_enforce(request.state.user['role'], 'platform_status', ['read_all'])

    async def generate():
        pubsub = connection.pubsub()
        pubsub.psubscribe("*:TRACKER:PERF")
        while True:
            if should_stop.is_set():
                data = {'epoch': time.time(), 'line': END_OF_EVENT_SIGNAL}
                yield f"event: message\ndata: {json.dumps(data)}\n\n"
                break
            message = pubsub.get_message()
            if message and message["type"] == "pmessage":
                data = {'data': json.loads(message['data']), 'channel': message['channel']}
                yield f"event: message\ndata: {json.dumps(data)}\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(generate(), media_type="text/event-stream")
