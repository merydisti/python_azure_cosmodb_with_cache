import logging

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

logger = logging.getLogger(__name__)

# Add configuration to connect to a real DB
HOST = ""
MASTERKEY = ""
DATABASEID = ""


class CosmosClient:
    def connect(self, container):
        try:
            self._set_client()
            self._get_database(DATABASEID)
            self._find_container(container)
        except Exception as e:
            logger.exception(f"Failed to get connection to the Db. Message={e}")

    def _set_client(self):
        try:
            self.client = cosmos_client.CosmosClient(
                HOST,
                {"masterKey": MASTERKEY},
            )
        except Exception as e:
            logger.exception(f"Failed to set the client to the Db. Message={e}")

    def _get_database(self, id):
        try:
            database = self.client.get_database_client(id)
            database.read()
            self.db = database

        except exceptions.CosmosResourceNotFoundError as e:
            logger.error(f"A database with id '{id}' does not exist. Message={e}")

    def _find_container(self, id):
        try:
            container = self.db.get_container_client(id)
            container.read()
            self.container = container
        except exceptions.CosmosResourceNotFoundError as e:
            logger.error(f"A container with id '{id}' does not exist.  Message={e}")

    def get_items(self, query, parameters):
        result = list(
            self.container.query_items(
                query={
                    "query": query,
                    "parameters": parameters,
                },
                max_integrated_cache_staleness_in_ms=1800000,
                enable_cross_partition_query=True,
                populate_query_metrics=True,
            )
        )

        return result
