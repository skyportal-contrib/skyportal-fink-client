# coding: utf-8
import os
from fink_client.consumer import AlertConsumer
from astropy.time import Time
import skyportal_fink_client.utils.skyportal_api as skyportal_api
import skyportal_fink_client.utils.files as files
from skyportal_fink_client.utils.log import make_log
from skyportal_fink_client.utils.switchers import fid_to_filter_ztf
from fink_filters.classification import extract_fink_classification_from_pdf
import pandas as pd

# open yaml config file
conf = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml"
)


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
            The url of skyportal.
        skyportal_token : str
            The token of skyportal.
        skyportal_group : str
            The group to post alerts to in skyportal.
        fink_username : str
            The username of the fink account.
        fink_password : str
            The password of the fink account.
        fink_group_id : str
            The group id of the fink account.
        fink_servers : list
            The list of fink servers to connect to.
        fink_topics : list
            The list of topics to subscribe to.
        testing : bool
            Whether to run in testing mode (using fake alerts).
        whitelisted : bool
            Whether to only post alerts from whitelisted sources.
        log : logging.Logger
            The logger to use.
        maxtimeout : int
            The maximum number of seconds to wait for a response from a server when no alerts are received.

    Returns
    ----------
        None
    """

    if log is None:
        log = make_log("fink")

    if skyportal_url is None:
        skyportal_url = conf["skyportal_url"]

    if skyportal_token is None:
        skyportal_token = conf["skyportal_token"]

    if skyportal_group is None:
        skyportal_group = conf["skyportal_group"]

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

    if whitelisted is None:
        whitelisted = conf["whitelisted"]

    myconfig = {
        "username": fink_username,
        "bootstrap.servers": fink_servers,
        "group_id": fink_group_id,
    }

    if fink_password is not None:
        myconfig["password"] = fink_password

    # extract all topics from conf['mytopics'] and create a list of topics names
    log(f"Fink topics you subscribed to: {fink_topics}")

    group_id, stream_id, filter_id = skyportal_api.init_skyportal(
        group=skyportal_group, url=skyportal_url, token=skyportal_token
    )
    assert group_id is not None
    assert stream_id is not None
    assert filter_id is not None

    # load taxonomy from data/taxonomy.yaml
    taxonomy_dict = files.yaml_to_dict(
        os.path.abspath(os.path.join(os.path.dirname(__file__)))
        + "/../skyportal_fink_client/data/taxonomy.yaml"
    )

    status, taxonomy_id, latest = skyportal_api.get_fink_taxonomy_id(
        taxonomy_dict["version"], url=skyportal_url, token=skyportal_token
    )

    assert status == 200

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

        assert status == 200
        assert taxonomy_id is not None

        if status != 200:
            log("Error while posting taxonomy")
            return
        log(f"Fink Taxonomy posted with id {taxonomy_id}")
    # Instantiate a consumer, with a given schema if we are testing with fake alerts
    assert testing == True
    if testing == True:
        log("Using fake alerts for testing")
        schema = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "/schemas/schema_test.avsc")
        )
        consumer = AlertConsumer(
            topics=fink_topics, config=myconfig, schema_path=schema
        )
    else:
        log("Using Fink Broker")
        consumer = AlertConsumer(topics=fink_topics, config=myconfig)

    failed_attempts = 0
    try:
        while True:
            if failed_attempts > 2:
                print("No more alerts to process")
                break
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
                        url=skyportal_url,
                        token=skyportal_token,
                        log=log,
                    )
                    topic = None
                    alert = None

            else:
                log("No alerts received in the last {} seconds".format(maxtimeout))
                failed_attempts += 1

    except KeyboardInterrupt:
        log("interrupted!")
        # Close the connection to the servers
        consumer.close()


def test_poll_alerts():
    """
    Test the poll_alerts function.
    """
    poll_alerts(
        skyportal_url="http://localhost:5000",
        fink_username="testuser",
        fink_password=None,
        fink_group_id="test_group",
        fink_servers="localhost:9093",
        fink_topics=["test_stream"],
        testing=True,
        whitelisted=False,
    )
