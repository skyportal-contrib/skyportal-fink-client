# coding: utf-8
import os
import traceback

import numpy as np
import pandas as pd
from astropy.time import Time
from fink_client.consumer import AlertConsumer
from fink_filters.ztf.classification import extract_fink_classification_from_pdf

from .utils import files, skyportal_api
from .utils.log import make_log
from .utils.switchers import (
    band_to_filter_lsst,
    fid_to_filter_ztf,
)

conf = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml"
)

taxonomy_dict = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/data/taxonomy.yaml"
)

schema = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../tests/schemas/schema_test.avsc")
)

_VALID_SURVEYS = {"ztf", "lsst"}

_REQUIRED_CONFIG_FIELDS = [
    "fink_topics",
    "fink_username",
    "fink_group_id",
    "fink_servers",
    "skyportal_url",
    "skyportal_token",
    "skyportal_group",
    "testing",
    "whitelisted",
]


def validate_config(conf: dict):
    """Validate a config dict and raise ValueError with a descriptive message on failure.

    Arguments
    ----------
    conf : dict
        Config dict, typically loaded from config.yaml.

    Raises
    ----------
    ValueError
        If the config is missing required fields or contains invalid values.
    """
    missing = [f for f in _REQUIRED_CONFIG_FIELDS if f not in conf]
    if missing:
        raise ValueError(f"Missing required field(s) in config: {missing}")

    survey = conf.get("survey", "ztf")
    if survey not in _VALID_SURVEYS:
        raise ValueError(
            f"Invalid survey {survey!r} in config. Must be one of {_VALID_SURVEYS}."
        )

    topics = conf["fink_topics"]
    if not isinstance(topics, list) or len(topics) == 0:
        raise ValueError("fink_topics must be a non-empty list.")

    for field in ("skyportal_url", "skyportal_token", "fink_group_id", "fink_servers"):
        if not conf[field]:
            raise ValueError(f"{field!r} must not be empty.")


_KN_TOPICS_ZTF = {
    "fink_kn_candidates_ztf",
    "fink_early_kn_candidates_ztf",
    "fink_rate_based_kn_candidates_ztf",
}


