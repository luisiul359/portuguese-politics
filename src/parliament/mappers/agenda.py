from parliament.mappers.legislature import map_to_legislature
from parliament.models.agenda import AnexosAgenda, EventoAgenda, SessaoAgenda, TemaAgenda


# TODO: mapping is failing with latest requests
def map_to_upcoming_events(events: any) -> list[EventoAgenda]:
    return [EventoAgenda(
        id=event["Id"],
        titulo=event["Title"],
        subTitulo=None if "Subtitle" not in event else event["Subtitle"],
        sessao=SessaoAgenda(
            id=event["SectionId"],
            descricao=event["Section"]
        ),
        tema=TemaAgenda(
            id=event["ThemeId"],
            descricao=event["Theme"]
        ),
        ordem=event["OrderValue"],
        grupoParlamentarId=event["ParlamentGroup"],
        dataInicio=event["EventStartDate"],
        horaInicio=None if "EventStartTime" not in event else event["EventStartTime"],
        dataFim=event["EventEndDate"],
        horaFim=None if "EventEndTime" not in event else event["EventEndTime"],
        textoHtml=event["InternetText"],
        local=None if "Local" not in event else event["Local"],
        orgao=None if "OrgaoDes" not in event else event["OrgaoDes"],
        numeroReuniao=None if "ReuNumero" not in event else event["ReuNumero"],
        sessaoLegislativa=None if "SelNumero" not in event else event["SelNumero"],
        ocorreAposSessaoPlenaria=event["PostPlenary"],
        anexosComissaoPermanente=map_to_attaches(event["AnexosComissaoPermanente"]),
        anexosPlenario=map_to_attaches(event["AnexosPlenario"]),
        link=None if "Link" not in event else event["Link"],
        duracaoDiaInteiro=event["AllDayEvent"],
        legislatura=map_to_legislature(event["LegDes"])
    ) for event in events]


def map_to_attaches(event: any) -> list[AnexosAgenda] | None:
    if (event):
        return [AnexosAgenda(
        id=attach["idField"],
        tipoDocumento=attach["tipoDocumentoField"],
        titulo=attach["tituloField"],
        link=attach["uRLField"]
        ) for attach in event]
    return None
