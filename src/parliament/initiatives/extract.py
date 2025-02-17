import json
import sys
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List

import pandas as pd
from azure.storage.blob import ContainerClient as BlobContainerClient
from tqdm import tqdm

from src.parliament.common import MyDict, to_list

# endpoints updated daily
# XIV Legislatura
PATH_XIV = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d6c6a6157463061585a68637939595356596c4d6a424d5a57647063327868644856795953394a626d6c6a6157463061585a686331684a566c3971633239754c6e523464413d3d&fich=IniciativasXIV_json.txt&Inline=true"
# XV Legislatura
PATH_XV = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d6c6a6157463061585a6863793959566955794d45786c5a326c7a6247463064584a684c306c7561574e7059585270646d467a57465a66616e4e76626935306548513d&fich=IniciativasXV_json.txt&Inline=true"
# XVI Legislatura
PATH_XVI = "https://app.parlamento.pt/webutils/docs/doc.txt?path=9%2bS1R0rmlrJvA0k2UXLx9yXhooCL9aOS1uwNJphMqHhYpUJSfAZL3TuTXUSEdgr0rEqcbxbKyZ8kkqjsINFMLdFXsUnM%2ffrx2L%2bqlZZftbIFjCovRHvFD1l%2bEhYNkY5XJyJr8JB%2brn0T%2fU3ryaefr2nendsQE9PEZevIlvAUVSXpDfYXejIDMEK6PLJ1fAgqrpwN1mQ33joes2PSsmGkTJ16S7ccT94syYr4ehW2V3Kj3yAMuDHW68rp8MCMl1QfCCBu52Fo%2bhdG6ax7R5OHARHV0l8PXrC2deUDz1R6kaF7rIpQiSDX%2fRhM8E1OrXS%2fziFr1wbBtE1zThR4P%2basXA%3d%3d&fich=IniciativasXVI_json.txt&Inline=true"

ALL_PATHS = [
    ("XIV", PATH_XIV),
    ("XV", PATH_XV),
    ("XVI", PATH_XVI)
]

ONGOING_PATHS = [
    ("XV", PATH_XV),
    ("XVI", PATH_XVI)
]


def get_raw_data_from_blob(
    blob_container: BlobContainerClient, legislature_name: str
) -> List[Dict]:
    """Load the most recent data provided by Parlamento cached in our Blob Storage"""

    try:
        data = blob_container.get_blob_client(f"{legislature_name}.json")
        return json.loads(data.download_blob().readall())
    except Exception as e:
        print(blob_container.container_name)
        raise e


# TODO: Not updated
def get_initiatives_followups(raw_initiatives: List) -> pd.DataFrame:
    """Create a many to many relationship between initiatives (the main initiative and the folow-up)"""

    data_initiatives_followups = []
    for initiative in tqdm(
        raw_initiatives, "getting_initiatives_followups", file=sys.stdout
    ):
        # save all the initiative information to be stored
        info_to_store = {}

        info_to_store["iniciativa_id"] = initiative.get("iniId", "")
        info_to_store["iniciativa_nr"] = initiative.get("iniNr", "")

        initiatives_followups = initiative.get("iniciativasOriginadas", {}).get(
            "pt_gov_ar_objectos_iniciativas_DadosGeraisOut", []
        )
        if isinstance(initiatives_followups, Dict):
            initiatives_followups = [initiatives_followups]

        for initiative_followup in initiatives_followups:
            info_to_store_details = deepcopy(info_to_store)

            info_to_store_details["iniciativa_followup_id"] = initiative_followup.get(
                "id", ""
            )
            info_to_store_details["iniciativa_followup_nr"] = initiative_followup.get(
                "numero", ""
            )
            info_to_store_details[
                "iniciativa_followup_assunto"
            ] = initiative_followup.get("assunto", "")
            info_to_store_details["iniciativa_followup_desc"] = initiative_followup.get(
                "descTipo", ""
            )

            data_initiatives_followups.append(info_to_store_details)

    return pd.DataFrame(data_initiatives_followups)


