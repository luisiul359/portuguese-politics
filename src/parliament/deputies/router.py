import httpx
from fastapi import APIRouter, HTTPException
from parliament.deputies.mapper import map_to_deputies
from parliament.deputies.model import CirculoEleitoral, Deputado, DescricaoSituacaoDeputado, SituacaoDeputado
from parliament.model import Legislatura


router = APIRouter(
    prefix="/deputados",
    tags=["Deputados"],
    responses={404: {"description": "Not found"}},
)

PATH_DEPUTY_ACTIVITIES_XV = f"https://app.parlamento.pt/webutils/docs/doc.txt?path=5HkcoxZtIW435A4jY873hYI6kfnIvwq2vw8efGiSKZ%2bF8GtZEjctfXdoRHRpewiAnH5yA9uC7Gy4RiXnloYfuJGpG3SIXiWROpvUgzMel8Hl6W5%2borom9A%2fwAMW7oAnXTRhUzobKyDsyFvvjyQ2dK1NhBy2EJ0Hgl%2bYu1b5xJldH2CHH3xsiS9HWLNIs6QQrvNSHra5fIijKudD%2fXCfvr1vgBfvAGeTWNQcC2vTBORfP31nyrGYX6wHhXHx%2fmnC1n1%2bMZ2nLzEfjQwbT8iISMUrtXEPccjsKyIhn2ts0tdGs%2f530BvZpu2LJsFbwratms8RwihlLJbnlS69UlBhREyuEZ8f1n2OqCTq7SKPCOAyz4wZzcFd0eA11fsgz5Cco&fich=AtividadeDeputadoXV_json.txt"
TOTAL_DEPUTIES = 230


@router.get(
    path="/hemiciclo",
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
    parliament_data = await get_parliament_data(legislatura)

    deputies = hemycicle_deputies(map_to_deputies(parliament_data))

    if len(deputies) != TOTAL_DEPUTIES:
        raise HTTPException(status_code=500, detail=f"Inconsistência nos deputados recolhidos: {len(deputies)} visto que no total são {TOTAL_DEPUTIES}.")
    
    return filter_by(
        id=id,
        party_acronym=siglaPartido,
        electoral_district=circuloEleitoral,
        deputies=deputies
    )


async def get_parliament_data(legislature: Legislatura) -> any:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(define_legislature(legislature), timeout=None)
            assert response.status_code == 200
            return response.json()
        except Exception as e:
            raise e


def define_legislature(legislature: Legislatura) -> str:
    if (legislature.XV):
        return PATH_DEPUTY_ACTIVITIES_XV


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
