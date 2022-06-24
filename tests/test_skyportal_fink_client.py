import os
import uuid
import skyportal_fink_client.skyportal_fink_client as skyportal_fink_client
import skyportal_fink_client.utils.skyportal_api as skyportal_api
import skyportal_fink_client.utils.files as files
from skyportal_fink_client.utils.log import make_log

conf = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml"
)

schema = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "schemas/schema_test.avsc")
)


def init_test():
    skyportal_url = conf["skyportal_url"]
    skyportal_token = conf["skyportal_token"]
    fink_username = conf["fink_username"]
    fink_password = conf["fink_password"]
    fink_group_id = conf["fink_group_id"]
    fink_servers = conf["fink_servers"]
    fink_topics = conf["fink_topics"]
    testing = True
    log = make_log("test_skyportal_fink_client")
    return (
        skyportal_url,
        skyportal_token,
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        log,
    )


def test_init_skyportal():
    (
        skyportal_url,
        skyportal_token,
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        log,
    ) = init_test()
    skyportal_group = str(uuid.uuid4())
    whitelisted = False
    (
        group_id,
        stream_id,
        filter_id,
        taxonomy_id,
        skyportal_url,
        skyportal_token,
        whitelisted,
    ) = skyportal_fink_client.init_skyportal(
        skyportal_url, skyportal_token, skyportal_group, whitelisted, log
    )
    assert group_id is not None
    assert stream_id is not None
    assert filter_id is not None
    assert taxonomy_id is not None
    assert skyportal_url is not None
    assert skyportal_token is not None
    assert whitelisted is not None


def test_init_consumer():
    (
        skyportal_url,
        skyportal_token,
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        log,
    ) = init_test()
    consumer = skyportal_fink_client.init_consumer(
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        schema,
        log,
    )
    assert consumer is not None


def test_poll_alert():
    (
        skyportal_url,
        skyportal_token,
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        log,
    ) = init_test()
    consumer = skyportal_fink_client.init_consumer(
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        schema,
        log,
    )
    retries = 0
    max_retries = 30
    topic, alert = None, None
    while retries < max_retries:
        topic, alert = skyportal_fink_client.poll_alert(consumer, 5, log)
        if alert is not None and topic is not None:
            break
        else:
            retries += 1

    assert topic is not None
    assert alert is not None
    assert retries < max_retries


def test_extract_alert_data():
    (
        skyportal_url,
        skyportal_token,
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        log,
    ) = init_test()
    consumer = skyportal_fink_client.init_consumer(
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        schema,
        log,
    )
    retries = 0
    max_retries = 30
    topic, alert = None, None
    while retries < max_retries:
        topic, alert = skyportal_fink_client.poll_alert(consumer, 5, log)
        if alert is not None and topic is not None:
            break
        else:
            retries += 1

    assert topic is not None
    assert alert is not None
    assert retries < max_retries
    data = skyportal_fink_client.extract_alert_data(alert)
    assert data is not None


def test_poll_alert_and_post_to_skyportal():
    (
        skyportal_url,
        skyportal_token,
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        log,
    ) = init_test()
    skyportal_group = str(str(uuid.uuid4()))
    whitelisted = False
    (
        group_id,
        stream_id,
        filter_id,
        taxonomy_id,
        skyportal_url,
        skyportal_token,
        whitelisted,
    ) = skyportal_fink_client.init_skyportal(
        skyportal_url, skyportal_token, skyportal_group, whitelisted, log
    )
    assert group_id is not None
    assert stream_id is not None
    assert filter_id is not None
    assert taxonomy_id is not None
    assert skyportal_url is not None
    assert skyportal_token is not None
    assert whitelisted is not None
    consumer = skyportal_fink_client.init_consumer(
        fink_username,
        fink_password,
        fink_group_id,
        fink_servers,
        fink_topics,
        testing,
        schema,
        log,
    )
    assert consumer is not None
    retries = 0
    max_retries = 30
    topic, alert = None, None
    while retries < max_retries:
        topic, alert = skyportal_fink_client.poll_alert(consumer, 5, log)
        if alert is not None and topic is not None:
            break
        else:
            retries += 1

    assert topic is not None
    assert alert is not None
    assert retries < max_retries
    data = skyportal_fink_client.extract_alert_data(alert)
    assert data is not None
    status = skyportal_api.from_fink_to_skyportal(
        *data,
        group_id=group_id,
        filter_id=filter_id,
        stream_id=stream_id,
        taxonomy_id=taxonomy_id,
        whitelisted=whitelisted,
        url=skyportal_url,
        token=skyportal_token,
        log=log
    )

    assert status is not None
    assert status == 200
