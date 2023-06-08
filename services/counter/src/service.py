import asyncio

import websockets

async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
            print(message)
            l = len(message)
            print(l)
            await websocket.send(str(l))
        except websockets.ConnectionClosedOK:
            break

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
