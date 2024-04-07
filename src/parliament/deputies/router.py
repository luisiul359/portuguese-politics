import httpx
from fastapi import APIRouter, HTTPException
from parliament.deputies.mapper import get_absences, map_to_deputies
from parliament.deputies.model import CirculoEleitoral, Deputado, DescricaoSituacaoDeputado, AusenciasDeputado, SituacaoDeputado
from parliament.model import Legislatura


router = APIRouter(
    prefix="/hemiciclo/deputados",
    tags=["Deputados"],
    responses={404: {"description": "Not found"}},
)

PATH_DEPUTY_ACTIVITIES_XV = f"https://app.parlamento.pt/webutils/docs/doc.txt?path=5HkcoxZtIW435A4jY873hYI6kfnIvwq2vw8efGiSKZ%2bF8GtZEjctfXdoRHRpewiAnH5yA9uC7Gy4RiXnloYfuJGpG3SIXiWROpvUgzMel8Hl6W5%2borom9A%2fwAMW7oAnXTRhUzobKyDsyFvvjyQ2dK1NhBy2EJ0Hgl%2bYu1b5xJldH2CHH3xsiS9HWLNIs6QQrvNSHra5fIijKudD%2fXCfvr1vgBfvAGeTWNQcC2vTBORfP31nyrGYX6wHhXHx%2fmnC1n1%2bMZ2nLzEfjQwbT8iISMUrtXEPccjsKyIhn2ts0tdGs%2f530BvZpu2LJsFbwratms8RwihlLJbnlS69UlBhREyuEZ8f1n2OqCTq7SKPCOAyz4wZzcFd0eA11fsgz5Cco&fich=AtividadeDeputadoXV_json.txt"
PATH_PARLIAMENT_STRUCTURE_XV = f"https://app.parlamento.pt/webutils/docs/doc.txt?path=W9RaCZUGiT6SODLmMBkS6szZ8N7mdM13t%2fl3EX%2bwogn%2bK40mYgU4HIzKi0jinWxmn6Br2A7JrikIvIhNfYatbv%2bRmJcTNJ4kgGr7hSyrb9ltxZhNuN9CcI7sFPm2ADYGWZ4g%2bWYZ7zcU26T3cVV%2fBN1kB5XzzAcbZ5K8l9yq%2bGa7uo8eXqzqmRrFNrh57oLlqHmUAr0vWgXJJxFzWVMKSSeAgf4qC7regF1uS4%2f6O71Tu7%2bCNu1RY83ZYFv7hGj8eDC4OSI%2fAVmOCuROBAH54lcsioY1fw3hxO1ylwG4a5hNwQdV5bvLCSXkp46oOt0rHEzN9XW0Oy1PYE8fQPLIZz40SDY%2fNpybt4BWHTpqfr7%2brVLQXlEEfft9YIkFs2qN5MZD7Fx3uIBsfoN%2bN6YuTA%3d%3d&fich=OrgaoComposicaoXV_json.txt"
TOTAL_DEPUTIES = 230


@router.get(
    path="/",
    description="Retorna por defeito todos os 230 Deputados com assento parlamentar na actual Legislatura.",
    name="",
    response_description="Lista de 230 Deputados"
)
async def get_deputies(
    id: int | None = None,
    siglaPartido: str | None = None,
    circuloEleitoral: CirculoEleitoral | None = None,
    legislatura: Legislatura = Legislatura.XV, #hardcoded
) -> list[Deputado]:
    parliament_data = await get_parliament_data(PATH_DEPUTY_ACTIVITIES_XV, legislatura)

    deputies = hemycicle_deputies(map_to_deputies(parliament_data))

    if len(deputies) != TOTAL_DEPUTIES:
        raise HTTPException(status_code=500, detail=f"Inconsistência nos deputados recolhidos: {len(deputies)} visto que no total são {TOTAL_DEPUTIES}.")
    
    return filter_by(
        id=id,
        party_acronym=siglaPartido,
        electoral_district=circuloEleitoral,
        deputies=deputies
    )


async def get_parliament_data(path: str, legislature: Legislatura) -> any:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(define_legislature(path, legislature), timeout=None)
            assert response.status_code == 200
            return response.json()
        except Exception as e:
            raise e


def define_legislature(path: str, legislature: Legislatura) -> str:
    if (path == PATH_DEPUTY_ACTIVITIES_XV and legislature == Legislatura.XV):
        return PATH_DEPUTY_ACTIVITIES_XV
    if (path == PATH_PARLIAMENT_STRUCTURE_XV and legislature == Legislatura.XV):
        return PATH_PARLIAMENT_STRUCTURE_XV


def filter_by(
    deputies: list[Deputado],
    id: int | None = None,
    party_acronym: str | None = None,
    electoral_district: CirculoEleitoral | None = None
) -> list[Deputado]:
    result = deputies

    if (id is not None):
        result = [next(deputy for deputy in deputies if id == deputy.id)]
    if (party_acronym is not None):
        result = [deputy for deputy in result if deputy.grupoParlamentar[0].sigla == party_acronym]
    if (electoral_district is not None):
        result = [deputy for deputy in result if deputy.circuloEleitoral == electoral_district]
    
    return result


def hemycicle_deputies(deputies: list[Deputado]) -> list[Deputado]:
    return [deputy for deputy in deputies if is_active(deputy)]


def is_active(deputy: Deputado) -> bool:
    for situation in deputy.situacao:
        if not is_valid(situation):
            return False
    return True


def is_valid(situation: SituacaoDeputado) -> bool:
    if (situation.dataFim is None):
        match situation.descricao:
            case DescricaoSituacaoDeputado.SUPLENTE | DescricaoSituacaoDeputado.SUSPENSO_ELEITO | DescricaoSituacaoDeputado.RENUNCIOU:
                return False
    return True


@router.get(
    path="/{id}/ausencias",
    description="Retorna as faltas de um Deputado com assento parlamentar na actual Legislatura em reuniões de Plenário.",
    name="",
    response_description="Faltas do Deputado"
)
async def get_deputy_absences(id: int, legislature: Legislatura = Legislatura.XV) -> AusenciasDeputado:
    parliament_data = await get_parliament_data(PATH_PARLIAMENT_STRUCTURE_XV, legislature)

    return get_absences(0, parliament_data)
