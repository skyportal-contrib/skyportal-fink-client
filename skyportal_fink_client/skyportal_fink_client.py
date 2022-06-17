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


def poll_alerts(
    url=None,
    token=None,
    maxtimeout: int = 5,
    log=None,
    testing=False,
    whitelisted=False,
):
    """
    Connect to and poll alerts from fink servers to post them in skyportal using its API, using a config file containing
    the necessary access credentials to both fink and skyportal, as well as a list of topics to subscribe to
    (corresponding to a classification in skyportal).

    Arguments
    ----------
        maxtimeout : int
            maximum time to wait for a message to be received from a topic
            (max interval between two polling tries)

    Returns
    ----------
        None
    """

    if log is None:
        log = make_log("fink")

    myconfig = {
        "username": conf["username"],
        "bootstrap.servers": conf["servers"],
        "group_id": conf["group_id"],
    }

    if url is None:
        url = conf["skyportal_url"]

    if token is None:
        token = conf["skyportal_token"]

    if testing is None:
        testing = conf["testing"]

    if whitelisted is None:
        whitelisted = conf["whitelisted"]

    if conf["password"] is not None:
        myconfig["password"] = conf["password"]

    # extract all topics from conf['mytopics'] and create a list of topics names
    topics = list(conf["mytopics"])
    log(f"Fink topics you subscribed to: {topics}")

    group_id, stream_id, filter_id = skyportal_api.init_skyportal(
        conf["skyportal_group"], url, token
    )

    # load taxonomy from data/taxonomy.yaml
    taxonomy_dict = files.yaml_to_dict(
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/data/taxonomy.yaml"
    )

    status, taxonomy_id, latest = skyportal_api.get_fink_taxonomy_id(
        taxonomy_dict["version"], url, token
    )
    if taxonomy_id is None or not latest:
        # post taxonomy
        status, taxonomy_id = skyportal_api.post_taxonomy(
            taxonomy_dict["name"],
            taxonomy_dict["hierarchy"],
            taxonomy_dict["version"],
            [group_id],
            url,
            token,
        )
        if status != 200:
            log("Error while posting taxonomy")
            return
        log(f"Fink Taxonomy posted with id {taxonomy_id}")
    # Instantiate a consumer, with a given schema if we are testing with fake alerts
    if testing == True:
        log("Using fake alerts for testing")
        schema = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../tests/schemas/schema_test.avsc")
        )
        consumer = AlertConsumer(topics, myconfig, schema_path=schema)
    else:
        log("Using Fink Broker")
        consumer = AlertConsumer(topics, myconfig)
    try:
        while True:
            try:
                # Poll the servers
                topic, alert, key = consumer.poll(maxtimeout)
            except Exception as e:
                log(f"Error while polling: {e}")
                continue
            # Analyse output - we just print some values for example
            if topic is not None:
                if alert is not None:
                    alert_pd = pd.DataFrame([alert])
                    alert_pd["tracklet"] = ""
                    classification = extract_fink_classification_from_pdf(alert_pd)[0]
                    log(
                        f"\nReceived alert from topic {topic} with classification {classification}"
                    )
                    object_id = alert["objectId"]
                    mjd = Time(alert["candidate"]["jd"], format="jd").mjd
                    instruments = ["CFH12k", "ZTF"]
                    filter = fid_to_filter_ztf(
                        alert["candidate"]["fid"]
                    )  # fid is filter id
                    mag = alert["candidate"]["magpsf"]  # to be verified
                    magerr = alert["candidate"]["sigmapsf"]  # to be verified
                    limiting_mag = alert["candidate"]["diffmaglim"]  # to be verified
                    magsys = "ab"  # seems like it is the good magsys
                    ra = alert["candidate"]["ra"]
                    dec = alert["candidate"]["dec"]
                    skyportal_api.from_fink_to_skyportal(
                        classification,
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
                        group_id,
                        filter_id,
                        stream_id,
                        taxonomy_id,
                        whitelisted,
                        url,
                        token,
                        log=log,
                    )
                    topic = None
                    alert = None

            else:
                log("No alerts received in the last {} seconds".format(maxtimeout))

    except KeyboardInterrupt:
        log("interrupted!")
        # Close the connection to the servers
        consumer.close()


if __name__ == "__main__":
    poll_alerts()
