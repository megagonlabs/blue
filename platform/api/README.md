## Run API server
Under `platform/api/`
- Install dependencies: `pip install -r requirements.txt`
- Start server: `uvicorn server:app --port 5000 --reload`

## Add routes
> For more detailed documentation, check out [APIRouter](https://fastapi.tiangolo.com/reference/apirouter/) class.
> 
Import router files inside `server.py` file
```py
# platform/api/server.py
from routers import agents
```
Under `platform/api/routers`
```py
# <name>.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix='<name>')


@router.get("/")
def get_example():
    return JSONResponse(content={})
```
## Send websocket message
Under `platform/api/`
- `python test_client.py`