import requests
from astropy.time import Time
import time


def api(
    method,
    endpoint,
    data=None,
    token=None,
):
    """
    Make an API call to skyportal

    Arguments
    ----------
        method : str
            HTTP method to use
        endpoint : str
            Endpoint to call
        data : dict
            Data to send with the request
        token : str
            Skyportal token

    Returns
    ----------
        response : requests.Response
            Response from skyportal

    """
    headers = {"Authorization": f"token {token}"}
    response = requests.request(method, endpoint, json=data, headers=headers)
    return response


def get_all_group_ids(url: str, token: str):
    """
    Get all group ids from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status : int
            HTTP status code
        data : list
            List of group ids

    """
    groups = api("GET", f"{url}/api/groups", token=token)

    data = []
    if groups.status_code == 200:
        data = [group["id"] for group in groups.json()["data"]["all_groups"]]
    return groups.status_code, data


def get_group_ids_and_name(url: str, token: str):
    """
    Get all group ids and their names from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of group ids and their names
    """

    groups = api("GET", f"{url}/api/groups", token=token)

    data = {}
    if groups.status_code == 200:
        data = {
            group["name"]: group["id"]
            for group in groups.json()["data"]["user_accessible_groups"]
        }
    return groups.status_code, data


def get_all_instruments(url: str, token: str):
    """
    Get all instruments from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of instruments
    """
    instruments = api("GET", f"{url}/api/instrument", token=token)

    data = {}
    if instruments.status_code == 200:
        data = {
            instrument["name"]: instrument["id"]
            for instrument in instruments.json()["data"]
        }
    return instruments.status_code, data


def get_all_source_ids(url: str, token: str):
    """
    Get all source ids from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of source ids
    """
    sources = api("GET", f"{url}/api/sources", token=token)

    data = []
    if sources.status_code == 200:
        data = [source["id"] for source in sources.json()["data"]["sources"]]
    return sources.status_code, data


def get_all_candidate_ids(url: str, token: str):
    """
    Get all candidate ids from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of candidate ids
    """
    candidates = api("GET", f"{url}/api/candidates", token=token)

    return candidates.status_code, [
        candidate["id"] for candidate in candidates.json()["data"]["candidates"]
    ]


def get_all_streams(url: str, token: str):
    """
    Get all streams from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of streams
    """
    streams = api("GET", f"{url}/api/streams", token=token)

    return streams.status_code, streams.json()["data"]


def get_all_stream_ids(url: str, token: str):
    """
    Get all stream ids from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of stream ids
    """
    streams = api("GET", f"{url}/api/streams", token=token)

    data = []
    if streams.status_code == 200:
        data = [stream["id"] for stream in streams.json()["data"]]
    return streams.status_code, data


def classification_exists_for_objs(object_id: str, url: str, token: str):
    """
    Check if a classification exists for a given object

    Arguments
    ----------
        object_id : str
            Object id to check if classification exists for
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        exists : bool
            True if classification exists, False otherwise
    """
    classifications = api(
        "GET",
        f"{url}/api/sources/{object_id}/classifications",
        token=token,
    )
    return classifications.json()["data"] != []


def classification_id_for_objs(object_id: str, url: str, token: str):
    """
    Get classification id for a given object

    Arguments
    ----------
        object_id : str
            Object id to get classification id for
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of classification ids and their author ids
    """
    classifications = api(
        "GET",
        f"{url}/api/sources/{object_id}/classifications",
        token=token,
    )
    data = {}
    if classifications.status_code == 200:
        data = {
            "id": classifications.json()["data"][0]["id"],
            "author_id": classifications.json()["data"][0]["author_id"],
        }
    return classifications.status_code, data