# TODO: Not updated
def get_initiatives_petitions(raw_initiatives: List) -> pd.DataFrame:
    """Create a many to many relationship between initiatives and petitions"""

    data_initiatives_petitions = []
    for initiative in tqdm(
        raw_initiatives, "geting_initiatives_petitions", file=sys.stdout
    ):
        # save all the initiative information to be stored
        info_to_store = {}

        info_to_store["iniciativa_id"] = initiative.get("iniId", "")
        info_to_store["iniciativa_nr"] = initiative.get("iniNr", "")

        initiatives_petitions = initiative.get("peticoes", {}).get(
            "pt_gov_ar_objectos_iniciativas_DadosGeraisOut", []
        )
        if isinstance(initiatives_petitions, Dict):
            initiatives_petitions = [initiatives_petitions]

        for initiative_petition in initiatives_petitions:
            info_to_store_details = deepcopy(info_to_store)

            info_to_store_details["iniciativa_petition_id"] = initiative_petition.get(
                "id", ""
            )
            info_to_store_details["iniciativa_petition_nr"] = initiative_petition.get(
                "numero", ""
            )
            info_to_store_details[
                "iniciativa_petition_assunto"
            ] = initiative_petition.get("assunto", "")

            data_initiatives_petitions.append(info_to_store_details)

    return pd.DataFrame(data_initiatives_petitions)


def _get_author(initiative: pd.Series) -> str:
    """
    Get the correct author of an initiative. That information is spread among 3 columns
    """

    if initiative["iniciativa_autor_grupos_parlamentares"] == "":
        # initiative not from parliamentary groups or deputies
        if initiative["iniciativa_autor_deputados_GPs"] == "":
            return initiative["iniciativa_autor_outros_nome"]
        # when "iniciativa_autor_grupos_parlamentares" is not defined we fallback to iniciativa_autor_deputados_GPs
        else:
            # ensure we have the name of the unregistered deputy - split from his party midway through his term
            if initiative["iniciativa_autor_deputados_GPs"] == "Ninsc":
                return initiative["iniciativa_autor_deputados_nomes"]
            else:
                distribution = pd.Series(
                    initiative["iniciativa_autor_deputados_GPs"].split("|")
                ).value_counts()
                return "|".join(distribution.index.values)
    else:
        return initiative["iniciativa_autor_grupos_parlamentares"]


def _get_author_deputy(initiative: pd.Series) -> str:
    """
    Get the correct deputy author of an initiative. That information is spread among 3 columns
    """

    if initiative["iniciativa_autor_deputados_nomes"] == "":
        if initiative["iniciativa_autor_outros_nome"] == "Grupos Parlamentares":
            return initiative["iniciativa_autor_grupos_parlamentares"]
        else:
            return initiative["iniciativa_autor_outros_nome"]
    else:
        return initiative["iniciativa_autor_deputados_nomes"]


