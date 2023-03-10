import logging
from datetime import datetime, timedelta

from classes.singleton_meta import SingletonMeta
from classes.cosmos_client import CosmosClient

logger = logging.getLogger(__name__)

TTL = "1140"

class Cache(metaclass=SingletonMeta):
    data = {}

    def _set_expiration(self):
        return datetime.today() + timedelta(seconds=int(TTL))

    def _set_data(self, container, name, query, parameters):
        try:
            cosmosdb = CosmosClient()
            cosmosdb.connect(container)
            info = cosmosdb.get_items(
                query,
                parameters,
            )

            if info:
                self.data[name] = {"data": info, "expiration": self._set_expiration()}

            return info
        except Exception as e:
            logger.exception(f"Failed to connect/read from DB. Message={e}")

    def get_data(self, container, name, query, parameters):
        if name in self.data and not self._is_expirated(self.data[name]["expiration"]):
            return self.data[name]["data"]

        return self._set_data(container, name, query, parameters)

    def _is_expirated(self, date):
        return datetime.now() > date
