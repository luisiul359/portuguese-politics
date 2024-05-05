import json
import logging
import os
import sys
from datetime import date
from typing import Dict, Optional
import pandas as pd
import uvicorn as uvicorn
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient as BlobContainerClient
# from dotenv import load_dotenv
from fastapi import FastAPI
from src.app.apis import schemas
from src.elections.extract import extract_legislativas_2019
from src.parliament.initiatives import votes
from src.parliament.deputies.router import router as deputies_router
from src.parliament.routers.agenda import agenda_router
from src.app.config import config

# load_dotenv(dotenv_path=".env")

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


#########################
##### Load clients  #####
#########################


def get_blob_container() -> BlobContainerClient:
    """
    Connects to Azure Blob Storage and return its client. Expects to load from
    env vars all needed information, otherwise will fail.
    """

    try:
        connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = os.environ["AZURE_STORAGE_CONTAINER"]
    except Exception:
        logger.exception("Error collection env vars to access blob storage:")
        raise

    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.get_container_client(container_name)
    except Exception:
        logger.exception(
            f"Error connecting to blob storage container {container_name}:"
        )
        raise

    return container_client


# Get Blob Storage client
blob_storage_container_client = get_blob_container()


####################################
##### Load things into memory  #####
####################################


# ALL_LEGISLATURES = ["XIV", "XV"]


def load_party_approvals(
    legislature: str, phase: str, container_client: BlobContainerClient
) -> pd.DataFrame:
    """
    Load party approvals for a full legislature from Blob Storage
    """

    data = container_client.get_blob_client(
        f"{legislature}_party_approvals_{phase}.json"
    )
    return pd.DataFrame.from_dict(
        json.loads(data.download_blob().readall()), orient="index"
    )


def load_party_correlations(
    legislature: str, phase: str, container_client: BlobContainerClient
) -> pd.DataFrame:
    """
    Load party correlations for a full legislature from Blob Storage
    """

    data = container_client.get_blob_client(
        f"{legislature}_party_correlations_{phase}.json"
    )
    return pd.DataFrame.from_dict(
        json.loads(data.download_blob().readall()), orient="index"
    )


def load_initiative_votes(
    legislature: str, container_client: BlobContainerClient
) -> pd.DataFrame:
    """
    Load initiative votes of a certain legislature from Blob Storage
    """

    data = container_client.get_blob_client(f"{legislature}_initiatives_votes.json")
    df = pd.DataFrame.from_dict(
        json.loads(data.download_blob().readall()), orient="index"
    )

    df["iniciativa_evento_data"] = pd.to_datetime(
        df["iniciativa_evento_data"], unit="ms"
    )
    return df


def load_legislatures_fields(
    legislature: str, container_client: BlobContainerClient
) -> Dict:
    """
    Load initiative votes of a certain legislature from Blob Storage
    """
    print("PRE-DOWNLOAD")
    data = container_client.get_blob_client(f"{legislature}_legislatures.json")
    print(">>>>>>>", data)
    return json.loads(data.download_blob().readall())


party_approvals = None
party_correlations = None
initiative_votes = None
parties_legislatives_2019 = None
candidates_legislatives_2019 = None
legislature_fields = None


def load_data():
    """
    Load all data into memory
    """

    # no thread safe, to be fixed when the api usage justify
    global party_approvals
    global party_correlations
    global initiative_votes
    global parties_legislatives_2019
    global candidates_legislatives_2019
    global legislature_fields

    # parliament data
    party_approvals = {
        legislature: {
            phase.value: load_party_approvals(
                legislature, phase.name.lower(), blob_storage_container_client
            )
            for phase in schemas.EventPhase
        }
        for legislature in ALL_LEGISLATURES
    }

    party_correlations = {
        legislature: {
            phase.value: load_party_correlations(
                legislature, phase.name.lower(), blob_storage_container_client
            )
            for phase in schemas.EventPhase
        }
        for legislature in ALL_LEGISLATURES
    }

    initiative_votes = {
        legislature: load_initiative_votes(legislature, blob_storage_container_client)
        for legislature in ALL_LEGISLATURES
    }

    legislature_fields = {
        legislature: load_legislatures_fields(
            legislature=legislature, container_client=blob_storage_container_client
        )
        for legislature in ALL_LEGISLATURES
    }

    # legislative data
    (
        parties_legislatives_2019,
        candidates_legislatives_2019,
    ) = extract_legislativas_2019()


######################
##### Endpoints  #####
######################


