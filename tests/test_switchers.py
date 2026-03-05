# coding: utf-8
import math

import pytest

from skyportal_fink_client.utils.switchers import (
    band_to_filter_lsst,
    fid_to_filter_ztf,
    flux_err_to_mag_err,
    flux_to_mag,
)


@pytest.mark.parametrize(
    "fid, expected",
    [(1, "ztfg"), (2, "ztfr"), (3, "ztfi")],
)
def test_fid_to_filter_ztf_valid(fid, expected):
    assert fid_to_filter_ztf(fid) == expected


def test_fid_to_filter_ztf_unknown_returns_none():
    assert fid_to_filter_ztf(99) is None


@pytest.mark.parametrize(
    "band, expected",
    [
        ("u", "lsstu"),
        ("g", "lsstg"),
        ("r", "lsstr"),
        ("i", "lssti"),
        ("z", "lsstz"),
        ("y", "lssty"),
    ],
)
def test_band_to_filter_lsst_valid(band, expected):
    assert band_to_filter_lsst(band) == expected


def test_band_to_filter_lsst_unknown_returns_none():
    assert band_to_filter_lsst("x") is None


def test_flux_to_mag_known_value():
    # 1 nJy → -2.5*log10(1) + 31.4 = 31.4
    assert flux_to_mag(1.0) == pytest.approx(31.4)


def test_flux_to_mag_increases_as_flux_decreases():
    # fainter objects have higher magnitude
    assert flux_to_mag(100.0) < flux_to_mag(10.0)


def test_flux_err_to_mag_err_known_value():
    # SNR=10 → magerr ≈ 2.5/ln(10) * 0.1 ≈ 0.1086
    result = flux_err_to_mag_err(flux_nJy=1000.0, flux_err_nJy=100.0)
    assert result == pytest.approx(2.5 / math.log(10) * 0.1, rel=1e-5)


def test_flux_err_to_mag_err_symmetric():
    # sign of flux_err should not affect the result
    result_pos = flux_err_to_mag_err(1000.0, 100.0)
    result_neg = flux_err_to_mag_err(1000.0, -100.0)
    assert result_pos == pytest.approx(result_neg)
