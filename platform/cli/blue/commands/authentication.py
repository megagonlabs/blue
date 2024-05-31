import os
from blue.commands.profile import ProfileManager
import websockets
from websockets import exceptions as ws_exceptions
import asyncio
import json
import os
import subprocess
import sys
import time
import webbrowser


class Authentication:
    def __init__(self) -> None:
        self.__WEB_PORT = 25830
        self.__SOCKET_PORT = 25831
        self.cookie = None
        self.__start_servers()

    def get_cookie(self):
        return self.cookie

    def __set_cookie(self, cookie):
        if cookie == "":
            cookie = None
        self.cookie = cookie

    def __start_servers(self):
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "http.server",
                    str(self.__WEB_PORT),
                    "-b",
                    "localhost",
                    "-d",
                    f"{path}/web/auth/out",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            time.sleep(2)
            webbrowser.open(f"http://localhost:{self.__WEB_PORT}")
            self.stop = asyncio.Future()

            async def handler(websocket):
                data = None
                while True:
                    try:
                        data = await websocket.recv()
                        json_data = json.loads(data)
                        if json_data == "REQUEST_CONNECTION_INFO":
                            current_profile = ProfileManager().get_selected_profile()
                            await websocket.send(json.dumps({"type": "REQUEST_CONNECTION_INFO", "message": dict(current_profile)}))
                        else:
                            await websocket.send(json.dumps("done"))
                    except ws_exceptions.ConnectionClosedOK:
                        break
                    except ws_exceptions.ConnectionClosedError:
                        break
                    except Exception as ex:
                        await websocket.send(json.dumps({"error": str(ex)}))
                self.stop.set_result(json_data)

            async def main():
                async with websockets.serve(handler, "", self.__SOCKET_PORT):
                    self.__set_cookie(await self.stop)
                    if self.process is not None:
                        self.process.terminate()

            asyncio.run(main())
        except OSError as ex:
            if self.process is not None:
                self.process.terminate()
            raise Exception(ex)
        except KeyboardInterrupt as ex:
            self.stop.set_result(None)
