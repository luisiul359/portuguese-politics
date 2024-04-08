import asyncio
import time

from fastapi import APIRouter

from src.parliament.parliament_model import Legislature
from .initiative_model import Iniciativa, ProjectoPropostaLei
from .initiative_service import get_initiative as service_get_initiative


router = APIRouter(
    prefix="/initiatives",
    tags=["Initiative"],
    responses={404: {"description": "Not found"}},
)

# For future initiative types, they could inherit from Iniciativa
# and also be added as Union[type1, type2, ...] on the response model
@router.get("/{id}", response_model=ProjectoPropostaLei)
async def get_initiative(id: int, legislature: Legislature = Legislature.XV) -> Iniciativa:
    timer = time.time() # just to test time with sync/async code
    initiative = await service_get_initiative(int(id), legislature)
    print(f"Timer {time.time() - timer:0.3}")
    return initiative