def post_source(
    object_id: str, ra: float, dec: float, group_ids: list, url: str, token: str
):
    """
    Post a source to skyportal using its API

    Arguments
    ----------
        object_id : str
            Object id to post source for
        ra : float
            Right ascension of object
        dec : float
            Declination of object
        group_ids : list
            List of group ids to post source to
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Source id
    """
    data = {
        "ra": ra,
        "dec": dec,
        "id": object_id,
        # "ra_dis": 0,
        # "dec_dis": 0,
        # "ra_err": 0,
        # "dec_err": 0,
        # "offset": 0,
        # "redshift": 0,
        # "redshift_error": 0,
        # "altdata": null,
        # "dist_nearest_source": 0,
        # "mag_nearest_source": 0,
        # "e_mag_nearest_source": 0,
        # "transient": true,
        # "varstar": true,
        # "is_roid": true,
        # "score": 0,
        # "origin": "string",
        # "alias": null,
        # "detect_photometry_count": 0,
        "group_ids": group_ids,
    }

    response = api("POST", f"{url}/api/sources", data, token=token)
    return (
        response.status_code,
        response.json()["data"]["id"] if response.json()["data"] != {} else {},
    )


def post_candidate(
    object_id: str,
    ra: float,
    dec: float,
    filter_ids: list,
    passed_at: str,
    url: str,
    token: str,
):
    """
    Post a candidate to skyportal using its API

    Arguments
    ----------
        object_id : str
            Object id to post candidate for
        ra : float
            Right ascension of object
        dec : float
            Declination of object
        filter_ids : list
            List of filter ids for this candidate
        passed_at : str
            Date and time candidate was passed
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Candidate id
    """

    data = {
        "ra": ra,
        "dec": dec,
        "id": object_id,
        # "ra_dis": 0,
        # "dec_dis": 0,
        # "ra_err": 0,
        # "dec_err": 0,
        # "offset": 0,
        # "redshift": 0,
        # "redshift_error": 0,
        # "altdata": null,
        # "dist_nearest_source": 0,
        # "mag_nearest_source": 0,
        # "e_mag_nearest_source": 0,
        # "transient": true,
        # "varstar": true,
        # "is_roid": true,
        # "score": 0,
        # "origin": "string",
        # "alias": null,
        # "detect_photometry_count": 0,
        # /!\ HARDCODED FILTER ID TO ONE, ISSUES WITH IT FOR THE MOMENT
        "filter_ids": filter_ids,
        # "passing_alert_id": 0,
        "passed_at": passed_at,
    }
    response = api("POST", f"{url}/api/candidates", data, token=token)
    return (
        response.status_code,
        response.json()["data"]["ids"] if response.json()["data"] != {} else {},
    )


def post_photometry(
    object_id: str,
    mjd: float,
    instrument_id: int,
    filter: str,
    mag: float,
    magerr: float,
    limiting_mag: float,
    magsys: str,
    ra: float,
    dec: float,
    group_ids: list,
    stream_ids: list,
    url: str,
    token: str,
):
    """
    Post a photometry to skyportal using its API
    Arguments
    ----------
        object_id : str
            Object id to post candidate for
        mjd : float
            Modified Julian Date of the observation
        instrument_id : int
            id of the instrument used to observe the object
        filter : str
            Filter used by the instrument to observe the object
        mag : float
            Magnitude value of the observation
        magerr : float
            Magnitude error value of the observation
        limiting_mag : float
            Limiting magnitude value of the observation
        magsys : str
            Magnitude system used for the magnitude values
        ra : float
            Right ascension of object
        dec : float
            Declination of object
        group_ids : list
            List of group ids to post photometry to
        stream_ids : list
            List of stream ids to post photometry to
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Source id
    """
    data = {
        "ra": ra,
        # "ra_unc": 0,
        "magerr": magerr,
        "magsys": magsys,
        "group_ids": group_ids,
        # "altdata": None,
        "mag": mag,
        "mjd": mjd,
        # "origin": None,
        "filter": filter,
        "limiting_mag": limiting_mag,
        # "limiting_mag_nsigma": 0,
        # "dec_unc": 0,
        # "assignment_id": None,
        "stream_ids": stream_ids,
        "dec": dec,
        "instrument_id": instrument_id,
        "obj_id": object_id,
    }

    response = api("POST", f"{url}/api/photometry", data, token=token)
    print(response.json())
    return (
        response.status_code,
        response.json()["data"]["ids"] if response.json()["data"] != {} else {},
    )


