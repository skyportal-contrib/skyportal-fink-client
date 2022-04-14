# coding: utf-8
from cgi import test
import os
import yaml
from fink_client.consumer import AlertConsumer
from astropy.time import Time

import skyportal_fink_client.utils.skyportal_api as skyportal_api

# open yaml config file
with open(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml", "r"
) as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def fid_to_filter(fid: int):
    """
    Convert a fid to a filter name.
    In the alert data from Fink, the fid corresponds to the 3 different filters used by the ZTF telescope.

    Parameters
    ----------
    fid: int
        id of a filter in an alert

    Returns
    ----------
    filter: str
        name of the filter
    """
    switcher = {1: "ztfg", 2: "ztfr", 3: "ztfi"}
    return switcher.get(fid)


def test_poll_alerts():
    """
    Connect to and poll alerts from fink servers to post them in skyportal using its API, using a config file containing
    the necessary access credentials to both fink and skyportal, as well as a list of topics to subscribe to
    (corresponding to a classification in skyportal).

    Parameters
    ----------
    None

    Returns
    ----------
    None
    """
    assert conf["skyportal_token"] is not None
    myconfig = {
        "username": conf["username"],
        "bootstrap.servers": conf["servers"],
        "group_id": conf["group_id"],
    }

    if conf["password"] is not None:
        myconfig["password"] = conf["password"]

    # extract all topics from conf['mytopics'] and create a list of topics names
    topics = list(conf["mytopics"].keys())
    print(f"Fink topics you subscribed to: {topics}")
    print("adding alerts")
    taxonomy_ids = {}
    for topic in topics:
        status, taxonomy_id = skyportal_api.get_taxonomy_id_including_classification(
            conf["mytopics"][topic]["classification"],
            conf["skyportal_url"],
            conf["skyportal_token"],
        )
        assert status == 200
        if status != 401:
            if taxonomy_id is not None:
                taxonomy_ids[topic] = taxonomy_id
            else:
                return print(
                    "Classification not found in taxonomy:",
                    conf["mytopics"][topic]["classification"],
                )
        else:
            return print("Skyportal token not valid")

    fink_id, stream_id, filter_id = skyportal_api.init_skyportal(
        conf["skyportal_url"], conf["skyportal_token"]
    )

    assert fink_id is not None
    assert stream_id is not None
    assert filter_id is not None
    failed_attempts = 0
    maxtimeout = 5
    # Instantiate a consumer, with a given schema if we are testing with fake alerts
    if conf["testing"] == True:
        print("Using fake alerts for testing")
        schema = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "schemas/schema_test.avsc")
        )
        print(f"Schema used: {schema}")
        consumer = AlertConsumer(topics, myconfig, schema_path=schema)
    else:
        print("Using Fink Broker")
        consumer = AlertConsumer(topics, myconfig)
    try:
        while True:
            if failed_attempts > 2:
                print("No more alerts to process")
                break
            # Poll the servers
            topic, alert, key = consumer.poll(maxtimeout)
            # Analyse output - we just print some values for example
            if topic is not None:
                if alert is not None:
                    object_id = alert["objectId"]
                    mjd = Time(alert["candidate"]["jd"], format="jd").mjd
                    instrument = "ZTF"
                    filter = fid_to_filter(
                        alert["candidate"]["fid"]
                    )  # fid is filter id
                    mag = alert["candidate"]["magpsf"]  # to be verified
                    magerr = alert["candidate"]["sigmapsf"]  # to be verified
                    limiting_mag = alert["candidate"]["diffmaglim"]  # to be verified
                    magsys = "ab"  # seems like it is the good magsys
                    ra = alert["candidate"]["ra"]
                    dec = alert["candidate"]["dec"]
                    status = skyportal_api.from_fink_to_skyportal(
                        conf["mytopics"][topic]["classification"],
                        conf["mytopics"][topic]["probability"],
                        object_id,
                        mjd,
                        instrument,
                        filter,
                        mag,
                        magerr,
                        limiting_mag,
                        magsys,
                        ra,
                        dec,
                        fink_id,
                        filter_id,
                        stream_id,
                        taxonomy_ids[topic],
                        url=conf["skyportal_url"],
                        token=conf["skyportal_token"],
                    )
                    topic = None
                    alert = None

            else:
                print("No alerts received in the last {} seconds".format(maxtimeout))
                failed_attempts += 1

    except KeyboardInterrupt:
        print("interrupted!")
        # Close the connection to the servers
        consumer.close()
