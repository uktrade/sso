from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_signature_checker():
    mock_path = 'sigauth.helpers.RequestSignatureChecker.test_signature'
    patcher = patch(mock_path, return_value=True)
    patcher.start()
    yield
    patcher.stop()


@pytest.fixture(autouse=True)
def feature_flags(settings):
    # solves this issue: https://github.com/pytest-dev/pytest-django/issues/601
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS}
    yield settings.FEATURE_FLAGS
