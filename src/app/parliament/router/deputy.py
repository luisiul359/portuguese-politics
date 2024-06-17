from app.parliament.mapper.deputy import map_to_deputies
from app.parliament.model.deputy import CirculoEleitoral, Deputado, DescricaoSituacaoDeputado, SituacaoDeputado
from app.parliament.model.legislature import Legislatura
from app.parliament.temp_constants import PATH_DEPUTY_ACTIVITIES_XV, PATH_DEPUTY_ACTIVITIES_XVI
import httpx
from fastapi import APIRouter, HTTPException

from app.parliament.common import current_legislature 


deputy_router = APIRouter(
    prefix="/deputados",
    tags=["Deputados"],
     responses={
        500: { "mensagem": "Erro interno do servidor" }
    }
)

TOTAL_DEPUTIES = 230


@deputy_router.get(
    path="/hemiciclo",
    description="Retorna por defeito todos os 230 Deputados com assento parlamentar na actual Legislatura.",
    name="",
    response_description="Lista de 230 Deputados"
)
async def get_deputies(
    id: int | None = None,
    siglaPartido: str | None = None,
    circuloEleitoral: CirculoEleitoral | None = None,
    legislatura: Legislatura = current_legislature
) -> list[Deputado]:
    parliament_data = await get_parliament_data(legislatura)

    deputies = hemycicle_deputies(map_to_deputies(parliament_data))

    if (len(deputies) != TOTAL_DEPUTIES):
        raise HTTPException(status_code=500, detail=f"Inconsistência nos deputados recolhidos. {len(deputies)}/{TOTAL_DEPUTIES}.")

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
    match legislature:
        case Legislatura.XV:
            return PATH_DEPUTY_ACTIVITIES_XV 
        case Legislatura.XVI:
            return PATH_DEPUTY_ACTIVITIES_XVI
        case _:
            return NameError(f"Legislatura inválida. ${legislature} não é válida.")


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
        if (not is_valid(situation)):
            return False
    return True


def is_valid(situation: SituacaoDeputado) -> bool:
    if (situation.dataFim is None):
        match situation.descricao:
            case (DescricaoSituacaoDeputado.SUPLENTE |
                  DescricaoSituacaoDeputado.SUSPENSO_ELEITO |
                  DescricaoSituacaoDeputado.SUSPENSO_NAO_ELEITO |
                  DescricaoSituacaoDeputado.RENUNCIOU):
                return False
    return True
