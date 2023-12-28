from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/agents")


@router.get("/")
def get_agents():
    return JSONResponse(content={})
