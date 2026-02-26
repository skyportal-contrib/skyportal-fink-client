# coding: utf-8
import pytest

from skyportal_fink_client.skyportal_fink_client import _topic_to_classification


@pytest.mark.parametrize(
    "topic, expected",
    [
        ("fink_sn_candidates_ztf", "Sn Candidates"),
        ("fink_kn_candidates_ztf", "Kn Candidates"),
        ("fink_early_kn_candidates_ztf", "Early Kn Candidates"),
        ("fink_extragalactic_new_candidate_lsst", "Extragalactic New Candidate"),
        ("fink_sn_candidates_rubin", "Sn Candidates"),
        ("fink_blazar_rubin", "Blazar"),
    ],
)
def test_topic_to_classification(topic, expected):
    assert _topic_to_classification(topic) == expected


def test_topic_without_fink_prefix():
    # topics not starting with "fink_" are returned as-is (capitalised)
    assert _topic_to_classification("my_custom_topic") == "My Custom Topic"


def test_topic_strips_only_one_suffix():
    # only the last survey suffix is stripped
    assert _topic_to_classification("fink_sn_ztf_ztf") == "Sn Ztf"
