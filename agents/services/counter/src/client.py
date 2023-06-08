import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:8001") as websocket:
        await websocket.send("Hello world!")
        message = await websocket.recv()
        print(f"Received: {message}")

if __name__ == "__main__":
    asyncio.run(hello())
