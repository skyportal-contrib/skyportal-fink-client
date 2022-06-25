# coding: utf-8
import os
from fink_client.consumer import AlertConsumer
from astropy.time import Time
from fink_filters.classification import extract_fink_classification_from_pdf

from .utils import skyportal_api
from .utils import files
from .utils.switchers import fid_to_filter_ztf
from .utils.log import make_log

import pandas as pd

# open yaml config file
conf = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml"
)

taxonomy_dict = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/data/taxonomy.yaml"
)

schema = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "/../tests/schemas/schema_test.avsc")
)


def init_skyportal(skyportal_url=None, skyportal_token=None, skyportal_group=None, whitelisted=None, log=None):
    """
    Parameters
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
    group_id : int
        ID of the group in Skyportal that we post to
    stream_id : int
        ID of the stream in Skyportal that we post to
    filter_id : int
        ID of the filter in Skyportal that we post to
    taxonomy_id : int
        ID of the fink taxonomy we posted in SkyPortal. This is used to classify the alerts
    skyportal_url : str
        Skyportal url
    skyportal_token : str
        Skyportal token
    whitelisted : bool
        If False, we take a 1 second pause between alerts
    """
    if skyportal_url is None:
        skyportal_url = conf["skyportal_url"]

    if skyportal_token is None:
        skyportal_token = conf["skyportal_token"]

    if skyportal_group is None:
        skyportal_group = conf["skyportal_group"]

    if whitelisted is None:
        whitelisted = conf["whitelisted"]

    group_id, stream_id, filter_id = skyportal_api.init_skyportal_group(
        group=skyportal_group, url=skyportal_url, token=skyportal_token
    )

    status, taxonomy_id, latest = skyportal_api.get_fink_taxonomy_id(
        taxonomy_dict["version"], url=skyportal_url, token=skyportal_token
    )

    if taxonomy_id is None or not latest:
        # post taxonomy
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
        whitelisted,
    )


def init_consumer(
    fink_username=None,
    fink_password=None,
    fink_group_id=None,
    fink_servers=None,
    fink_topics=None,
    testing=None,
    schema=None,
    log=None,
):
    """
    Parameters
    ----------
    fink_username : str
        Fink username. Can be omitted, then the username is taken from the config file.
    fink_password : str
        Fink password. Can be omitted, then the password is taken from the config file.
    fink_group_id : int
        Fink group id. Can be omitted, then the group id is taken from the config file.
    fink_servers : list
        Fink servers. Can be omitted, then the servers are taken from the config file.
    fink_topics : list
        Fink topics. Can be omitted, then the topics are taken from the config file.
    testing : bool
        If True, we use the testing servers. Can be omitted, then the value is taken from the config file.
    schema : str
        Schema file. Can be omitted, then the schema is taken from the config file.
    log : function
        Log function. Can be omitted if you do not desire to log.

    Returns
    ----------
    consumer : AlertConsumer
        AlertConsumer object
    """
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

    fink_config = {
        "username": fink_username,
        "bootstrap.servers": fink_servers,
        "group_id": fink_group_id,
    }

    if fink_password is not None:
        fink_config["password"] = fink_password

    if testing == True:
        if log is not None:
            log("Using fake alerts for testing")
        consumer = AlertConsumer(
            topics=fink_topics, config=fink_config, schema_path=schema
        )
    else:
        if log is not None:
            log("Using Fink Broker")
        consumer = AlertConsumer(topics=fink_topics, config=fink_config)
    if log is not None:
        log(f"Fink topics you subscribed to: {fink_topics}")
    return consumer


def poll_alert(consumer, maxtimeout, log):
    try:
        # Poll the servers
        topic, alert, key = consumer.poll(maxtimeout)
        if topic is None or alert is None:
            if log is not None:
                log("No alerts received in the last {} seconds".format(maxtimeout))
            return None, None
        else:
            return topic, alert
    except Exception as e:
        if log is not None:
            log(f"Error while polling: {e}")
        return None, None


