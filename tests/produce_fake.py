# coding: utf-8
import os
import subprocess
import datetime
import time
import confluent_kafka
import yaml

from fink_client.avro_utils import AlertReader
from fink_client.avro_utils import encode_into_avro

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = basedir + "/sample.avro"
schema_path = basedir + "/schemas/schema_test.avsc"
config_path = os.path.abspath(os.path.join(basedir, "../config.yaml"))


def sanitize_alert(alert: dict) -> dict:
    """Convert datetime objects to ISO strings to match avsc schema string fields."""
    sanitized = {}
    for k, v in alert.items():
        if isinstance(v, datetime.datetime):
            sanitized[k] = v.isoformat()
        elif isinstance(v, dict):
            sanitized[k] = sanitize_alert(v)
        else:
            sanitized[k] = v
    return sanitized


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
    with open(config_path) as f:
        conf = yaml.safe_load(f)
    topics = conf.get("fink_topics", ["test_stream"])

    print("Stopping previous kafka and zookeeper instances:")
    cmd = subprocess.Popen(
        ["docker", "compose", "down"], cwd=basedir, preexec_fn=os.setsid
    )
    cmd.communicate()[0]

    print("Starting kafka and zookeeper instances:")
    cmd = subprocess.Popen(
        ["docker", "compose", "up", "-d"], cwd=basedir, preexec_fn=os.setsid
    )
    cmd.communicate()[0]

    print("Waiting for Kafka to be ready...")
    time.sleep(15)

    print("Generating fake alerts:")
    r = AlertReader(data_path)
    alerts = r.to_list()
    p = confluent_kafka.Producer({"bootstrap.servers": "localhost:9093"})
    for alert in alerts[::-1]:
        alert = sanitize_alert(alert)
        avro_data = encode_into_avro(alert, schema_path)
        for topic in topics:
            try:
                p.produce(topic, avro_data)
                print(f"  Produced alert to topic: {topic}")
            except ConnectionError as e:
                print(f"Connection Error for topic {topic}: {e}")

    remaining = p.flush(30)
    if remaining > 0:
        print(f"WARNING: {remaining} messages were not delivered (broker unreachable?)")
    else:
        print(f"Done: produced {len(alerts)} alerts to topics {topics}")


produce_fake_alerts()
