# coding: utf-8
import pytest

from skyportal_fink_client.skyportal_fink_client import _extract_lsst_data

TOPIC = "fink_extragalactic_new_candidate_lsst"

VALID_DIA_SOURCE = {
    "midpointMjdTai": 60000.0,
    "band": "r",
    "psfFlux": 1000.0,
    "psfFluxErr": 50.0,
    "ra": 10.5,
    "dec": -20.3,
}

VALID_DIA_OBJECT = {
    "diaObjectId": 123456,
    "ra": 10.5,
    "dec": -20.3,
}


def _alert(**overrides):
    alert = {
        "diaSource": {**VALID_DIA_SOURCE},
        "diaObject": {**VALID_DIA_OBJECT},
    }
    alert.update(overrides)
    return alert


def test_valid_alert_returns_data():
    result = _extract_lsst_data(TOPIC, _alert())
    assert result is not None
    assert len(result) == 12


def test_object_id_is_string_of_int64():
    # np.int64 ensures no int32 truncation; str() makes it SkyPortal-compatible
    result = _extract_lsst_data(TOPIC, _alert())
    assert isinstance(result[0], str)
    assert result[0] == "123456"


def test_object_id_preserves_large_lsst_ids():
    # values exceeding int32 range (2^31-1 = 2_147_483_647) must not be truncated
    large_id = 313721465979011198
    alert = _alert()
    alert["diaObject"]["diaObjectId"] = large_id
    result = _extract_lsst_data(TOPIC, alert)
    assert result[0] == str(large_id)


def test_zp_is_31_4():
    # LSST has no limiting mag, so flux space is used with zp=31.4 (nJy AB)
    result = _extract_lsst_data(TOPIC, _alert())
    assert result[6] == pytest.approx(31.4)


def test_is_flux_flag_is_true():
    result = _extract_lsst_data(TOPIC, _alert())
    assert result[11] is True


def test_classification_from_topic():
    result = _extract_lsst_data(TOPIC, _alert())
    assert result[10] == "Extragalactic New Candidate"


def test_coordinates_from_dia_object():
    result = _extract_lsst_data(TOPIC, _alert())
    assert result[8] == pytest.approx(10.5)
    assert result[9] == pytest.approx(-20.3)


def test_coordinates_fallback_to_dia_source():
    diaobj = {**VALID_DIA_OBJECT}
    diaobj.pop("ra")
    diaobj.pop("dec")
    alert = {"diaSource": {**VALID_DIA_SOURCE}, "diaObject": diaobj}
    result = _extract_lsst_data(TOPIC, alert)
    assert result is not None
    assert result[8] == pytest.approx(10.5)
    assert result[9] == pytest.approx(-20.3)


def test_object_id_from_mpc_orbits():
    alert = {
        "diaSource": {**VALID_DIA_SOURCE},
        "mpc_orbits": {"designation": "2024 AB1"},
    }
    result = _extract_lsst_data(TOPIC, alert)
    assert result is not None
    assert result[0] == "2024 AB1"


def test_instruments_are_lsst():
    result = _extract_lsst_data(TOPIC, _alert())
    assert "LSST" in result[2]


def test_missing_dia_source_returns_none():
    assert _extract_lsst_data(TOPIC, {}) is None


def test_none_alert_returns_none():
    assert _extract_lsst_data(TOPIC, None) is None


def test_missing_dia_object_and_mpc_returns_none():
    alert = {"diaSource": {**VALID_DIA_SOURCE}}
    assert _extract_lsst_data(TOPIC, alert) is None


def test_negative_flux_returns_none():
    alert = _alert()
    alert["diaSource"]["psfFlux"] = -100.0
    assert _extract_lsst_data(TOPIC, alert) is None


def test_zero_flux_returns_none():
    alert = _alert()
    alert["diaSource"]["psfFlux"] = 0.0
    assert _extract_lsst_data(TOPIC, alert) is None


@pytest.mark.parametrize("field", ["midpointMjdTai", "band", "psfFlux", "psfFluxErr"])
def test_missing_required_dia_source_field_returns_none(field):
    alert = _alert()
    alert["diaSource"].pop(field)
    assert _extract_lsst_data(TOPIC, alert) is None


def test_unknown_band_returns_none():
    alert = _alert()
    alert["diaSource"]["band"] = "x"
    assert _extract_lsst_data(TOPIC, alert) is None


def test_missing_coordinates_returns_none():
    diaobj = {"diaObjectId": 123456}
    dia = {k: v for k, v in VALID_DIA_SOURCE.items() if k not in ("ra", "dec")}
    assert _extract_lsst_data(TOPIC, {"diaSource": dia, "diaObject": diaobj}) is None
