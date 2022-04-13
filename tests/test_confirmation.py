import os
import yaml
from unittest import result
import skyportal_api as skyportal_api
from fink_client.avroUtils import AlertReader

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = basedir + "/sample.avro"

with open(
    os.path.abspath(os.path.join(os.path.dirname(__file__)))
    + "/../config.yaml",
    "r",
) as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

skyportal_token = conf["skyportal_token"]

with open(
    os.path.abspath(os.path.join(os.path.dirname(__file__)))
    + "/../skyportal/data/db_demo.yaml",
    "r",
) as stream:
    try:
        demo_data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def test_verify_pooling():
    """
    Parameters
    ----------
    None

    Returns
    ----------
    None
    """

    r = AlertReader(data_path)
    alerts = r.to_list()
    print(len(alerts))
    print(alerts[0].keys())
    
    skyportal_candidates = skyportal_api.api("GET", f"http://localhost:5000/api/candidates", token=skyportal_token).json()["data"]["candidates"]
    assert (len(skyportal_candidates)-len(demo_data['candidates'])) == len(alerts)

    alerts_sources = []
    for alert in alerts:
        if alert['objectId'] not in alerts_sources:
            alerts_sources.append(alert['objectId'])
    skyportal_sources = skyportal_api.api("GET", f"http://localhost:5000/api/sources", token=skyportal_token).json()["data"]["sources"]

    assert (len(skyportal_sources)-len(demo_data['sources'])) == len(alerts_sources)

    print(skyportal_sources[0])

    # create a nest list of alerts by source
    alerts_by_source = {}
    for source in alerts:
        if source['objectId'] in alerts_by_source:
            alerts_by_source[source['objectId']].append(source)
        else:
            alerts_by_source[source['objectId']] = [source]
    
    print(len(alerts_by_source))
    print(alerts_by_source[alerts_sources[0]][0]['objectId'])

    for source in alerts_by_source:
        print()


test_verify_pooling()