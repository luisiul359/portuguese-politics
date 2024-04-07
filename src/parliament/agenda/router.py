from fastapi import APIRouter, HTTPException
import httpx
from parliament.agenda.mapper import map_to_upcoming_events
from parliament.agenda.model import EventoAgenda


router = APIRouter(
    prefix="/agenda",
    tags=["Agenda"],
    responses={404: {"description": "Not found"}},
)


PATH_PARLIAMENT_AGENDA_XVI = f"https://app.parlamento.pt/webutils/docs/doc.txt?path=WF3U%2fWKcx%2bnBGl9NaUbw9xKeCGlzUtS6xFHOa6F64ZhsuDPSUUqmHm%2fPK19vgo9ChlEcQ29gl3AyGx%2fDUmY8F0gjTzU4aY3tQ0%2bV3BPEe3cmQTp9K1lFGXsemVy1AkavtzNtHVs316ykSDMNVIpvaxN4axCSgMrC0SUPeFGlKFKOnv4TI5Xy1%2f2XVBqdM5cEvDhEz9Ngfqm9AcKszXcTGism8hpUzX3KDwZ6WXFz2paF5pr9fUIq%2b%2biXJWtn3BqccSw2YfLBJfVNP9c1kr1hKyUtJRIaYRBePddzE9kflhS5yQJTiE%2fkScxzrO9A3w8yxzgm68txLohSBMGikRwBvasI43hiY7AiFlGKbY6OT%2bdFTR4ELYJ6wmSPcBrxDrkb&fich=AgendaParlamentar_json.txt"


@router.get(
    path="",
    description="Retorna os próximos eventos agendados na Assembleia da República na presente Legislatura.",
    name="",
    response_description="Eventos"
)
async def get_upcoming_events() -> list[EventoAgenda]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/go", timeout=None)
            assert response.status_code != 200        
            parliament_data = response.json()
            return map_to_upcoming_events(parliament_data)
        except Exception as e:
            raise HTTPException(
                response.status_code,
                detail=f"Erro ao recolher dados no parlamento.pt. Por favor tente mais tarde. {e}"
            )
