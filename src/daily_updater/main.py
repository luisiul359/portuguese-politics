import datetime
import json
import logging
import os
import sys

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.storage.blob import ContainerClient as BlobContainerClient
from tqdm import tqdm

from src.app.apis.schemas import EventPhase
from src.parliament.initiatives.extract import ONGOING_PATHS as PATHS
from src.parliament.initiatives.extract import (get_initiatives,
                                                get_initiatives_votes,
                                                get_raw_data_from_blob)
from src.parliament.initiatives.votes import (get_party_approvals,
                                              get_party_correlations)
from src.parliament.legislatures.extract import \
    ONGOING_PATHS as LegislaturePaths
from src.parliament.legislatures.extract import get_legislatures_fields

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

sched = BlockingScheduler()


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


def update_app():
    """
    Send a request to Portuguese Politics app to refresh data
    """

    r = requests.get("https://portuguese-politics.herokuapp.com/update")
    if r.status_code != 200:
        logger.error(r.status_code)
        logger.error(r.content)
    else:
        return {"Ok"}


def run_legislatures(blob_storage_container_client: BlobContainerClient):
    for legislature_name, path in tqdm(
        LegislaturePaths, "processing_legislatures", file=sys.stdout
    ):
        blob_client: BlobClient = blob_storage_container_client.get_blob_client(
            f"{legislature_name}_legislatures.json"
        )
        legislature_fields = get_legislatures_fields(path=path)
        blob_client.upload_blob(json.dumps(legislature_fields), overwrite=True)


def run_initiatives(blob_storage_container_client: BlobContainerClient):
    # Go through each supported legislature and store the statistics
    # and raw data
    for legislature_name, _ in tqdm(PATHS, "processing_legislatures", file=sys.stdout):
        # load raw data (json format) from Blob Sotrage (cache from parlamento API)
        raw_initiatives = get_raw_data_from_blob(
            blob_storage_container_client, legislature_name
        )

        # collect all initiatives, still very raw info
        df_initiatives = get_initiatives(raw_initiatives)

        # free up memory
        del raw_initiatives

        # collect vote information from all initiatives
        df_initiatives_votes = get_initiatives_votes(df_initiatives)

        # we do not need those initiatives, they were dropped
        df_initiatives_votes = df_initiatives_votes[
            df_initiatives_votes["iniciativa_votacao_res"] != "Retirado"
        ]

        # store initiative votes in Blob Storage, already processed
        initiatives_votes = df_initiatives_votes.to_json(orient="index")
        blob_client: BlobClient = blob_storage_container_client.get_blob_client(
            f"{legislature_name}_initiatives_votes.json"
        )
        blob_client.upload_blob(initiatives_votes, overwrite=True)

        # Break the results per initiative phase and
        # store the info in Azure Blob Storage
        for phase in EventPhase:
            if phase != EventPhase.ALL:
                df_initiatives_votes_ = df_initiatives_votes[
                    df_initiatives_votes["iniciativa_evento_fase"] == phase
                ]
            else:
                df_initiatives_votes_ = df_initiatives_votes

            party_approvals = get_party_approvals(df_initiatives_votes_).to_json(
                orient="index"
            )
            party_correlations = get_party_correlations(df_initiatives_votes_).to_json(
                orient="index"
            )

            # party_approvals
            blob_client: BlobClient = blob_storage_container_client.get_blob_client(
                f"{legislature_name}_party_approvals_{phase.name.lower()}.json"
            )
            blob_client.upload_blob(party_approvals, overwrite=True)

            # party_correlations
            blob_client: BlobClient = blob_storage_container_client.get_blob_client(
                f"{legislature_name}_party_correlations_{phase.name.lower()}.json"
            )
            blob_client.upload_blob(party_correlations, overwrite=True)


@sched.scheduled_job("cron", hour="23", minute="55")
def main() -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    logger.info("Portuguese Politics daily updater ran at %s", utc_timestamp)

    # Get Blob Storage client
    blob_storage_container_client = get_blob_container()

    # get all initiatives data
    run_initiatives(blob_storage_container_client)

    # get all legislatures data
    run_legislatures(blob_storage_container_client)

    # force API to reload the new data
    update_app()

    logger.info("Done.")


#if __name__ == "__main__":
#   main()

sched.start()
