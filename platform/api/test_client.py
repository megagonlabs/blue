import json
import uuid

from websocket import create_connection

ws = create_connection("ws://localhost:5000/sessions")
result = ws.recv()
client_id = json.loads(result)["id"]
try:
    while True:
        message = input("message?")
        ws.send(
            json.dumps(
                {
                    "type": "message",
                    "session": f"session-{uuid.uuid4()}",
                    "content": message,
                }
            )
        )
except KeyboardInterrupt:
    ws.close()
