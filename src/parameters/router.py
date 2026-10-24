from fastapi import APIRouter

from src.db import Connection
from src.parameters.schemas import UserParametersCreate, UserParametersResponse
from src.parameters.service import ParametersService

router = APIRouter(prefix="/users/parameters", tags=["parameters"])


@router.post("/", status_code=201, response_model=UserParametersResponse)
async def save_parameters(
    data: UserParametersCreate, conn: Connection
) -> UserParametersResponse:
    return await ParametersService(conn).save(data)


@router.get("/{user_id}", response_model=UserParametersResponse)
async def get_parameters(user_id: int, conn: Connection) -> UserParametersResponse:
    return await ParametersService(conn).get(user_id)
