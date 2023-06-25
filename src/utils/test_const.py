import os
import pytest


@pytest.mark.parametrize("env_var", [
    "DATA_PATH",
    "WAF_CONTAINER_NAME",
    "CADVISOR_ENDPOINT",
    "FTW_TEST_FILE_PATH"
])

def test_env_variables_exist(env_var):
    assert env_var in os.environ