from fastapi import APIRouter
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from parliament.mappers.agenda import map_to_upcoming_events
from parliament.models.agenda import EventoAgenda


agenda_router = APIRouter(
    prefix="/agenda",
    tags=["Agenda"],
    responses={
        500: { "mensagem": "Erro interno do servidor" }
    },
)


PATH_PARLIAMENT_AGENDA_XVI = f"https://app.parlamento.pt/webutils/docs/doc.txt?path=WF3U%2fWKcx%2bnBGl9NaUbw9xKeCGlzUtS6xFHOa6F64ZhsuDPSUUqmHm%2fPK19vgo9ChlEcQ29gl3AyGx%2fDUmY8F0gjTzU4aY3tQ0%2bV3BPEe3cmQTp9K1lFGXsemVy1AkavtzNtHVs316ykSDMNVIpvaxN4axCSgMrC0SUPeFGlKFKOnv4TI5Xy1%2f2XVBqdM5cEvDhEz9Ngfqm9AcKszXcTGism8hpUzX3KDwZ6WXFz2paF5pr9fUIq%2b%2biXJWtn3BqccSw2YfLBJfVNP9c1kr1hKyUtJRIaYRBePddzE9kflhS5yQJTiE%2fkScxzrO9A3w8yxzgm68txLohSBMGikRwBvasI43hiY7AiFlGKbY6OT%2bdFTR4ELYJ6wmSPcBrxDrkb&fich=AgendaParlamentar_json.txt"


@agenda_router.get(
    path="",
    description="Retorna os próximos eventos agendados na Assembleia da República.",
    name="",
    response_description="Próximos eventos agendados na presente Legislatura"
)
async def get_agenda() -> list[EventoAgenda]:
    async with AsyncClient() as client:
        response = await client.get(PATH_PARLIAMENT_AGENDA_XVI, timeout=None)
        
        if (response.status_code != 200):
            return JSONResponse({"mensagem": "Erro ao obter dados no parlamento.pt. Por favor tente mais tarde."}, response.status_code)
        
        parliament_data = response.json()
        return map_to_upcoming_events(parliament_data)

