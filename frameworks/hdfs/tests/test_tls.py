import pytest

import sdk_cmd
import sdk_install
import sdk_plan
import sdk_security
import sdk_utils
import shakedown
from tests import config
from tests.config import (
    PACKAGE_NAME,
    SERVICE_NAME,
)


@pytest.fixture(scope='module')
def service_account():
    """
    Creates service account with `hdfs` name and yields the name.
    """
    name = SERVICE_NAME
    sdk_security.create_service_account(
        service_account_name=name, service_account_secret=name)
     # TODO(mh): Fine grained permissions needs to be addressed in DCOS-16475
    sdk_cmd.run_cli(
        "security org groups add_user superusers {name}".format(name=name))
    yield name
    sdk_security.delete_service_account(
        service_account_name=name, service_account_secret=name)


@pytest.fixture(scope='module')
def hdfs_service_tls(service_account):
    sdk_install.install(
        PACKAGE_NAME,
        service_name=SERVICE_NAME,
        expected_running_tasks=NO_INGEST_TASK_COUNT,
        additional_options={
            "service": {
                "service_account_secret": service_account,
                "service_account": service_account,
                "tls": {
                    "enabled": True,
                }
            }
        }
    )

    sdk_plan.wait_for_completed_deployment(SERVICE_NAME)

    # Wait for service health check to pass
    shakedown.service_healthy(SERVICE_NAME)

    yield

    sdk_install.uninstall(PACKAGE_NAME, SERVICE_NAME)


@pytest.mark.tls
@pytest.mark.smoke
@sdk_utils.dcos_1_10_or_higher
def test_healthy(hdfs_service_tls):
    config.check_healthy(service_name=config.SERVICE_NAME)


@pytest.mark.tls
@pytest.mark.sanity
@pytest.mark.data_integrity
@sdk_utils.dcos_1_10_or_higher
def test_write_and_read_data_over_tls(hdfs_service_tls):
    config.write_data_to_hdfs(config.SERVICE_NAME, config.TEST_FILE_1_NAME)
    config.read_data_from_hdfs(config.SERVICE_NAME, config.TEST_FILE_1_NAME)