# Create FastAPI client
tags_metadata = [
    {
        "name": "Parlamento",
        "description": "Informação relativa à Assembleia da República e trabalhos no Parlamento Português.",
    },
    {
        "name": "Elections",
        "description": "Information from Portuguese previous elections.",
    },
]

    app = FastAPI(openapi_tags=tags_metadata)

    parliament_app = FastAPI() #tag parlamento
    parliament_app.include_router(deputies_router, prefix="/parlamento")
    parliament_app.include_router(agenda_router, prefix="/parlamento")

    app.mount("/v2", parliament_app)

    return app

app = create_app()


@app.on_event("startup")
async def startup_event():
    if (config.env == "procution"):
        # The idea is to load all cached data during the app boostrap.
        # In some endpoints due the parameters it is not possible to just
        # filter the cached data and therefore some computation is done,
        # meaning slower responses.
        load_data()


@app.get("/parliament/party-approvals", tags=["Parlamento"])
def get_party_approvals(
    legislature: schemas.Legislature = schemas.Legislature.XV,
    event_phase: schemas.EventPhase = schemas.EventPhase.GENERALIDADE,
    type: Optional[str] = None,
    dt_ini: Optional[date] = None,
    dt_fin: Optional[date] = None,
) -> schemas.PartyApprovalsOut:
    """
    Get the % that each party approves initiatives from other parties.
    """

    if dt_ini or dt_fin or type:
        data_initiatives_votes_ = initiative_votes[legislature.value]

        if event_phase != schemas.EventPhase.ALL:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_evento_fase"] == event_phase
            ]

        if dt_ini:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_evento_data"].dt.date >= dt_ini
            ]

        if dt_fin:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_evento_data"].dt.date <= dt_fin
            ]

        if type:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_tipo"] == type
            ]

        _party_approvals = votes.get_party_approvals(data_initiatives_votes_).to_json(
            orient="index"
        )
    else:
        _party_approvals = party_approvals[legislature.value][
            event_phase.value
        ].to_json(orient="index")

    # transform to the expected schema
    approvals = []
    for autor, value in json.loads(_party_approvals).items():
        data = {
            "id": autor.lower()
            .replace(" ", "-")
            .replace("cristina-rodrigues", "cr")
            .replace("joacine-katar-moreira", "jkm")
            .replace("antónio-maló-de-abreu", "ama"),
            "nome": autor,
            "total_iniciativas": value["total_iniciativas"],
            "total_iniciativas_aprovadas": value["total_iniciativas_aprovadas"],
        }

        data["aprovacoes"] = {
            k.replace("iniciativa_votacao_", ""): v
            for k, v in value.items()
            if k.startswith("iniciativa_votacao_")
        }

        approvals.append(data)

    return {"autores": approvals}


@app.get("/parliament/party-correlations", tags=["Parlamento"])
def get_party_correlations(
    legislature: schemas.Legislature = schemas.Legislature.XV,
    event_phase: schemas.EventPhase = schemas.EventPhase.GENERALIDADE,
    type: Optional[str] = None,
    dt_ini: Optional[date] = None,
    dt_fin: Optional[date] = None,
) -> schemas.PartyCorrelationsOut:
    """
    Get the percentage of times that 2 parties vote the same.
    """

    if dt_ini or dt_fin or type:
        data_initiatives_votes_ = initiative_votes[legislature.value]

        if event_phase != schemas.EventPhase.ALL:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_evento_fase"] == event_phase
            ]

        if dt_ini:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_evento_data"].dt.date >= dt_ini
            ]

        if dt_fin:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_evento_data"].dt.date <= dt_fin
            ]

        if type:
            data_initiatives_votes_ = data_initiatives_votes_[
                data_initiatives_votes_["iniciativa_tipo"] == type
            ]

        _party_corr = votes.get_party_correlations(data_initiatives_votes_).to_json(
            orient="index"
        )
    else:
        _party_corr = party_correlations[legislature.value][event_phase.value].to_json(
            orient="index"
        )

    # transform to the expected schema
    res = []
    for _, corr in json.loads(_party_corr).items():
        res.append(
            {
                "nome": corr.pop("nome").replace("iniciativa_votacao_", ""),
                "correlacoes": {
                    k.replace("iniciativa_votacao_", ""): v for k, v in corr.items()
                },
            }
        )

    return {"partido": res}


