def fid_to_filter_ztf(fid: int):
    """
    Convert a fid to a filter name.
    In the alert data from Fink, the fid corresponds to the 3 different filters used by the ZTF telescope.

    Parameters
    ----------
        fid : int
            id of a filter in an alert

    Returns
    ----------
        filter : str
            name of the filter
    """
    switcher = {1: "ztfg", 2: "ztfr", 3: "ztfi"}
    return switcher.get(fid)