def post_classification(
    object_id: str,
    classification: str,
    probability: float,
    taxonomy_id: int,
    group_ids: list,
    url: str,
    token: str,
):
    """
    Post a classification to skyportal using its API

    Arguments
    ----------
        object_id : str
            Object id to post candidate for
        classification : str
            Classification of the object, e.g. 'kilonova'
        probability : float
            Probability of the classification
        taxonomy_id : int
            id of the taxonomy in which the classification is defined
        groups_ids : list
            List of group ids to post classification to
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Classification id
    """
    data = {
        "classification": classification,
        "taxonomy_id": taxonomy_id,
        "probability": probability,
        "obj_id": object_id,
        "group_ids": group_ids,
    }

    response = api(
        "POST",
        f"{url}/api/classification",
        data,
        token=token,
    )

    return response.status_code, response.json()


def post_streams(name: str, url: str, token: str):
    """
    Post a stream to skyportal using its API

    Arguments
    ----------
        name : str
            Name of the stream to post
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Stream id
    """
    data = {"name": name}

    response = api("POST", f"{url}/api/streams", data, token=token)
    return (
        response.status_code,
        response.json()["data"]["id"] if response.json()["data"] != {} else None,
    )


def post_filters(name: str, stream_id: int, group_id: int, url: str, token: str):
    """
    Post a filter to skyportal using its API

    Arguments
    ----------
        name : str
            Name of the filter to post
        stream_id : int
            id of the stream to post filter to
        group_id : int
            id of the group to post filter to
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Filter id
    """
    data = {"name": name, "stream_id": stream_id, "group_id": group_id}

    response = api("POST", f"{url}/api/filters", data, token=token)
    return (
        response.status_code,
        response.json()["data"]["id"] if response.json()["data"] != {} else None,
    )


def post_telescopes(name: str, nickname: str, diameter: float, url: str, token: str):
    """
    Post a telescope to skyportal using its API

    Arguments
    ----------
        name : str
            Name of the telescope to post
        nickname : str
            Nickname of the telescope to post
        diameter : float
            Diameter of the telescope to post
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Telescope id
    """
    data = {"name": name, "nickname": nickname, "diameter": diameter}
    response = api("POST", f"{url}/api/telescope", data, token=token)
    return (
        response.status_code,
        response.json()["data"]["id"] if response.json()["data"] != {} else None,
    )


def post_instruments(
    name: str, type: str, telescope_id: int, filters: list, url: str, token: str
):
    """
    Post an instrument to skyportal using its API

    Arguments
    ----------
        name : str
            Name of the instrument to post
        type : str
            Type of the instrument to post
        telescope_id : int
            Id of the telescope to which the instrument is attached
        filters : list
            List of filters the instrument has
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Instrument id
    """
    data = {
        "name": name,
        "type": "imager",
        "filters": filters,
        "telescope_id": telescope_id,
    }
    response = api("POST", f"{url}/api/instrument", data, token=token)
    print(response.json())
    return (
        response.status_code,
        response.json()["data"]["id"] if response.json()["data"] != {} else {},
    )


def post_groups(name: str, url: str, token: str):
    """
    Post a group to skyportal using its API

    Arguments
    ----------
        name : str
            Name of the group to post
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Group id
    """
    data = {
        "name": name,
        "group_admins": [1],
    }
    response = api("POST", f"{url}/api/groups", data, token=token)
    return (
        response.status_code,
        response.json()["data"]["id"] if response.json()["data"] != {} else None,
    )


