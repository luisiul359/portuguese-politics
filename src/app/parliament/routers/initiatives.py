import time

from fastapi import APIRouter

from src.app.parliament.models.initiatives import Iniciativa, ProjectoPropostaLei
from src.app.parliament.models.parliament import Legislature
from src.app.parliament.services.initiatives import get_initiative as service_get_initiative


router = APIRouter(
    prefix="/initiatives",
    tags=["Initiative"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

# For future initiative types, they should inherit from Iniciativa
# and also be added as Union[type1, type2, ...] on the response model
@router.get("/{id}", response_model=ProjectoPropostaLei)
def get_initiative(id: int, legislature: Legislature = Legislature.XV) -> Iniciativa:
    #timer = time.time()
    initiative = service_get_initiative(int(id), legislature)
    #print(f"Timer {time.time() - timer:0.3}")
    return initiative
