import time

from SPI.modules.base_spi import EVENT_SPI_UPDATED, EVENT_SPI_DELETED
from tests.SPI_generator.utils import create_sp, update_sp, delete_sp, create_station


def test_station_create(setup_db, actor_setup, create_mocks):
    version_1, version_3 = create_mocks
    sp = create_sp("zzebu")
    time.sleep(0.150)
    create_station(sp.id)
    time.sleep(0.150)

    version_1.assert_called_with(
        EVENT_SPI_UPDATED,
        {"id": 1, "codops": "zzebu"},
        None
    )

    version_3.assert_called_with(
        EVENT_SPI_UPDATED,
        {"id": 1, "codops": "zzebu"},
        None
    )


# def test_service_provider_update(setup_db, actor_setup, create_mocks):
#     version_1, version_3 = create_mocks
#     update_sp(1, "test2")
#
#     time.sleep(0.150)
#
#     version_1.assert_called_with(
#         EVENT_SPI_UPDATED,
#         {"id": 1, "codops": "zzebu"},
#         None
#     )
#
#     version_3.assert_called_with(
#         EVENT_SPI_UPDATED,
#         {"id": 1, "codops": "zzebu"},
#         None
#     )
#
#
# def test_service_provider_delete(setup_db, actor_setup, create_mocks):
#     version_1, version_3 = create_mocks
#     delete_sp(1)
#
#     time.sleep(0.150)
#
#     version_1.assert_called_with(
#         EVENT_SPI_DELETED,
#         {"id": 1, "codops": "zzebu"},
#         None
#     )
#
#     version_3.assert_called_with(
#         EVENT_SPI_DELETED,
#         {"id": 1, "codops": "zzebu"},
#         None
#     )
#