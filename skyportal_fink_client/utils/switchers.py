import numpy as np


def fid_to_filter_ztf(fid: int):
    """
    Convert a ZTF fid integer to a filter name.

    Parameters
    ----------
    fid : int
        id of a filter in a ZTF alert (1=g, 2=r, 3=i)

    Returns
    -------
    filter : str
        name of the filter
    """
    switcher = {1: "ztfg", 2: "ztfr", 3: "ztfi"}
    return switcher.get(fid)


_LSST_BAND_TO_FILTER = {
    "u": "lsstu",
    "g": "lsstg",
    "r": "lsstr",
    "i": "lssti",
    "z": "lsstz",
    "y": "lssty",
}


def band_to_filter_lsst(band: str):
    """
    Convert an LSST band letter to a SkyPortal filter name.

    Parameters
    ----------
    band : str
        Band name from a Rubin/LSST alert (u, g, r, i, z, y)

    Returns
    -------
    filter : str or None
        SkyPortal filter name, or None if band is unrecognised
    """
    return _LSST_BAND_TO_FILTER.get(band)


def flux_to_mag(flux_nJy: float) -> float:
    """
    Convert flux in nJy to AB magnitude.

    Parameters
    ----------
    flux_nJy : float
        Flux in nano-Jansky

    Returns
    -------
    mag : float
        AB magnitude
    """
    return -2.5 * np.log10(flux_nJy) + 31.4


def flux_err_to_mag_err(flux_nJy: float, flux_err_nJy: float) -> float:
    """
    Convert flux and flux error in nJy to magnitude error.

    Parameters
    ----------
    flux_nJy : float
        Flux in nano-Jansky
    flux_err_nJy : float
        Flux error in nano-Jansky

    Returns
    -------
    magerr : float
        Magnitude error
    """
    return 2.5 / np.log(10) * abs(flux_err_nJy / flux_nJy)
