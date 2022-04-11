# coding: utf-8
import os
import subprocess
import confluent_kafka
import time
import yaml

from fink_client.avroUtils import AlertReader
from fink_client.avroUtils import encode_into_avro

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

data_path = basedir + "/sample.avro"
schema_path = basedir + "/schemas/schema_test.avsc"
skyportal_dir = basedir + "/../skyportal"
pool_alerts_dir = basedir + "/../"

def test_generate_fake_alerts():
    """
    Generate fake alerts on a kafka server for testing purposes

    Parameters
    ----------
    None

    Returns
    ----------
    None
    """

    print("Stopping previous kafka and zookeeper instances:")
    cmd = subprocess.Popen(
        ["docker-compose", "down"], cwd=basedir, preexec_fn=os.setsid
    )
    cmd.communicate()[0]

    print("Starting kafka and zookeeper instances:")
    cmd = subprocess.Popen(
        ["docker-compose", "up", "-d"], cwd=basedir, preexec_fn=os.setsid
    )
    cmd.communicate()[0]

    print("Generating fake alerts:")
    r = AlertReader(data_path)
    alerts = r.to_list()
    p = confluent_kafka.Producer({"bootstrap.servers": "localhost:9093"})
    for alert in alerts[::-1]:
        avro_data = encode_into_avro(alert, schema_path)
        topic = "test_stream"
        try:
            p.produce(topic, avro_data)
        except ConnectionError:
            print("Connection Error")

    p.flush()

def test_getting_skyportal_admin_token():
    # open yaml config file
    with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml", "r"
    ) as stream:
        try:
            conf_skyportal = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    assert skyportal_token is not None
    skyportal_token = conf_skyportal["INITIAL_ADMIN"]

    with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml", "r"
    ) as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    conf["skyportal_token"] = skyportal_token

    with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml", "w"
    ) as stream:
        try:
            yaml.dump(conf, stream)
        except yaml.YAMLError as exc:
            print(exc)


