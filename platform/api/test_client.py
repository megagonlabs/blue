import json
import uuid

from websocket import create_connection

ws = create_connection("ws://localhost:5000/sessions/ws")
result = ws.recv()
client_id = json.loads(result)["id"]
try:
    while True:
        message = input("message?")
        ws.send(
            json.dumps(
                {
                    "type": "message",
                    "session_id": str(uuid.uuid4()),
                    "content": message,
                }
            )
        )
except KeyboardInterrupt:
    ws.close()
