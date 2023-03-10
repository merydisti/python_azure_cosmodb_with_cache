import logging
from datetime import datetime, timedelta
from unittest.mock import MagicMock, create_autospec, patch

import pytest

from classes.cache import Cache
from classes.cosmos_client import CosmosClient


@pytest.fixture
def cache_class():
    Cache.data = {}  # cleanup
    yield Cache


def test_set_expiration(cache_class):
    cache_instance = cache_class()
    mocked_today = datetime(2023, 2, 1)
    with patch("classes.cache.datetime") as datetime_mock:
        datetime_mock.today.return_value = mocked_today
        expiration_time = cache_instance._set_expiration()

    #TODO: Add enviroment variable in to delta
    assert expiration_time == mocked_today + timedelta(
        seconds=int(1140)
    )


def test_is_expired(cache_class):
    cache_instance = cache_class()
    fixed_time = datetime(2023, 2, 1)
    fixed_later_time = datetime(2023, 3, 10)

    with patch("classes.cache.datetime") as datetime_mock:
        datetime_mock.now.return_value = fixed_later_time
        assert cache_instance._is_expirated(fixed_time)


def test_set_data_data_returned_from_database(cache_class):
    data = [{"id": 1, "afield": "somedata"}, {"id": 1, "afield": "somedata"}]
    cosmos_client_mock = create_autospec(CosmosClient)
    cosmos_client_mock.return_value.get_items.return_value = data
    expiration = datetime(2023, 2, 1)

    with patch("classes.cache.CosmosClient", cosmos_client_mock):
        cache_instance = cache_class()

        with patch.object(cache_instance, "_set_expiration", return_value=expiration):
            returned_data = cache_instance._set_data("containerid", "name", "query", {})

    assert returned_data == data
    assert cache_instance.data["name"] == {"data": data, "expiration": expiration}


def test_set_data_no_data_returned_from_database(cache_class):
    cosmos_client_mock = create_autospec(CosmosClient)
    cosmos_client_mock.return_value.get_items.return_value = {}
    expiration = datetime(2023, 2, 1)

    with patch("classes.cache.CosmosClient", cosmos_client_mock):
        cache_instance = cache_class()

        with patch.object(cache_instance, "_set_expiration", return_value=expiration):
            returned_data = cache_instance._set_data("containerid", "name", "query", {})

    assert not returned_data
    assert "name" not in cache_instance.data


def test_set_data_database_client_error(cache_class, caplog):
    logging.getLogger("api").propagate = True

    cosmos_client_mock = create_autospec(CosmosClient)
    cosmos_client_mock.return_value.get_items.side_effect = Exception("test")

    with patch("classes.cache.CosmosClient", cosmos_client_mock):
        with caplog.at_level(logging.ERROR):
            cache_instance = cache_class()
            returned_data = cache_instance._set_data("containerid", "name", "query", {})

    assert "Failed to connect/read from DB. Message=test" in caplog.text
    assert returned_data is None


def test_get_data_data_aleady_in_cache(cache_class):
    data = [{"id": 1, "afield": "somedata"}, {"id": 1, "afield": "somedata"}]
    cosmos_client_mock = create_autospec(CosmosClient)
    cosmos_client_mock.return_value.get_items.return_value = data
    mocked_now = datetime(2023, 2, 1)
    expiration = datetime(2023, 2, 3)

    with patch("classes.cache.datetime", return_value=mocked_now) as datetime_mock, patch(
        "classes.cache.CosmosClient", cosmos_client_mock
    ):
        datetime_mock.now.return_value = mocked_now
        cache_instance = cache_class()
        cache_instance.data["name"] = {"data": data, "expiration": expiration}
        returned_data = cache_instance.get_data("containerid", "name", "query", {})

    assert returned_data == data
    assert not cosmos_client_mock.return_value.get_items.called, "Should not hit db"


def test_get_data_aleady_in_cache_but_expired(cache_class):
    data = [{"id": 1, "afield": "somedata"}, {"id": 1, "afield": "somedata"}]
    cosmos_client_mock = create_autospec(CosmosClient)
    cosmos_client_mock.return_value.get_items.return_value = data
    mocked_now = datetime(2023, 2, 3)
    expiration = datetime(2023, 2, 1)

    with patch("classes.cache.datetime", return_value=mocked_now) as datetime_mock, patch(
        "classes.cache.CosmosClient", cosmos_client_mock
    ):
        datetime_mock.now.return_value = mocked_now
        cache_instance = cache_class()
        cache_instance.data["name"] = {"data": data, "expiration": expiration}
        returned_data = cache_instance.get_data("containerid", "name", "query", {})

    assert returned_data == data
    assert cosmos_client_mock.return_value.get_items.called


def test_get_data_data_not_in_cache(cache_class):
    data = [{"id": 1, "afield": "somedata"}, {"id": 1, "afield": "somedata"}]
    cosmos_client_mock = create_autospec(CosmosClient)
    cosmos_client_mock.return_value.get_items.return_value = data
    mocked_now = datetime(2023, 2, 3)

    with patch("classes.cache.datetime", return_value=mocked_now) as datetime_mock, patch(
        "classes.cache.CosmosClient", cosmos_client_mock
    ):
        datetime_mock.now.return_value = mocked_now
        cache_instance = cache_class()
        returned_data = cache_instance.get_data("containerid", "name", "query", {})

    assert returned_data == data
    assert cosmos_client_mock.return_value.get_items.called
