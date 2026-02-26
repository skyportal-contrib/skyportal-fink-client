# coding: utf-8
import pytest

from skyportal_fink_client.skyportal_fink_client import validate_config

VALID_CONFIG = {
    "fink_topics": ["fink_sn_candidates_ztf"],
    "fink_username": "user",
    "fink_password": None,
    "fink_group_id": "my_group",
    "fink_servers": "kafka.example.org:24499",
    "skyportal_url": "http://localhost:5000",
    "skyportal_token": "abc123",
    "skyportal_group": "Fink",
    "survey": "ztf",
    "testing": False,
    "whitelisted": False,
}


def _config(**overrides):
    return {**VALID_CONFIG, **overrides}


def test_valid_config_passes():
    validate_config(VALID_CONFIG)


def test_valid_config_lsst():
    validate_config(_config(survey="lsst"))


def test_password_can_be_none():
    validate_config(_config(fink_password=None))


@pytest.mark.parametrize(
    "field",
    [
        "fink_topics",
        "fink_username",
        "fink_group_id",
        "fink_servers",
        "skyportal_url",
        "skyportal_token",
        "skyportal_group",
        "testing",
        "whitelisted",
    ],
)
def test_missing_required_field_raises(field):
    conf = {k: v for k, v in VALID_CONFIG.items() if k != field}
    with pytest.raises(ValueError, match="Missing required field"):
        validate_config(conf)


def test_invalid_survey_raises():
    with pytest.raises(ValueError, match="Invalid survey"):
        validate_config(_config(survey="rubin"))


def test_empty_topics_list_raises():
    with pytest.raises(ValueError, match="fink_topics"):
        validate_config(_config(fink_topics=[]))


def test_topics_not_a_list_raises():
    with pytest.raises(ValueError, match="fink_topics"):
        validate_config(_config(fink_topics="fink_sn_candidates_ztf"))


@pytest.mark.parametrize(
    "field",
    ["skyportal_url", "skyportal_token", "fink_group_id", "fink_servers"],
)
def test_empty_string_field_raises(field):
    with pytest.raises(ValueError, match=field):
        validate_config(_config(**{field: ""}))