def post_taxonomy(name: str, hierarchy: dict, version: str, url: str, token: str):
    """
    Post a taxonomy to skyportal using its API

    Arguments
    ----------
        name: str
            Name of the taxonomy to post
        hierarchy: dict
            Hierarchy of the taxonomy to post
        version: str
            Version of the taxonomy to post
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : int
            Taxonomy id
    """
    data = {
        "name": name,
        "hierarchy": hierarchy,
        # "group_ids": group_ids
        "version": version,
        # "provenance": provenance,
        # "isLatest": true
    }
    response = api("POST", f"{url}/api/taxonomy", data, token=token)
    return (
        response.status_code,
        response.json()["data"]["taxonomy_id"]
        if response.json()["data"] != {}
        else None,
    )


def update_classification(
    object_id: str,
    classification: str,
    probability: float,
    taxonomy_id: int,
    group_ids: list,
    url: str,
    token: str,
):
    """
    Update a classification to skyportal using its API

    Arguments
    ----------
        object_id : str
            Id of the object for which we update the classification
        classification : str
            Classification of the object
        probability : float
            Probability of classification
        taxonomy_id : int
            id of the taxonomy in which the classification is defined
        group_ids : list
            List of group ids to post the classification to
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
    """

    data_classification = classification_id_for_objs(object_id, url, token)[1]
    classification_id, author_id = (
        data_classification["id"],
        data_classification["author_id"],
    )

    data = {
        "obj_id": object_id,
        "classification": classification,
        "probability": probability,
        "taxonomy_id": taxonomy_id,
        "group_ids": group_ids,
        "author_id": author_id,
        "author_name": "fink_client",
    }

    response = api(
        "PUT",
        f"{url}/api/classification/{classification_id}",
        data,
        token=token,
    )
    return response.status_code


def get_all_filters(url: str, token: str):
    """
    Get all filters from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of filters
    """
    response = api("GET", f"{url}/api/filters", token=token)
    return (response.status_code, response.json()["data"])


def get_all_taxonomies(url: str, token: str):
    """
    Get all taxonomies from skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        data : list
            List of taxonomies
    """
    response = api("GET", f"{url}/api/taxonomy", token=token)
    return (response.status_code, response.json()["data"])


def init_skyportal(url: str, token: str):
    """
    Creates the different entities needed in skyportal to add the data of alerts from fink
    (streams, filters, groups) and returns the ids of the entities created, so they can be used to post the alerts to skyportal using its API

    Arguments
    ----------
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        fink_id : int
            Id of the fink group in SkyPortal
        stream_id : int
            Id of the fink stream in SkyPortal
        filter_id : int
            Id of the fink filter in SkyPortal
    """
    streams = get_all_streams(url, token)[1]
    # check if a stream with name 'fink_stream' exists
    stream_id = None
    if streams:
        for stream in streams:
            if stream["name"] == "fink_stream":
                stream_id = stream["id"]
                break
    if not stream_id:
        stream_id = post_streams("fink_stream", url, token)[1]
    groups_dict = get_group_ids_and_name(url=url, token=token)[1]
    fink_id = None
    if "Fink" not in list(groups_dict.keys()):
        fink_id = post_groups("Fink", url=url, token=token)[1]
    else:
        fink_id = groups_dict["Fink"]
    filters = get_all_filters(url=url, token=token)[1]
    filter_id = None
    if filters:
        for filter in filters:
            if filter["name"] == "fink_filter":
                filter_id = filter["id"]
                break
    if not filter_id:
        filter_id = post_filters("fink_filter", stream_id, fink_id, url, token)[1]

    return (
        fink_id,
        stream_id,
        filter_id,
    )


def class_exists_in_hierarchy(classification: str, branch: list):
    """
    Recursively look for a given class in a taxonomy hierarchy

    Arguments
    ----------
        classification : str
            Classification to look for
        branch : list
            Branch of a taxonomy hierarchy in which we look for the classification recursively

    Returns
    ----------
        exists : bool
            True if the classification is in the hierarchy, False otherwise
    """
    for tax_class in branch:
        if tax_class["class"] == classification:
            return True
        else:
            if "subclasses" in tax_class.keys():
                exists = class_exists_in_hierarchy(
                    classification, tax_class["subclasses"]
                )
                if exists is not None:
                    return exists


