import datetime
import json
import logging
import os
import sys

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from azure.cosmos import (ContainerProxy, CosmosClient, DatabaseProxy,
                          PartitionKey)
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.storage.blob import ContainerClient as BlobContainerClient
from tqdm import tqdm

from daily_updater.parliament.initiatives.extract import ONGOING_PATHS as PATHS
from daily_updater.parliament.initiatives.extract import (
    get_initiatives, get_initiatives_votes, get_raw_data_from_blob)
from daily_updater.parliament.initiatives.votes import (get_party_approvals,
                                                        get_party_correlations)
from daily_updater.parliament.legislatures.extract import \
    ON_GOING_PATHS as LegislaturePaths
from daily_updater.parliament.legislatures.extract import \
    get_legislatures_fields
from src.app.apis.schemas import EventPhase

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

sched = BlockingScheduler()


def get_or_create_database() -> DatabaseProxy:
    """
    Connects to Azure Cosmos DB and return its client. Expects to load from
    env vars all needed information, otherwise will fail.
    """

    try:
        database_name = os.environ["DATABASE_NAME"]
        url = os.environ["ACCOUNT_URI"]
        key = os.environ["ACCOUNT_KEY"]
    except Exception:
        logger.exception("Error collection env vars to access database:")
        raise

    try:
        client = CosmosClient(url, key)
        logger.debug("Connect to Cosmos successfully.")
        database = client.create_database_if_not_exists(id=database_name)
        logger.info("Connect to Database successfully.")
    except Exception:
        logger.exception("Unknow error connectiong to database:")
        raise

    return database


def recreate_all_cosmos_containers(database: DatabaseProxy) -> None:
    """
    Recreate all containers in Cosmos DB.
    """

    containers = "initiatives initiatives_votes".split()
    containers_partition_keys = "iniciativa_autor iniciativa_autor".split()

    for container, key in zip(containers, containers_partition_keys):
        logger.info(f"Creating container: {container}.")

        try:
            database.delete_container(container)
        except CosmosResourceNotFoundError:
            # All good, trying to delete a container that does not exit
            pass
        except:
            logger.info(f"Failed to delete container {container}.")
            raise

        logger.debug(f"Container {container} deleted successfully.")

        try:
            database.create_container(
                id=container, partition_key=PartitionKey(path=f"/{key}")
            )
        except:
            logger.info(f"Failed to create container {container}.")
            raise


def get_cosmos_container(database: CosmosClient, container_name: str) -> ContainerProxy:
    """
    Connects to a certain Azure Cosmos DB container and return its clients.
    """

    try:
        container = database.get_container_client(container_name)
    except Exception:
        logger.exception(f"Error connecting to container {container_name}:")
        raise

    return container


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

    # r = requests.get('https://portuguese-politics.fly.dev/update')
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


@sched.scheduled_job("cron", hour="3", minute="00")
def main() -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    logger.info("Portuguese Politics daily updater ran at %s", utc_timestamp)

    # Get Blob Storage client
    blob_storage_container_client = get_blob_container()

    run_legislatures(blob_storage_container_client=blob_storage_container_client)
    # Get Cosmos DB client
    database = get_or_create_database()

    # The idea is to update daily the information from parliament data, thus
    # I need to delete old data and populate with new data.
    # In Cosmos DB the fastest way to do it is to recreate the containers
    ##recreate_all_cosmos_containers(database)

    # Go through each supported legislature and populate the database
    for legislature_name, _ in tqdm(PATHS, "processing_legislatures", file=sys.stdout):
        # load raw data (json format) from Blob Sotrage (cache from parlamento API)
        raw_initiatives = get_raw_data_from_blob(
            blob_storage_container_client, legislature_name
        )
        # collect all initiatives, still very raw info
        df_initiatives = get_initiatives(raw_initiatives)

        # fix an error
        df_initiatives.loc[
            (df_initiatives["iniciativa_id"] == "151936")
            & (df_initiatives["iniciativa_votacao_res"] == "Rejeitado"),
            "iniciativa_votacao_res",
        ] = "Aprovado"

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

        # get containers' clients
        initiatives_container = get_cosmos_container(database, "initiatives")
        initiatives_votes_container = get_cosmos_container(
            database, "initiatives_votes"
        )

        for container, initiatives, name in [
            (initiatives_container, df_initiatives, "initiatives"),
            (initiatives_votes_container, df_initiatives_votes, "initiatives_votes"),
        ]:
            logger.info(f"Processing {name}..")

            # it seems bulk insert are not supported in Python SDK
            # https://docs.microsoft.com/en-us/python/api/overview/azure/cosmos-readme?view=azure-python#limitations
            # therefore we will insert one by one, which is not an issue since
            # this code runs once per day and there are "only" around 30k pairs
            # of (initiatives, stage) by the end of each legislature (~4 years)

            # https://towardsdatascience.com/heres-the-most-efficient-way-to-iterate-through-your-pandas-dataframe-4dad88ac92ee
            #
            # each row is a certain stage of an initiative.
            # for the votes we filtered by stages that had a vote moment

            # convert to epoch time to avoid serializable issues
            for col in initiatives.select_dtypes(include="datetime").columns:
                initiatives[col] = initiatives[col].apply(lambda x: x.value)

            # convert all nan to "", besides date and "iniciativa_aprovada" that
            # do not have nan all remaining columns are strings
            initiatives.fillna("", inplace=True)
            """
            for initiative in tqdm(initiatives.to_dict("records"), f"populating_{name}", file=sys.stdout):
                container.upsert_item({
                    "legislature_name": legislature_name,
                    "id": str(uuid.uuid4()),
                    **initiative
                })
            """
        # Azure Cosmos DB free tier only support 2 containers, thus
        # we will store the remaining info in Azure Blob Storage
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

    update_app()

    logger.info("Done.")


if __name__ == "__main__":
    main()

# sched.start()
