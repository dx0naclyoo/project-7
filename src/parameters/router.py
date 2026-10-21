from fastapi import APIRouter

from src.db import Connection
from src.parameters.schemas import UserParametersCreate, UserParametersResponse
from src.parameters.service import ParametersService

router = APIRouter(prefix="/users/parameters", tags=["parameters"])

@router.post("/", status_code=201, response_model=UserParametersResponse)
async def create_parameters(
data: UserParametersCreate, conn: Connection
) -> UserParametersResponse:
    return await ParametersService(conn).create(data)
