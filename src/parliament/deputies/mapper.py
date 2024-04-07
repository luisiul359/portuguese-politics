from parliament.deputies.model import CargoDeputado, CirculoEleitoral, CirculoEleitoralDeputado, Deputado, DescricaoCargoDeputado, DescricaoSituacaoDeputado, AusenciaReuniao, AusenciasDeputado, FaltaDeputado, GrupoParlamentar, NomeGrupoParlamentar, SiglaGrupoParlamentar, SituacaoDeputado


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
        case "L":
            return SiglaGrupoParlamentar.L
        case "PS":
            return SiglaGrupoParlamentar.PS
        case "PSD":
            return SiglaGrupoParlamentar.PSD
        case "PAN":
            return SiglaGrupoParlamentar.PAN
        case "BE":
            return SiglaGrupoParlamentar.BE
        case "IL":
            return SiglaGrupoParlamentar.IL
        case "CH":
            return SiglaGrupoParlamentar.CH
        case "PCP":
            return SiglaGrupoParlamentar.PCP
        case "Ninsc":
            return SiglaGrupoParlamentar.NI
        case _:
            raise NameError(party_acronym)


def map_to_pg_name(party_acronym: str) -> NomeGrupoParlamentar:
    match party_acronym:
        case "L":
            return NomeGrupoParlamentar.L
        case "PS":
            return NomeGrupoParlamentar.PS
        case "PSD":
            return NomeGrupoParlamentar.PSD
        case "PAN":
            return NomeGrupoParlamentar.PAN
        case "BE":
            return NomeGrupoParlamentar.BE
        case "IL":
            return NomeGrupoParlamentar.IL
        case "CH":
            return NomeGrupoParlamentar.CH
        case "PCP":
            return NomeGrupoParlamentar.PCP
        case "Ninsc":
            return NomeGrupoParlamentar.NI
        case _:
            raise NameError(party_acronym)


## Absences
def get_absences(id: int, data: any):
    meetings = data["OrganizacaoAR"]["Plenario"]["Reunioes"]["ReuniaoPlenario"]
    total_meetings = len(meetings)
    mock_name = "ANDRÉ VENTURA"
    mock_gp_acronym = "CH"
    absent_meetings: list[AusenciaReuniao] = []

    for meeting in meetings:
        deputies = meeting["Presencas"]["presencas"]["pt_gov_ar_wsgode_objectos_Presencas"]

        for deputy in deputies:
            if (is_absent(mock_name, mock_gp_acronym, deputy)):
                current_meeting = meeting["Reuniao"]
                
                absent_meetings.append(AusenciaReuniao(
                    id=current_meeting["reuId"],
                    data=meeting["Presencas"]["dtReuniao"],
                    falta=FaltaDeputado(
                        tipo=map_to_absence_desc(deputy["siglaFalta"]),
                        motivo=deputy["motivoFalta"]
                    )
                ))

    return AusenciasDeputado(
        numeroReunioes=total_meetings,
        numeroAusencias=len(absent_meetings),
        reunioesAusente=absent_meetings
    )


def is_absent(name: str, gp: str, deputy: any) -> bool:
    if (deputy["nomeDeputado"] == name and gp == deputy["siglaGrupo"] and "motivoFalta" in deputy):
        return True
    return False


def map_to_absence_desc(falta: str) -> str:
    match falta:
        case "QVJ" | "FJ":
            return "Falta Justificada"
        case "FI":
            return "Falta Injustificada"
        case "CO":
            return "Presença em Comissão autorizada pelo Presidente da Assembleia da República"
        case "ME" | "MP":
            return "Ausência em Missão Parlamentar (AMP)"
        case _:
            raise NameError(falta)
