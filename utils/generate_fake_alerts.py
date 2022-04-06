import os
import subprocess
import confluent_kafka
import pytest
import time
import yaml

from fink_client.avroUtils import AlertReader
from fink_client.avroUtils import encode_into_avro

from fink_client.consumer import AlertConsumer
from fink_client.configuration import load_credentials

from astropy.time import Time
import post_fink_alerts as post_fink_alerts

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

data_path = basedir + '/sample.avro'
schema_path = basedir + '/schemas/schema_test.avsc'

def generate_fake_alerts():

    fink_registration = [
        'fink_client_register',
        '-username',
        'test',
        '-password',
        'None',
        '-servers',
        'localhost:9093',
        '-mytopics',
        'test_stream',
        '-group_id',
        'test_group',
        '-maxtimeout',
        '10',
    ]
    test = subprocess.Popen(fink_registration, cwd=basedir, preexec_fn=os.setsid)
    test.communicate()[0]
    assert test.returncode == 0

    test = subprocess.Popen(
        ['docker-compose', 'down'], cwd=basedir, preexec_fn=os.setsid
    )
    test.communicate()[0]
    assert test.returncode == 0

    test = subprocess.Popen(
        ['docker-compose', 'up', '-d'], cwd=basedir, preexec_fn=os.setsid
    )
    test.communicate()[0]
    assert test.returncode == 0

    r = AlertReader(data_path)
    alerts = r.to_list()
    assert len(alerts) > 0
    conf = load_credentials()

    kafka_servers = conf['servers']
    
    assert (kafka_servers is not None) and (kafka_servers is not [])

    p = confluent_kafka.Producer({'bootstrap.servers': kafka_servers})

    assert isinstance(p, confluent_kafka.Producer)
    assert p is not None

    for alert in alerts[::-1]:
        avro_data = encode_into_avro(alert, schema_path)
        topic = 'test_stream'
        try:
            p.produce(topic, avro_data)
        except ConnectionError:
            pytest.fail("Connection Error")

    p.flush()


generate_fake_alerts()