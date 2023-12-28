from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
def get_agents():
    return JSONResponse(content={})
