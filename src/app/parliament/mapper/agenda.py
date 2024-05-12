<<<<<<< HEAD
from ..mapper.legislature import map_to_legislature
from ..model.agenda import AnexosAgenda, EventoAgenda, SessaoAgenda, TemaAgenda
=======
from src.app.parliament.mapper.legislature import map_to_legislature
from src.app.parliament.model.agenda import AnexosAgenda, EventoAgenda, SessaoAgenda, TemaAgenda
>>>>>>> branch 'add-agenda' of git@github.com:luisiul359/portuguese-politics.git


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
    # The fields are not the same as presented in the metadata, link below:
    # https://app.parlamento.pt/webutils/docs/doc.pdf?path=041obKOV9FSHmwZTiBZj%2bx%2frymn6Gjix8M46ofLcACsEJU7ckopzQr2jpco6jQCmHpXc%2fv7toftUbo%2bQsYrGcqY%2fWFdM5TDglHtfcMQXmi7rrak33hh3xUQnoeTj6t53vHaS7e8VA26i3GH%2f7Ch6J4Quasz9DzkjnarGjBNeGlnePkuZtPWbRyHMYaCXIBj7mcCcFzX8HIWX8oS0MFX4LxcYGGG6G0ATMr2E8DlS3v%2b%2fHd4r5wjzYNaPSvYyzUJMptXNwOM8HCLxwO83TJh5iV5OaQWxZ%2fTLY7UW182KSrIMRDNbGhWyhdtTmKoYyDzH97V5nvnUIwJUMhVgMTDR4LQJtwIaQ%2fq%2bJlsUuey7Jkb6c8Z4hRpN7%2bHlOZuR%2bXUdHrHDSKUKyrR9UUm9YPHht5YSzCw1%2boFaueeNuCt%2bodA%3d&fich=Defini%c3%a7%c3%a3o+da+estrutura+dos+ficheiros.pdf&Inline=true
    # They were changed on the XVI legislature and updated accordingly
    if (event):
        return [AnexosAgenda(
        id=attach["id"],
        tipoDocumento=attach["TipoDocumento"],
        titulo=attach["Titulo"],
        link=attach["URL"]
        ) for attach in event]
    return None