def get_initiatives(raw_initiatives: List) -> pd.DataFrame:
    """
    Parse parlamento API and return the main information of each initiative.

    Will return a raw version, i.e., a wide range of information that needs to be further parsed.

    Works until legislature XV.
    """

    data_initiatives = []
    for initiative in tqdm(raw_initiatives, "getting_initiatives", file=sys.stdout):
        # sometimes the `dict.get` works but it returns None,
        # with MyDict that won't happen
        initiative = MyDict(initiative)

        # save all the initiative information to be stored
        info_to_store = {}

        # initiative
        info_to_store["iniciativa_id"] = initiative.get("IniId", "")
        info_to_store["iniciativa_nr"] = initiative.get("IniNr", "")
        info_to_store["iniciativa_tipo"] = initiative.get("IniDescTipo", "")
        info_to_store["iniciativa_titulo"] = initiative.get("IniTitulo", "")
        info_to_store["iniciativa_url"] = initiative.get("IniLinkTexto", "")
        info_to_store["iniciativa_obs"] = initiative.get("IniObs", "")
        info_to_store["iniciativa_texto_subst"] = initiative.get(
            "IniTextoSubstCampo", ""
        )

        # iniAutorGruposParlamentares
        info_to_store["iniciativa_autor_grupos_parlamentares"] = "|".join(
            [
                MyDict(autor).get("GP", "")
                for autor in to_list(
                    initiative.get("IniAutorGruposParlamentares", [])
                )
            ]
        )

        # iniAutorOutros
        info_to_store["iniciativa_autor_outros_nome"] = initiative.get(
            "IniAutorOutros", {}
        ).get("nome", "")
        info_to_store["iniciativa_autor_outros_autor_comissao"] = initiative.get(
            "iniAutorOutros", {}
        ).get("iniAutorComissao", "")

        # iniAutorDeputados
        autor_deputados = to_list(
            initiative.get("IniAutorDeputados", [])
        )
        info_to_store["iniciativa_autor_deputados_nomes"] = "|".join(
            [MyDict(x).get("nome", "") for x in autor_deputados if x]
        )
        info_to_store["iniciativa_autor_deputados_GPs"] = "|".join(
            [MyDict(x).get("GP", "") for x in autor_deputados if x]
        )

        # iniAnexos
        anexos = to_list(
            initiative.get("IniAnexos", [])
        )
        info_to_store["iniciativa_anexos_nomes"] = "|".join(
            [MyDict(x).get("anexoNome", "") for x in anexos if x]
        )
        info_to_store["iniciativa_anexos_URLs"] = "|".join(
            [MyDict(x).get("anexoFich", "") for x in anexos if x]
        )

        # iniciativasOrigem
        origem = to_list(
            initiative.get("IniciativasOrigem", [])
        )
        info_to_store["iniciativa_origem_id"] = "|".join(
            [MyDict(x).get("id", "") for x in origem if x]
        )
        info_to_store["iniciativa_origem_nr"] = "|".join(
            [MyDict(x).get("numero", "") for x in origem if x]
        )
        info_to_store["iniciativa_origem_assunto"] = "|".join(
            [MyDict(x).get("assunto", "") for x in origem if x]
        )
        info_to_store["iniciativa_origem_desc"] = "|".join(
            [MyDict(x).get("descTipo", "") for x in origem if x]
        )

        # iniEventos
        #
        # each initiative can go through different stages / events until it is closed.
        # We will collect different information based on the stage / event
        events = to_list(
            initiative.get("IniEventos", [])
        )
        for event in events:
            info_to_store_details = deepcopy(info_to_store)

            info_to_store_details["iniciativa_evento_fase"] = event.get("Fase", "")
            info_to_store_details["iniciativa_evento_data"] = event.get("DataFase", "")
            info_to_store_details["iniciativa_evento_id"] = event.get("EvtId", "")
            info_to_store_details["iniciativa_evento_obsFase"] = event.get("ObsFase", "")

            publicacao_detalhe = to_list(
                event.get("PublicacaoFase", [])
            )
            info_to_store_details["iniciativa_publicacao_Tipo"] = [
                MyDict(x).get("pubTipo", "") for x in publicacao_detalhe
            ]
            info_to_store_details["iniciativa_publicacao_URL"] = [
                MyDict(x).get("URLDiario", "") for x in publicacao_detalhe
            ]
            info_to_store_details["iniciativa_publicacao_Obs"] = [
                MyDict(x).get("obs", "") for x in publicacao_detalhe
            ]
            info_to_store_details["iniciativa_publicacao_Pags"] = "|".join(
                [
                    "|".join(to_list(MyDict(x).get("pag", [])))
                    for x in publicacao_detalhe
                ]
            )

            iniciativas_conjuntas = to_list(
                event.get("IniciativasConjuntas", [])
            )
            info_to_store_details["iniciativa_iniciativas_conjuntas_tipo"] = "|".join(
                [MyDict(x).get("descTipo", "") for x in iniciativas_conjuntas if x]
            )
            info_to_store_details["iniciativa_iniciativas_conjuntas_titulo"] = "|".join(
                [MyDict(x).get("titulo", "") for x in iniciativas_conjuntas if x]
            )

            intervencoes = to_list(
                event.get("Intervencoesdebates", [])
            )
            info_to_store_details["iniciativa_oradores_deputados_nomes"] = "|".join(
                [
                    "|".join(
                        [
                            MyDict(orador).get("deputados", {}).get("nome", "")
                            for orador in to_list(
                                intervencao.get("oradores", [])
                            )
                        ]
                    )
                    for intervencao in intervencoes
                ]
            )
            info_to_store_details["iniciativa_oradores_deputados_gp"] = "|".join(
                [
                    "|".join(
                        [
                            MyDict(orador).get("deputados", {}).get("GP", "")
                            for orador in to_list(
                                intervencao.get("oradores", [])
                            )
                        ]
                    )
                    for intervencao in intervencoes
                ]
            )
            info_to_store_details["iniciativa_oradores_governo_nomes"] = "|".join(
                [
                    "|".join(
                        [
                            MyDict(orador).get("membrosGoverno", {}).get("nome", "")
                            for orador in to_list(
                                intervencao.get("oradores", [])
                            )
                        ]
                    )
                    for intervencao in intervencoes
                ]
            )
            info_to_store_details["iniciativa_oradores_governo_cargo"] = "|".join(
                [
                    "|".join(
                        [
                            MyDict(orador).get("membrosGoverno", {}).get("cargo", "")
                            for orador in to_list(
                                intervencao.get("oradores", [])
                            )
                        ]
                    )
                    for intervencao in intervencoes
                ]
            )
            # government and deputies videos are mixed
            info_to_store_details["iniciativa_oradores_videos"] = "|".join(
                [
                    "|".join(
                        [
                            "|".join(
                                [
                                    x.get("link", "")
                                    for x in to_list(
                                        MyDict(orador)
                                        .get("linkVideo", [])
                                    )
                                ]
                            )
                            for orador in to_list(
                                MyDict(intervencao)
                                .get("oradores", [])
                            )
                        ]
                    )
                    for intervencao in intervencoes
                ]
            )

            votacao = to_list(event.get("Votacao", []))
            # in some situations the same initiative in a certain event can have several votes
            # for now we will consider only the first one
            if len(votacao) > 0:
                votacao = votacao[0]
            votacao = MyDict(votacao)
            info_to_store_details["iniciativa_votacao_res"] = votacao.get(
                "resultado", ""
            )
            info_to_store_details["iniciativa_votacao_desc"] = votacao.get(
                "descricao", ""
            )
            info_to_store_details["iniciativa_votacao_tipo_reuniao"] = votacao.get(
                "tipoReuniao", ""
            )
            info_to_store_details["iniciativa_votacao_unanime"] = votacao.get(
                "unanime", ""
            )
            info_to_store_details["iniciativa_votacao_detalhe"] = votacao.get(
                "detalhe", ""
            )
            info_to_store_details["iniciativa_votacao_ausencias"] = to_list(
                votacao.get("ausencias", [])
            )

            anexos = to_list(
                event.get("AnexosFase", [])
            )
            info_to_store_details["iniciativa_anexo_nome"] = "|".join(
                [MyDict(x).get("anexoNome", "") for x in anexos if x]
            )
            info_to_store_details["iniciativa_anexo_url"] = "|".join(
                [MyDict(x).get("anexoFich", "") for x in anexos if x]
            )

            """
            comissao = to_list(event.get("Comissao", []))[0]
            info_to_store_details["iniciativa_comissao_nome"] = comissao.get("Nome", "")
            info_to_store_details["iniciativa_comissao_competente"] = comissao.get(
                "Competente", ""
            )
            info_to_store_details["iniciativa_comissao_observacao"] = comissao.get(
                "Observacao", ""
            )
            info_to_store_details["iniciativa_comissao_data_relatorio"] = comissao.get(
                "DataRelatorio", ""
            )
            info_to_store_details["iniciativa_comissao_pedidos_parecer"] = "|".join(
                [
                    _
                    for _ in to_list(
                        comissao.get("PedidosParecer", [])
                    )
                    if isinstance(_, str)
                ]
            )
            info_to_store_details["iniciativa_comissao_pareceres_recebidos"] = "|".join(
                [
                    _
                    for _ in to_list(
                        comissao.get("PareceresRecebidos", [])
                    )
                    if isinstance(_, str)
                ]
            )

            documentos = to_list(
                comissao.get("Documentos", [])
            )
            info_to_store_details["iniciativa_comissao_documentos_Titulos"] = "|".join(
                [MyDict(x).get("TituloDocumento", "") for x in documentos if x]
            )
            info_to_store_details["iniciativa_comissao_documentos_Tipos"] = "|".join(
                [MyDict(x).get("TipoDocumento", "") for x in documentos if x]
            )
            info_to_store_details["iniciativa_comissao_documentos_URLs"] = "|".join(
                [MyDict(x).get("URL", "") for x in documentos if x]
            )

            publicacaoDetalhe = to_list(
                comissao.get("PublicacaoFase", [])
            )
            info_to_store_details["iniciativa_comissao_publicacao_Tipo"] = [
                MyDict(x).get("pubTipo", "") for x in publicacaoDetalhe
            ]
            info_to_store_details["iniciativa_comissao_publicacao_URL"] = [
                MyDict(x).get("URLDiario", "") for x in publicacaoDetalhe
            ]
            info_to_store_details["iniciativa_comissao_publicacao_Obs"] = [
                MyDict(x).get("obs", "") for x in publicacaoDetalhe
            ]
            info_to_store_details["iniciativa_comissao_publicacao_Pags"] = "|".join(
                [
                    "|".join(to_list(MyDict(x).get("pag", [])))
                    for x in publicacaoDetalhe
                ]
            )

            votacao = comissao.get("Votacao", [])
            # in some situations that I need to understand we have several polls
            # for now will keep the first one
            if len(votacao) > 0:
                votacao = votacao[0]
            info_to_store_details["iniciativa_comissao_votacao_res"] = votacao.get(
                "resultado", ""
            )
            info_to_store_details["iniciativa_comissao_votacao_desc"] = votacao.get(
                "descricao", ""
            )
            info_to_store_details["iniciativa_comissao_votacao_data"] = votacao.get(
                "data", ""
            )
            info_to_store_details["iniciativa_comissao_votacao_unanime"] = votacao.get(
                "unanime", ""
            )
            """

            # TODO: in event: teor, sumario, publicacao
            # TODO: in comissao:  audicoes, audiencias, distribuicaoSubcomissao, motivoNaoParecer, pareceresRecebidos, pedidosParecer, relatores

            data_initiatives.append(info_to_store_details)

    data_initiatives = pd.DataFrame(data_initiatives)

    # enhance data with processed fields
    data_initiatives["iniciativa_autor"] = data_initiatives.apply(
        _get_author, axis="columns"
    )
    data_initiatives["iniciativa_autor_deputado"] = data_initiatives.apply(
        _get_author_deputy, axis="columns"
    )
    data_initiatives["iniciativa_evento_data"] = pd.to_datetime(
        data_initiatives["iniciativa_evento_data"]
    )

    return data_initiatives


