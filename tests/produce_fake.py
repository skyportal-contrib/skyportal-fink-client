# coding: utf-8
import os
import subprocess
import confluent_kafka

from fink_client.avroUtils import AlertReader
from fink_client.avroUtils import encode_into_avro

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = basedir + "/sample.avro"
schema_path = basedir + "/schemas/schema_test.avsc"


def produce_fake_alerts():
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


produce_fake_alerts()