def _topic_to_classification(topic: str) -> str:
    """Create a human-readable classification from a Fink topic name.

    Examples
    --------
    >>> _topic_to_classification("fink_sn_candidates_ztf")
    'Sn Candidates'
    >>> _topic_to_classification("fink_extragalactic_new_candidate_rubin")
    'Extragalactic New Candidate'
    """
    name = topic
    if name.startswith("fink_"):
        name = name[5:]
    for suffix in ("_ztf", "_rubin", "_lsst"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return " ".join(word.capitalize() for word in name.split("_"))


def init_skyportal(
    skyportal_url: str = None,
    skyportal_token: str = None,
    skyportal_group: str = None,
    skyportal_name: str = None,
    whitelisted: bool = None,
    log: callable = None,
):
    """
    Initializes the group, stream, filter and taxonomy needed to post alerts to Skyportal.

    Arguments
    ----------
        skyportal_url : str
            Skyportal url. Can be omitted, then the url is taken from the config file.
        skyportal_token : str
            Skyportal token. Can be omitted, then the token is taken from the config file.
        skyportal_group : str
            Name of the group in Skyportal. Can be omitted, then the group is taken from the config file.
        whitelisted : bool
            If False, we take a 1 second pause between alerts. Can be omitted, then the value is taken from the config file.
        log : function
            Log function. Can be omitted if you do not desire to log.

    Returns
    ----------
        group_id, stream_id, filter_id, taxonomy_id, skyportal_url, skyportal_token, whitelisted
    """
    if skyportal_url is None:
        skyportal_url = conf["skyportal_url"]
    if skyportal_token is None:
        skyportal_token = conf["skyportal_token"]
    if skyportal_group is None:
        skyportal_group = conf["skyportal_group"]
    if whitelisted is None:
        whitelisted = conf["whitelisted"]

    if skyportal_name is None:
        skyportal_name = conf["skyportal_name"]

    group_id, stream_id, filter_id = skyportal_api.init_skyportal_group(
        group=skyportal_group, url=skyportal_url, token=skyportal_token
    )

    status, taxonomy_id, latest = skyportal_api.get_fink_taxonomy_id(
        taxonomy_dict["version"], url=skyportal_url, token=skyportal_token
    )

    if taxonomy_id is None or not latest:
        status, taxonomy_id = skyportal_api.post_taxonomy(
            taxonomy_dict["name"],
            taxonomy_dict["hierarchy"],
            taxonomy_dict["version"],
            [group_id],
            url=skyportal_url,
            token=skyportal_token,
        )
    if status != 200:
        if log is not None:
            log("Error while posting taxonomy")
        return

    if log is not None:
        log(f"Fink Taxonomy posted with id {taxonomy_id}")
    return (
        group_id,
        stream_id,
        filter_id,
        taxonomy_id,
        skyportal_url,
        skyportal_token,
        skyportal_name,
        whitelisted,
    )


def init_consumer(
    survey: str = None,
    fink_username: str = None,
    fink_password: str = None,
    fink_group_id: str = None,
    fink_servers: str = None,
    fink_topics: list = None,
    testing: bool = None,
    schema_path: str = None,
    log: callable = None,
):
    """
    Create and return an AlertConsumer connected to the Fink broker.

    Arguments
    ----------
    survey : str
        Survey name: ``ztf`` or ``lsst``. Taken from config if omitted.
    fink_username : str
        Fink username. Taken from config if omitted.
    fink_password : str
        Fink password. Taken from config if omitted.
    fink_group_id : str
        Kafka consumer group id. Taken from config if omitted.
    fink_servers : str
        Kafka bootstrap servers. Taken from config if omitted.
    fink_topics : list
        Topics to subscribe to. Taken from config if omitted.
    testing : bool
        If True, connects to a local Kafka instance (localhost:9093).
    schema_path : str
        Path to a local avsc schema for decoding (used in testing mode).
    log : callable

    Returns
    ----------
    consumer : AlertConsumer
    """
    if survey is None:
        survey = conf.get("survey", "ztf")
    if fink_username is None:
        fink_username = conf["fink_username"]
    if fink_password is None:
        fink_password = conf["fink_password"]
    if fink_group_id is None:
        fink_group_id = conf["fink_group_id"]
    if fink_servers is None:
        fink_servers = conf["fink_servers"]
    if fink_topics is None:
        fink_topics = conf["fink_topics"]
    if testing is None:
        testing = conf["testing"]

    if testing:
        fink_servers = "localhost:9093"

    fink_config = {
        "bootstrap.servers": fink_servers,
        "group.id": fink_group_id,
    }
    if fink_username is not None:
        fink_config["username"] = fink_username
    if fink_password is not None:
        fink_config["password"] = fink_password

    if log is not None:
        auth_mode = "SASL" if fink_password is not None else "unauthenticated"
        log(f"Connecting to Fink broker at {fink_servers} ({auth_mode})")
        if testing:
            log("Using fake alerts for testing (local Kafka at localhost:9093)")
        else:
            log(f"Using live Fink Broker ({survey.upper()})")

    consumer = AlertConsumer(
        topics=fink_topics,
        config=fink_config,
        survey=survey,
        schema_path=schema_path if testing else None,
    )

    if log is not None:
        log(f"Subscribed to topics: {fink_topics}")
    return consumer


def poll_alert(consumer: AlertConsumer, maxtimeout: int, log: callable = None):
    """
    Poll the consumer once and return (topic, alert).

    Arguments
    ----------
    consumer : AlertConsumer
    maxtimeout : int
        Seconds to wait before returning None on an empty queue.
    log : callable

    Returns
    ----------
    topic : str or None
    alert : dict or None
    """
    try:
        topic, alert, key = consumer.poll(maxtimeout)
        if topic is None:
            if log is not None:
                log(f"No alerts received in the last {maxtimeout} seconds (timeout)")
            return None, None
        if alert is None:
            if log is not None:
                log(
                    f"Received message on topic {topic} (key={key!r}) "
                    "but alert could not be decoded"
                )
            return None, None
        if log is not None:
            log(f"Decoded alert from topic={topic}")
        return topic, alert
    except Exception as e:
        if log is not None:
            log(
                f"Exception during poll: {type(e).__name__}: {e}\n"
                f"{traceback.format_exc()}"
            )
        return None, None


def _extract_ztf_data(topic: str, alert: dict):
    """Extract a flat list of standardised alert fields from a ZTF alert."""
    if alert is None:
        return None
    if "objectId" not in alert or "candidate" not in alert:
        return None
    cand = alert["candidate"]
    required = ["jd", "fid", "magpsf", "sigmapsf", "diffmaglim", "ra", "dec"]
    if any(cand.get(k) is None for k in required):
        return None

    alert_pd = pd.DataFrame([alert])
    alert_pd["tracklet"] = ""
    classification = extract_fink_classification_from_pdf(alert_pd)[0]

    # Force kilonova classification for known KN topics
    if topic in _KN_TOPICS_ZTF and "kilonova" not in classification.lower():
        classification = "Kilonova candidate"

    return [
        alert["objectId"],
        Time(cand["jd"], format="jd").mjd,
        ["CFH12k", "ZTF"],
        fid_to_filter_ztf(cand["fid"]),
        cand["magpsf"],
        cand["sigmapsf"],
        cand["diffmaglim"],
        "ab",
        cand["ra"],
        cand["dec"],
        classification,
        False,  # is_flux: ZTF uses mag space
    ]


def _extract_lsst_data(topic: str, alert: dict):
    """Extract a flat list of standardised alert fields from an LSST/Rubin alert."""
    if alert is None:
        return None

    dia = alert.get("diaSource")
    if dia is None:
        return None

    required = ["midpointMjdTai", "band", "psfFlux", "psfFluxErr"]
    if any(dia.get(k) is None for k in required):
        return None
    if dia["psfFlux"] <= 0:
        return None

    diaobj = alert.get("diaObject")
    if diaobj is not None:
        object_id = str(np.int64(diaobj["diaObjectId"]))
        ra = diaobj.get("ra") or dia.get("ra")
        dec = diaobj.get("dec") or dia.get("dec")
    elif alert.get("mpc_orbits") is not None:
        object_id = alert["mpc_orbits"]["designation"]
        ra = dia.get("ra")
        dec = dia.get("dec")
    else:
        return None

    if ra is None or dec is None:
        return None

    filter_ = band_to_filter_lsst(dia["band"])
    if filter_ is None:
        return None

    # flux/fluxerr are in nJy; zp=31.4 gives AB mags (m = -2.5*log10(flux) + 31.4).
    return [
        object_id,
        dia["midpointMjdTai"],
        ["LSSTCam", "LSST"],
        filter_,
        dia["psfFlux"],  # flux in nJy
        dia["psfFluxErr"],  # fluxerr in nJy
        31.4,  # zp for nJy → AB mag
        "ab",
        ra,
        dec,
        _topic_to_classification(topic),
        True,  # is_flux: LSST uses flux space (no limiting mag available)
    ]


def extract_alert_data(survey: str, topic: str, alert: dict):
    """
    Dispatch alert data extraction to the correct survey handler.

    Arguments
    ----------
    survey : str
        ``ztf`` or ``lsst``
    topic : str
        Kafka topic the alert was received from
    alert : dict
        Raw alert dict from AlertConsumer.poll()

    Returns
    ----------
    list or None
        [object_id, mjd, instruments, filter, mag, magerr,
         limiting_mag, magsys, ra, dec, classification]
        Returns None if the alert could not be parsed.
    """
    if survey == "ztf":
        return _extract_ztf_data(topic, alert)
    elif survey == "lsst":
        return _extract_lsst_data(topic, alert)
    else:
        raise ValueError(f"Unknown survey: {survey!r}. Must be 'ztf' or 'lsst'.")


def poll_alerts(
    skyportal_url: str = None,
    skyportal_token: str = None,
    skyportal_group: str = None,
    survey: str = None,
    fink_username: str = None,
    fink_password: str = None,
    fink_group_id: str = None,
    fink_servers: str = None,
    fink_topics: list = None,
    testing: bool = None,
    whitelisted: bool = None,
    log: callable = None,
    maxtimeout: int = 5,
    config_path: str = None,
):
    """
    Connect to Fink and continuously post incoming alerts to SkyPortal.

    All arguments can be omitted; values are then read from config.yaml (or
    the file pointed to by ``config_path``).

    Arguments
    ----------
    skyportal_url : str
    skyportal_token : str
    skyportal_group : str
    survey : str
        ``ztf`` or ``lsst``
    fink_username : str
    fink_password : str
    fink_group_id : str
    fink_servers : str
    fink_topics : list
    testing : bool
        Use a local Kafka instance with fake alerts.
    whitelisted : bool
        Skip the 1-second inter-alert delay if your IP is whitelisted.
    log : callable
    maxtimeout : int
        Seconds to wait for an alert before polling again. Default 5.
    config_path : str
        Path to a config YAML file. Defaults to config.yaml in the repo root.
    """
    if log is None:
        log = make_log("fink")

    _conf = files.yaml_to_dict(config_path) if config_path else conf
    validate_config(_conf)

    if survey is None:
        survey = _conf.get("survey", "ztf")
    if skyportal_url is None:
        skyportal_url = _conf["skyportal_url"]
    if skyportal_token is None:
        skyportal_token = _conf["skyportal_token"]
    if skyportal_group is None:
        skyportal_group = _conf["skyportal_group"]
    if whitelisted is None:
        whitelisted = _conf["whitelisted"]
    if fink_username is None:
        fink_username = _conf["fink_username"]
    if fink_password is None:
        fink_password = _conf["fink_password"]
    if fink_group_id is None:
        fink_group_id = _conf["fink_group_id"]
    if fink_servers is None:
        fink_servers = _conf["fink_servers"]
    if fink_topics is None:
        fink_topics = _conf["fink_topics"]
    if testing is None:
        testing = _conf["testing"]

    (
        group_id,
        stream_id,
        filter_id,
        taxonomy_id,
        skyportal_url,
        skyportal_token,
        skyportal_name,
        whitelisted,
    ) = init_skyportal(
        skyportal_url,
        skyportal_token,
        skyportal_group,
        skyportal_name,
        whitelisted,
        log,
    )

    consumer = init_consumer(
        survey=survey,
        fink_username=fink_username,
        fink_password=fink_password,
        fink_group_id=fink_group_id,
        fink_servers=fink_servers,
        fink_topics=fink_topics,
        testing=testing,
        schema_path=schema,
        log=log,
    )

    try:
        while True:
            topic, alert = poll_alert(consumer, maxtimeout, log)
            data = extract_alert_data(survey, topic, alert)
            if data is not None:
                log(f"Received alert from topic {topic} with classification {data[10]}")
                skyportal_api.from_fink_to_skyportal(
                    *data[:11],
                    group_id=group_id,
                    filter_id=filter_id,
                    stream_id=stream_id,
                    taxonomy_id=taxonomy_id,
                    whitelisted=whitelisted,
                    url=skyportal_url,
                    token=skyportal_token,
                    skyportal_name=skyportal_name,
                    log=log,
                    is_flux=data[11],
                )
    except KeyboardInterrupt:
        log("interrupted!")
        consumer.close()


if __name__ == "__main__":
    poll_alerts()