# Improve: in some of the following situations maybe I could infer the vote
#          of some parties
# https://www.parlamento.pt/ActividadeParlamentar/Paginas/DetalheIniciativa.aspx?BID=44422
# https://www.parlamento.pt/ActividadeParlamentar/Paginas/DetalheIniciativa.aspx?BID=44343
# https://www.parlamento.pt/ActividadeParlamentar/Paginas/DetalheIniciativa.aspx?BID=120916
def _split_vote_result(vote: str) -> Dict[str, list]:
    """
    Extract vote result from poll

    Return a dicionary with a list of parties for each poll option
    """

    if not vote:
        return {}

    # clean vote information
    vote = (
        vote.lower()
        .replace(" ", "")
        .replace("<br>", "")
        .replace("</i>", "")
        .replace("<i>", "")
    )
    vote = (
        vote.replace("afavor:", ",afavor,")
        .replace("contra:", ",contra,")
        .replace("ausência:", ",ausência,")
        .replace("abstenção:", ",abstenção,")
    )
    vote = vote.replace("cristinarodrigues(ninsc)", "cr").replace(
        "joacinekatarmoreira(ninsc)", "jkm").replace(
        "antóniomalódeabreu(ninsc)", "ama"
    )
    vote = vote.split(",")

    result = defaultdict(list)

    # the first entry will always be empty
    current_option = vote[1]
    for party in vote[2:]:
        if party in "afavor,contra,ausência,abstenção":
            current_option = party
        else:
            if party in "ps,psd,be,pcp,cds-pp,pan,pev,ch,il,l,cr,jkm,ama".split(","):
                result[current_option].append(party)
            # sometimes deputies vote different from their own party
            else:
                result[f"outros_{current_option}"].append(party)

    return result


