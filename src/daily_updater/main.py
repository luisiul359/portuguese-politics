import datetime
import logging
import os
import sys 

from apscheduler.schedulers.blocking import BlockingScheduler

from azure.cosmos import (
    CosmosClient,
    PartitionKey,
    DatabaseProxy,
    ContainerProxy
)
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import ContainerClient as BlobContainerClient
from tqdm import tqdm

from src.daily_updater.parliament.extract import (
    PATH_XIV,
    ALL_PATHS,
    get_raw_data_from_blob,
    get_initiatives,
    get_initiatives_votes
)

from src.daily_updater.parliament.votes import (
    get_party_approvals,
    get_party_correlations
)


logger = logging.getLogger(__name__)
#handler = logging.StreamHandler(sys.stdout)
#logger.addHandler(handler)

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
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
    except Exception:
        logger.exception(f"Error connecting to blob storage container {container_name}:")
        raise
        
    return container_client


@sched.scheduled_job("cron", hour="16", minute="38")
def main() -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logger.info("Portuguese Politics daily updater ran at %s", utc_timestamp)

    # Get Blob Storage client
    blob_storage_container_client = get_blob_container()

    # Get Cosmos DB client
    database = get_or_create_database()

    # The idea is to update daily the information from parliament data, thus
    # I need to delete old data and populate with new data.
    # In Cosmos DB the fastest way to do it is to recreate the containers
    
    #recreate_all_cosmos_containers(database)

    # Go through each supported legislature and populate the database
    for legislature_name, _ in tqdm([("XIV", PATH_XIV)], "processing_legislatures", file=sys.stdout): 
    #for legislature_name, _ in tqdm(ALL_PATHS, "processing_legislatures", file=sys.stdout):

        # load raw data (still json) from parlamento API
        raw_initiatives = get_raw_data_from_blob(blob_storage_container_client, legislature_name)
        # collect all initiatives, still very raw info
        #df_initiatives = get_initiatives(raw_initiatives)
        import pandas as pd
        df_initiatives = pd.read_pickle("df_initiatives.pkl")
        # free up memory
        del raw_initiatives
        # collect vote information from all initiatives
        df_initiatives_votes = get_initiatives_votes(df_initiatives)

        # get containers' clients
        initiatives_container = get_cosmos_container(database, "initiatives")
        initiatives_votes_container = get_cosmos_container(database, "initiatives_votes")

        for container, initiatives, name in [
            (initiatives_container, df_initiatives,  "initiatives"), 
            (initiatives_votes_container, df_initiatives_votes, "initiatives_votes")
            ]:

            logger.info(f"Processing {name}..")


            c = {'iniciativa_anexo_nome': '', 'iniciativa_anexo_url': '', 
            'iniciativa_anexos_URLs': '', 'iniciativa_anexos_nomes': '', 
            'iniciativa_autor_deputados_GPs': 'PCP|PCP|PCP|PCP|PCP|PCP|PCP|PCP|PCP|PCP', 
            'iniciativa_autor_deputados_nomes': 'JOÃO DIAS|PAULA SANTOS|ANTÓNIO FILIPE|DIANA FERREIRA|BRUNO DIAS|DUARTE ALVES|VERA PRATA|JERÓNIMO DE SOUSA|ANA MESQUITA|ALMA RIVERA', 
            'iniciativa_autor_grupos_parlamentares': 'PCP', 'iniciativa_autor_outros_autor_comissao': '',
             'iniciativa_autor_outros_nome': 'Grupos Parlamentares', 'iniciativa_comissao_competente': '', 
             'iniciativa_comissao_data_relatorio': '', 'iniciativa_comissao_documentos_Tipos': '', 
             'iniciativa_comissao_documentos_Titulos': '', 'iniciativa_comissao_documentos_URLs': '', 
             'iniciativa_comissao_nome': '', 'iniciativa_comissao_observacao': '', 
             'iniciativa_comissao_pareceres_recebidos': '', 'iniciativa_comissao_pedidos_parecer': '', 
             'iniciativa_comissao_publicacao_Obs': '', 'iniciativa_comissao_publicacao_Pags': '', 
             'iniciativa_comissao_publicacao_Tipo': '', 'iniciativa_comissao_publicacao_URL': '', 
             'iniciativa_comissao_votacao_Data': '', 'iniciativa_comissao_votacao_Desc': '', 
             'iniciativa_comissao_votacao_Res': '', 'iniciativa_comissao_votacao_Unanime': '', 
             'iniciativa_evento_data': 1595894400000000000, 'iniciativa_evento_fase': 'Entrada', 
             'iniciativa_evento_id': '1', 'iniciativa_id': '45156', 'iniciativa_iniciativas_conjuntas_tipo': '',
             'iniciativa_iniciativas_conjuntas_titulo': '', 'iniciativa_nr': '28', 'iniciativa_obs': '', 
             'iniciativa_oradores_deputados_gp': '', 'iniciativa_oradores_deputados_nomes': '', 
             'iniciativa_oradores_governo_cargo': '', 'iniciativa_oradores_governo_nomes': '', 
             'iniciativa_oradores_videos': '', 'iniciativa_origem_assunto': '', 'iniciativa_origem_desc': '', 
             'iniciativa_origem_id': '', 'iniciativa_origem_nr': '', 'iniciativa_publicacao_Obs': '', 
             'iniciativa_publicacao_Pags': '', 'iniciativa_publicacao_Tipo': '', 'iniciativa_publicacao_URL': '', 
             'iniciativa_texto_subst': '', 'iniciativa_tipo': 'Apreciação Parlamentar', 
             'iniciativa_titulo': 'Decreto-Lei n.º 29/2020, de 29 de junho, que "Cria um programa de apoio ao emparcelamento rural simples, designado «Emparcelar para Ordenar»"', 
             'iniciativa_url': 'http://app.parlamento.pt/webutils/docs/doc.pdf?path=6148523063484d364c793968636d356c6443397a6158526c6379395953565a4d5a5763765247396a6457316c626e527663306c7561574e7059585270646d45764f445134595467794d6d59744f444d33596930304e6d55314c5467784e4755744e6a4a6c5954453459545a6c5a6a6b304c6d527659773d3d&fich=848a822f-837b-46e5-814e-62ea18a6ef94.doc&Inline=true', 
             'iniciativa_votacao_ausencias': '', 'iniciativa_votacao_desc': '', 'iniciativa_votacao_detalhe': '', 
             'iniciativa_votacao_res': '', 'iniciativa_votacao_tipo_reuniao': '', 'iniciativa_votacao_unanime': '', 
             'iniciativa_autor': 'PCP', 'iniciativa_autor_deputado': 'JOÃO DIAS|PAULA SANTOS|ANTÓNIO FILIPE|DIANA FERREIRA|BRUNO DIAS|DUARTE ALVES|VERA PRATA|JERÓNIMO DE SOUSA|ANA MESQUITA|ALMA RIVERA'
             }
            container.upsert_item({
                "legislature_name": legislature_name,
                **c
            })


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

            for initiative in tqdm(initiatives.head(1000).to_dict("records"), f"populating_{name}", file=sys.stdout):
                logger.info(initiative)
                container.upsert_item({
                    "legislature_name": legislature_name,
                    **initiative
                })

        # Azure Cosmos DB free tier only support 2 containers, thus
        # we will store the remaining info in Azure Blob Storage
        party_approvals = get_party_approvals(df_initiatives_votes).to_json(orient="index")
        party_correlations = get_party_correlations(df_initiatives_votes).to_json(orient="index")

        # party_approvals
        blob_client: BlobClient = blob_storage_container_client.get_blob_client(f"{legislature_name}_party_approvals.json")
        blob_client.upload_blob(party_approvals, overwrite=True)

        # party_correlations
        blob_client: BlobClient = blob_storage_container_client.get_blob_client(f"{legislature_name}_party_correlations.json")
        blob_client.upload_blob(party_correlations, overwrite=True)
        
    logger.info("Done.")


sched.start()