def get_taxonomy_id_including_classification(classification: str, url: str, token: str):
    """
    Get the taxonomy id of a classification if it exists in one of skyportal's taxonomies

    Arguments
    ----------
        classification : str
            Classification we are looking in skyportal taxonomies
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        status_code : int
            HTTP status code
        exists : bool
            True if the classification is in the hierarchy, False otherwise
    """
    # find the id of a taxonomy that includes a given classification in its hierarchy
    status, taxonomies = get_all_taxonomies(url, token)
    if status != 200:
        return status, None
    else:
        for taxonomy in taxonomies:
            exists = class_exists_in_hierarchy(classification, [taxonomy["hierarchy"]])
            if exists is not None:
                return (200, taxonomy["id"])
        return (404, None)


def from_fink_to_skyportal(
    classification: str,
    probability: float,
    object_id: str,
    mjd: float,
    instruments: list,
    filter: str,
    mag: float,
    magerr: float,
    limiting_mag: float,
    magsys: str,
    ra: float,
    dec: float,
    fink_id: int,
    filter_id: int,
    stream_id: int,
    taxonomy_id: int,
    url: str,
    token: str,
):
    """
    Post an alert to skyportal using its API, that means posting
    a candidate, the associated source, the photometry of the observation and the classification given by fink

    Arguments
    ----------
        classification : str
            Classification of for the object
        probability : float
            Given probability for the object's classification
        object_id : str
            Id of the object
        mjd : float
            MJD of the observation (Modified Julian Date)
        instruments:
            List of possible names of the instrument used to observe the object
        filter:
            Filter of the instrument used for the observation
        mag : float
            Magnitude value of the observation
        magerr : float
            Magnitude error value of the observation
        limiting_mag : float
            Limiting magnitude value of the observation
        magsys : str
            Magnitude system used for the magnitude values
        ra : float
            Right ascension of object
        dec : float
            Declination of object
        fink_id : int
            Id of the group in skyportal that contains the alerts from fink (group called Fink)
        filter_id : int
            Id of the filter in skyportal that contains the alerts from fink (filter called fink_filter)
        stream_id : int
            Id of the stream in skyportal that contains the alerts from fink (stream called fink_stream)
        url : str
            Skyportal url
        token : str
            Skyportal token

    Returns
    ----------
        None
    """
    time.sleep(1)
    overall_status = 200
    overall_status, skyportal_instruments = get_all_instruments(url=url, token=token)
    instrument_id = None
    for existing_instrument in skyportal_instruments:
        for instrument in instruments:
            if instrument.lower() in existing_instrument.lower():
                instrument_id = skyportal_instruments[existing_instrument]
                break
    if instrument_id is not None:
        status = post_source(object_id, ra, dec, [fink_id], url=url, token=token)[0]
        if status != 200:
            overall_status = status
        passed_at = Time(mjd, format="mjd").isot
        status = post_candidate(
            object_id, ra, dec, [filter_id], passed_at, url=url, token=token
        )[0]
        if status != 200:
            overall_status = status
        status = post_photometry(
            object_id,
            mjd,
            instrument_id,
            filter,
            mag,
            magerr,
            limiting_mag,
            magsys,
            ra,
            dec,
            [fink_id],
            [stream_id],
            url=url,
            token=token,
        )[0]
        if classification_exists_for_objs(object_id, url=url, token=token):
            status = update_classification(
                object_id,
                classification,
                probability,
                taxonomy_id,
                [fink_id],
                url=url,
                token=token,
            )
            if status != 200:
                overall_status = status
        else:
            status = post_classification(
                object_id,
                classification,
                probability,
                taxonomy_id,
                [fink_id],
                url=url,
                token=token,
            )[0]
            if status != 200:
                overall_status = status
        print(
            f"Candidate with source: {object_id}, classified as a {classification} added to SkyPortal"
        )
    else:
        print("error: instrument named {} does not exist".format(instrument))
    return overall_status
