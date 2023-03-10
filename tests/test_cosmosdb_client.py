import logging
from unittest.mock import MagicMock, create_autospec, patch

import pytest
from azure.cosmos.container import ContainerProxy
from azure.cosmos.cosmos_client import CosmosClient as AzureCosmosClient
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from classes.cosmos_client import CosmosClient, logger

def test_connect_sucess():
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    method_call_list = []

    def register_call(method_name):
        return lambda *args, **kwargs: method_call_list.append(method_name)

    with (
        patch(
            "classes.cosmos_client.CosmosClient",
            cosmos_client_mock,
        ),
        patch.object(
            CosmosClient,
            "_set_client",
            autospec=True,
            side_effect=register_call("_set_client"),
        ),
        patch.object(
            CosmosClient,
            "_get_database",
            autospec=True,
            side_effect=register_call("_get_database"),
        ),
        patch.object(
            CosmosClient,
            "_find_container",
            autospec=True,
            side_effect=register_call("_find_container"),
        ),
    ):
        cosmos = CosmosClient()
        cosmos.connect("containerid")

    # Check calls and order of calls
    assert method_call_list == ["_set_client", "_get_database", "_find_container"]


def test_connect_error(caplog):
    logging.getLogger("api").propagate = True
    cosmos_client_mock = create_autospec(AzureCosmosClient)

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ), patch.object(
        CosmosClient, "_set_client", autospec=True, side_effect=Exception("test")
    ):
        cosmos = CosmosClient()
        cosmos.connect("containerid")

    assert "Failed to get connection to the Db. Message=" in caplog.text


def test_get_database_sucess():
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    db_proxy_mock = create_autospec(DatabaseProxy)
    cosmos_client_mock.get_database_client.return_value = db_proxy_mock

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ):
        cosmos = CosmosClient()
        cosmos.client = cosmos_client_mock
        database_id = "db_id"
        cosmos._get_database(database_id)

    assert cosmos.db == db_proxy_mock


def test_get_database_unhandled_error():
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    db_proxy_mock = create_autospec(DatabaseProxy)
    db_proxy_mock.read.side_effect = Exception()
    cosmos_client_mock.get_database_client.return_value = db_proxy_mock

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ):
        cosmos = CosmosClient()
        cosmos.client = cosmos_client_mock
        database_id = "db_id"

        with pytest.raises(Exception):
            cosmos._get_database(database_id)


def test_get_database_database_not_found(caplog):
    logging.getLogger("api").propagate = True
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    db_proxy_mock = create_autospec(DatabaseProxy)
    db_proxy_mock.read.side_effect = CosmosResourceNotFoundError()
    cosmos_client_mock.get_database_client.return_value = db_proxy_mock

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ):
        cosmos = CosmosClient()
        cosmos.client = cosmos_client_mock
        database_id = "db_id"

        with caplog.at_level(logging.ERROR):
            cosmos._get_database(database_id)

    assert f"A database with id '{database_id}' does not exist. Message=" in caplog.text


def test_find_container_sucess():
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    container_proxy_mock = create_autospec(ContainerProxy)
    db_proxy_mock = create_autospec(DatabaseProxy)
    db_proxy_mock.get_container_client.return_value = container_proxy_mock

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ):
        cosmos = CosmosClient()
        cosmos.client = cosmos_client_mock
        cosmos.db = db_proxy_mock
        container_id = "container_id"
        cosmos._find_container(container_id)

    assert cosmos.container == container_proxy_mock


def test_find_container_container_not_found(caplog):
    logging.getLogger("api").propagate = True
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    db_proxy_mock = create_autospec(DatabaseProxy)
    db_proxy_mock.get_container_client.side_effect = CosmosResourceNotFoundError()

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ):
        cosmos = CosmosClient()
        cosmos.client = cosmos_client_mock
        cosmos.db = db_proxy_mock
        container_id = "container_id"
        with caplog.at_level(logging.ERROR):
            cosmos._find_container(container_id)

    assert (
        f"A container with id '{container_id}' does not exist.  Message=" in caplog.text
    )


def test_find_container_unhandled_error():
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    db_proxy_mock = create_autospec(DatabaseProxy)
    db_proxy_mock.get_container_client.side_effect = Exception()

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ):
        cosmos = CosmosClient()
        cosmos.client = cosmos_client_mock
        cosmos.db = db_proxy_mock
        container_id = "container_id"

        with pytest.raises(Exception):
            cosmos._find_container(container_id)


def test_get_items_has_results():
    cosmos_client_mock = create_autospec(AzureCosmosClient)
    container_proxy_mock = create_autospec(ContainerProxy)
    db_proxy_mock = create_autospec(DatabaseProxy)
    container_proxy_mock.query_items.return_value = ({"id": "dummy1"}, {"id": "dummy2"})

    with patch(
        "classes.cosmos_client.CosmosClient",
        cosmos_client_mock,
    ):
        cosmos = CosmosClient()
        cosmos.client = cosmos_client_mock
        cosmos.db = db_proxy_mock
        cosmos.container = container_proxy_mock
        items = cosmos.get_items("somequery", {"param": "param_value"})

    assert isinstance(items, list)
    assert len(items) == 2