def get_initiatives_votes(initiatives: pd.DataFrame) -> pd.DataFrame:
    """
    Collect vote information from each initiative.
    """

    # we only need this initiative information regaring votes
    columns_to_keep = [
        "iniciativa_id",
        "iniciativa_nr",
        "iniciativa_tipo",
        "iniciativa_titulo",
        "iniciativa_evento_fase",
        "iniciativa_evento_data",
        "iniciativa_url",
        "iniciativa_obs",
        "iniciativa_texto_subst",
        "iniciativa_autor_grupos_parlamentares",
        "iniciativa_autor_outros_nome",
        "iniciativa_autor_outros_autor_comissao",
        "iniciativa_autor_deputados_nomes",
        "iniciativa_autor_deputados_GPs",
        "iniciativa_votacao_res",
        "iniciativa_votacao_desc",
        "iniciativa_autor",
        "iniciativa_votacao_unanime",
    ]

    data_initiatives = []
    for _, row in tqdm(
        initiatives.iterrows(),
        "getting_initiatives_votes",
        len(initiatives),
        file=sys.stdout,
    ):
        columns_to_store = row[columns_to_keep].copy()

        if row["iniciativa_votacao_res"]:
            # create a new column for each party with the respective vote
            vote_results = _split_vote_result(row["iniciativa_votacao_detalhe"])

            for vote, parties in vote_results.items():
                for party in parties:
                    if "outros" in vote:
                        k = f"iniciativa_votacao_{vote}"
                        if k in columns_to_store:
                            columns_to_store[k] = f"{columns_to_store[k]}|{party}"
                        else:
                            columns_to_store[k] = party
                    else:
                        columns_to_store[f"iniciativa_votacao_{party}"] = vote

            if row["iniciativa_evento_obsFase"]:
                if columns_to_store["iniciativa_votacao_desc"]:
                    columns_to_store["iniciativa_votacao_desc"] += f'| {row["iniciativa_evento_obsFase"]}'
                else:
                    columns_to_store["iniciativa_votacao_desc"] = row["iniciativa_evento_obsFase"]

            if row["iniciativa_votacao_unanime"] == "unanime":
                columns_to_store["iniciativa_votacao_contra_sua_iniciativa"] = False
            else:
                party = columns_to_store["iniciativa_autor"].lower()
                if f"iniciativa_votacao_{party}" in columns_to_store:
                    columns_to_store["iniciativa_votacao_contra_sua_iniciativa"] = (
                        columns_to_store[f"iniciativa_votacao_{party}"] == "contra"
                    )
                else:
                    columns_to_store["iniciativa_votacao_contra_sua_iniciativa"] = False

            data_initiatives.append(columns_to_store)

    df_initiatives = pd.DataFrame(data_initiatives)

    # enhance data with processed fields
    df_initiatives["iniciativa_aprovada"] = (
        df_initiatives["iniciativa_votacao_res"] == "Aprovado"
    )

    return df_initiatives
