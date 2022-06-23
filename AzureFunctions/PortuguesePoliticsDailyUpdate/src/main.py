import datetime
import logging
import os
import sys 
import requests
import json

import azure.functions as func

from typing import Dict, List
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import ContainerClient as BlobContainerClient
from tqdm import tqdm


logger = logging.getLogger(__name__)


# XIV Legislatura
PATH_XIV = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d6c6a6157463061585a68637939595356596c4d6a424d5a57647063327868644856795953394a626d6c6a6157463061585a686331684a566c3971633239754c6e523464413d3d&fich=IniciativasXIV_json.txt&Inline=true"
# XIV Legislatura
PATH_XV = "https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d6c6a6157463061585a6863793959566955794d45786c5a326c7a6247463064584a684c306c7561574e7059585270646d467a57465a66616e4e76626935306548513d&fich=IniciativasXV_json.txt&Inline=true"

ALL_PATHS = [
  ("XIV", PATH_XIV), 
  ("XV", PATH_XV)
]


def get_raw_data(path: str) -> List[Dict]:
    """ Load the most recent data provided by Parlamento """
    
    try:
      payload = requests.get(
        path,
        # fake, but wihtout it the request is rejected
        headers={
            'User-Agent': 'Mozilla/5.0',
        },
        timeout=40
      )
      assert payload.status_code == 200

      logger.info(payload.request.url)
      logger.info(payload.request.body)
      logger.info(payload.request.headers)

      return payload.json()
    except Exception:
      logger.exception(f"Error downloading {path}.")
      raise


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
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
    except Exception:
        logger.exception(f"Error connecting to blob storage container {container_name}:")
        raise
        
    return container_client


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logger.info("The timer is past due!")

    logger.info("Portuguese Politics daily updater function ran at %s", utc_timestamp)

    # Get Blob Storage client
    blob_storage_container_client = get_blob_container()

    # Go through each supported legislature and download it
    for legislature_name, legislature_path in tqdm(ALL_PATHS, "processing_legislatures", file=sys.stdout):
        logger.info(f"Start processing {legislature_name}")
    
        data = get_raw_data(legislature_path)
        
        try:
            blob_client: BlobClient = blob_storage_container_client.get_blob_client(f"{legislature_name}.json")
            blob_client.upload_blob(json.dumps(data), overwrite=True)
        except Exception:
            logger.exception(f"Error processing {legislature_name}.")
            raise
        
    logger.info("Done.")
  