@app.get("/parliament/initiatives", tags=["Parlamento"])
def get_initiatives(
    legislature: schemas.Legislature = schemas.Legislature.XV,
    event_phase: schemas.EventPhase = schemas.EventPhase.GENERALIDADE,
    name_filter: Optional[str] = None,
    party: Optional[str] = None,
    deputy: Optional[str] = None,
    dt_ini: Optional[date] = None,
    dt_fin: Optional[date] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0,
):  # -> schemas.InitiativesOut:  ## TODO: each legislature has different parties, we may need to update the schema
    """
    Get information regarting initiatives prresented in the Assembly of the
    Portuguese Republic.
    """

    data_initiatives_votes_ = initiative_votes[legislature.value]

    if event_phase != schemas.EventPhase.ALL:
        data_initiatives_votes_ = data_initiatives_votes_[
            data_initiatives_votes_["iniciativa_evento_fase"] == event_phase
        ]

    if dt_ini:
        data_initiatives_votes_ = data_initiatives_votes_[
            data_initiatives_votes_["iniciativa_evento_data"].dt.date >= dt_ini
        ]

    if dt_fin:
        data_initiatives_votes_ = data_initiatives_votes_[
            data_initiatives_votes_["iniciativa_evento_data"].dt.date <= dt_fin
        ]

    if name_filter:
        data_initiatives_votes_ = data_initiatives_votes_[
            data_initiatives_votes_["iniciativa_titulo"]
            .str.lower()
            .str.contains(name_filter.lower())
        ]

    if party:
        data_initiatives_votes_ = data_initiatives_votes_[
            data_initiatives_votes_["iniciativa_autor"].str.lower() == party.lower()
        ]

    if deputy:
        data_initiatives_votes_ = data_initiatives_votes_[
            data_initiatives_votes_["iniciativa_autor_deputado"]
            .str.lower()
            .str.contains(deputy.lower())
        ]

    initiatives = (
        votes.get_initiatives(data_initiatives_votes_)
        .sort_values("iniciativa_data")
        .head(limit + offset)
        .tail(limit)
        .to_json(orient="index")
    )

    # transform to the expected schema
    res = []
    for _, initiative in json.loads(initiatives).items():
        res.append(initiative)

    return {"initiativas": res}


@app.get("/parliament/legislatures", tags=["Parlamento"])
def get_legislatures(
    legislature: schemas.Legislature = schemas.Legislature.XV,
):
    """
    Get information regarding a particular legislature
    """
    return legislature_fields[legislature.value]


@app.get("/elections/parties", tags=["Eleições"])
def get_elections_parties(
    type: Optional[str] = "Legislativas", year: Optional[int] = 2019
):  # -> schemas.PartiesOut: ## TODO: it is not working
    """
    Get all the parties that participated in a certain election.
    """

    # ignoring input parameters until we have other elections

    return {"parties": json.loads(parties_legislatives_2019.to_json(orient="index"))}


@app.get("/elections/candidates", tags=["Eleições"])
def get_party_candidates(
    party: Optional[str],
    type: Optional[str] = "Legislativas",
    year: Optional[int] = 2019,
) -> schemas.CandidatesOut:
    """
    Get all the candidates from party in a certain election.
    """

    # ignoring some input parameters until we have other elections

    candidates_legislatives_2019_ = candidates_legislatives_2019[
        candidates_legislatives_2019["party"] == party
    ]

    return {
        "candidates": json.loads(
            candidates_legislatives_2019_.to_json(orient="records")
        )
    }


@app.get("/elections/candidates-district", tags=["Eleições"])
def get_district_candidates(
    district: str,
    type: Optional[str] = "Legislativas",
    year: Optional[int] = 2019,
    party: Optional[str] = None,
) -> schemas.CandidatesOut:
    """
    Get all the candidates from party in the constituency of district.
    """

    # ignoring some input parameters until we have other elections

    candidates_legislatives_2019_ = candidates_legislatives_2019

    if party:
        candidates_legislatives_2019_ = candidates_legislatives_2019_[
            candidates_legislatives_2019_["party"] == party
        ]

    candidates_legislatives_2019_ = candidates_legislatives_2019_[
        candidates_legislatives_2019_["district"] == district
    ]

    return {
        "candidates": json.loads(
            candidates_legislatives_2019_.to_json(orient="records")
        )
    }


@app.get("/update")
def update():
    """
    Forces to reload the parliament data from our datalake.

    This is called by our daily updater.
    """
    logger.info("Loading new data..")
    load_data()
    logger.info("New data loaded.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
