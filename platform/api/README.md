## Run API server
Under `platform/api/`
- Install dependencies: `pip install -r src/requirements.txt`
- Run script (copy libs): `./docker_build_api.sh`
- Start server: `uvicorn server:app --app-dir src --port 5050 --reload`
  - To set environment variables inside `.env` : `set -a; source .env; set +a`

## API Documentation

Check out [SwaggerUI](http://localhost:5050/docs)

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
