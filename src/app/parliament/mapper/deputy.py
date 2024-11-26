from app.parliament.model.deputy import CargoDeputado, CirculoEleitoral, CirculoEleitoralDeputado, Deputado, DescricaoCargoDeputado, DescricaoSituacaoDeputado, GrupoParlamentar, NomeGrupoParlamentar, SiglaGrupoParlamentar, SituacaoDeputado


def map_to_deputies(data: any) -> list[Deputado]:
    deputies_activities = data["ArrayOfAtividadeDeputado"]["AtividadeDeputado"]
    full_deputies_list = [item["deputado"] for item in deputies_activities]

    return [Deputado(
        id=deputy["depId"],
        cadastroId=deputy["depCadId"],
        nomeParlamentar=deputy["depNomeParlamentar"],
        nomeCompleto=deputy["depNomeCompleto"],
        grupoParlamentar=map_to_grupo_parlamentar(deputy),
        circuloEleitoral=map_to_electoral_district(deputy),
        situacao=map_to_status(deputy),
        cargo=map_to_position(deputy),
        legislatura=deputy["legDes"]
    ) for deputy in full_deputies_list]


# As the deputy party can be a list, we assume a list by default
# Ex: a deputy moved from a party to independent
def map_to_grupo_parlamentar(deputy: any) -> GrupoParlamentar:
    groups = deputy["depGP"]["pt_ar_wsgode_objectos_DadosSituacaoGP"]

    if (type(groups) is list):
        return [GrupoParlamentar(
        id=group["gpId"],
        sigla=map_to_pg_acronym(group["gpSigla"]),
        nome=map_to_pg_name(group["gpSigla"]),
        dataInicio=group["gpDtInicio"],
        dataFim=group["gpDtFim"]
    ) for group in groups]

    return [GrupoParlamentar(
        id=groups["gpId"],
        sigla=map_to_pg_acronym(groups["gpSigla"]),
        nome=map_to_pg_name(groups["gpSigla"]),
        dataInicio=groups["gpDtInicio"],
        dataFim=groups["gpDtFim"]
    )]


def map_to_electoral_district(deputy: any) -> CirculoEleitoralDeputado:
    return CirculoEleitoralDeputado(
        id=deputy["depCPId"],
        nome=CirculoEleitoral(deputy["depCPDes"])
    )


# As the deputy status can be a list, we assume a list by default
def map_to_status(deputy: any) -> list[SituacaoDeputado]:
    statuses = deputy["depSituacao"]["pt_ar_wsgode_objectos_DadosSituacaoDeputado"]

    if (type(statuses) is list):
        return [SituacaoDeputado(
        descricao=map_to_status_desc(status["sioDes"]),
        dataInicio=status["sioDtInicio"],
        dataFim=status["sioDtFim"] if "sioDtFim" in status else None
    ) for status in statuses]

    return [SituacaoDeputado(
        descricao=map_to_status_desc(statuses["sioDes"]),
        dataInicio=statuses["sioDtInicio"],
        dataFim=statuses["sioDtFim"] if "sioDtFim" in statuses else None
    )]


def map_to_position(deputy: any) -> CargoDeputado | None:
    if ("depCargo" not in deputy):
        return None
    else:
        position = deputy["depCargo"]["pt_ar_wsgode_objectos_DadosCargoDeputado"]

        return CargoDeputado(
            id=position["carId"],
            descricao=map_to_position_desc(position["carDes"]),
            dataInicio=position["carDtInicio"],
            dataFim=position["carDtFim"] if "carDtFim" in position else None
        )


def map_to_position_desc(position: str) -> DescricaoCargoDeputado:
    match position:
        case "Presidente":
            return DescricaoCargoDeputado.PRESIDENTE
        case "Secretário":
            return DescricaoCargoDeputado.SECRETARIO
        case "Vice-Presidente":
            return DescricaoCargoDeputado.VICE_PRESIDENTE
        case "Vice-Secretário":
            return DescricaoCargoDeputado.VICE_SECRETARIO
        case _:
            raise NameError(position)


def map_to_status_desc(status: str) -> DescricaoSituacaoDeputado:
    match status:
        case "Efetivo":
            return DescricaoSituacaoDeputado.EFECTIVO
        case "Efetivo Definitivo":
            return DescricaoSituacaoDeputado.EFECTIVO_DEFINITIVO
        case "Efetivo Temporário":
            return DescricaoSituacaoDeputado.EFECTIVO_TEMPORARIO
        case "Impedido":
            return DescricaoSituacaoDeputado.IMPEDIDO
        case "Renunciou":
            return DescricaoSituacaoDeputado.RENUNCIOU
        case "Suplente":
            return DescricaoSituacaoDeputado.SUPLENTE
        case "Suspenso(Não Eleito)":
            return DescricaoSituacaoDeputado.SUSPENSO_NAO_ELEITO
        case "Suspenso(Eleito)":
            return DescricaoSituacaoDeputado.SUSPENSO_ELEITO
        case _:
            raise NameError(status)


def map_to_pg_acronym(party_acronym: str) -> SiglaGrupoParlamentar:
    match party_acronym:
        case "BE":
            return SiglaGrupoParlamentar.BE
        case "CDS-PP":
            return SiglaGrupoParlamentar.CDS_PP
        case "CH":
            return SiglaGrupoParlamentar.CH
        case "IL":
            return SiglaGrupoParlamentar.IL
        case "L":
            return SiglaGrupoParlamentar.L
        case "Ninsc":
            return SiglaGrupoParlamentar.NI
        case "PAN":
            return SiglaGrupoParlamentar.PAN
        case "PCP":
            return SiglaGrupoParlamentar.PCP
        case "PS":
            return SiglaGrupoParlamentar.PS
        case "PSD":
            return SiglaGrupoParlamentar.PSD        
        case _:
            raise NameError(party_acronym)


def map_to_pg_name(party_acronym: str) -> NomeGrupoParlamentar:
    match party_acronym:
        case "BE":
            return NomeGrupoParlamentar.BE
        case "CDS-PP":
            return NomeGrupoParlamentar.CDS_PP
        case "CH":
            return NomeGrupoParlamentar.CH
        case "IL":
            return NomeGrupoParlamentar.IL
        case "L":
            return NomeGrupoParlamentar.L
        case "Ninsc":
            return NomeGrupoParlamentar.NI
        case "PAN":
            return NomeGrupoParlamentar.PAN
        case "PCP":
            return NomeGrupoParlamentar.PCP
        case "PS":
            return NomeGrupoParlamentar.PS
        case "PSD":
            return NomeGrupoParlamentar.PSD
        case _:
            raise NameError(party_acronym)