def extract_alert_data(alert):
    """
    Extracts the data from the alert.
    
    Parameters
    ----------
    alert : dict
        Alert from Fink
        
    Returns
    ----------
    data : dict
        Data from the alert we need to post to Skyportal
    """
    if alert is None:
        return None
    if "objectId" not in alert.keys():
        return
    if not "candidate" in alert.keys():
        return None
    if any(
        key not in alert["candidate"].keys()
        for key in ["jd", "fid", "magpsf", "sigmapsf", "diffmaglim", "ra", "dec"]
    ):
        return None
    alert_pd = pd.DataFrame([alert])
    alert_pd["tracklet"] = ""
    classification = extract_fink_classification_from_pdf(alert_pd)[0]
    instruments = ["CFH12k", "ZTF"]
    magsys = "ab"
    object_id = alert["objectId"]
    mjd = Time(alert["candidate"]["jd"], format="jd").mjd
    filter = fid_to_filter_ztf(alert["candidate"]["fid"])
    mag = alert["candidate"]["magpsf"]
    magerr = alert["candidate"]["sigmapsf"]
    limiting_mag = alert["candidate"]["diffmaglim"]
    ra = alert["candidate"]["ra"]
    dec = alert["candidate"]["dec"]
    return [
        object_id,
        mjd,
        instruments,
        filter,
        mag,
        magerr,
        limiting_mag,
        magsys,
        ra,
        dec,
        classification,
    ]


def poll_alerts(
    skyportal_url=None,
    skyportal_token=None,
    skyportal_group=None,
    fink_username=None,
    fink_password=None,
    fink_group_id=None,
    fink_servers=None,
    fink_topics=None,
    testing=False,
    whitelisted=False,
    log=None,
    maxtimeout: int = 5,
):
    """
    Connect to and poll alerts from fink servers to post them in skyportal using its API, using a config file containing
    the necessary access credentials to both fink and skyportal, as well as a list of topics to subscribe to
    (corresponding to a classification in skyportal).

    Arguments
    ----------
        skyportal_url : str
            The url of skyportal. Can be omitted, then the url is taken from the config file.
        skyportal_token : str
            The token of skyportal. Can be omitted, then the token is taken from the config file.
        skyportal_group : str
            The group to post alerts to in skyportal. Can be omitted, then the group is taken from the config file.
        fink_username : str
            The username of the fink account. Can be omitted, then the username is taken from the config file.
        fink_password : str
            The password of the fink account. Can be omitted, then the password is taken from the config file.
        fink_group_id : str
            The group id of the fink account. Can be omitted, then the group id is taken from the config file.
        fink_servers : list
            The list of fink servers to connect to. Can be omitted, then the servers are taken from the config file.
        fink_topics : list
            The list of topics to subscribe to. Can be omitted, then the topics are taken from the config file.
        testing : bool
            Whether to run in testing mode (using fake alerts). Can be omitted, then the value is taken from the config file.
        whitelisted : bool
            Whether to only post alerts from whitelisted sources. Can be omitted, then the value is taken from the config file.
        log : logging.Logger
            The logger to use. Can be omitted, then we create a new logger.
        maxtimeout : int
            The maximum number of seconds to wait for a response from a server when no alerts are received. Defaults to 5 seconds.

    Returns
    ----------
        None
    """

    if log is None:
        log = make_log("fink")

    (
        group_id,
        stream_id,
        filter_id,
        taxonomy_id,
        skyportal_url,
        skyportal_token,
        whitelisted,
    ) = init_skyportal(
        skyportal_url, skyportal_token, skyportal_group, whitelisted, log
    )
    consumer = init_consumer(
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        log,
    )
    try:
        while True:
            topic, alert = poll_alert(consumer, maxtimeout, log)
            data = extract_alert_data(alert)
            if data is not None:
                log(f"Received alert from topic {topic} with classification {data[-1]}")
                skyportal_api.from_fink_to_skyportal(
                    *data,
                    group_id=group_id,
                    filter_id=filter_id,
                    stream_id=stream_id,
                    taxonomy_id=taxonomy_id,
                    whitelisted=whitelisted,
                    url=skyportal_url,
                    token=skyportal_token,
                    log=log,
                )

    except KeyboardInterrupt:
        log("interrupted!")
        consumer.close()


if __name__ == "__main__":
    poll_alerts()
