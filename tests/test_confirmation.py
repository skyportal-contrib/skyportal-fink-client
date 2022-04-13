import os
import yaml
from unittest import result
import skyportal_api as skyportal_api
from fink_client.avroUtils import AlertReader

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = basedir + "/sample.avro"

with open(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml",
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

    skyportal_candidates = skyportal_api.api(
        "GET",
        f"http://localhost:5000/api/candidates?numPerPage=100",
        token=skyportal_token,
    ).json()["data"]["candidates"]
    print(len(skyportal_candidates) - len(demo_data["candidates"]))
    assert (len(skyportal_candidates) - len(demo_data["candidates"])) == len(alerts)

    alerts_sources = []
    for alert in alerts:
        if alert["objectId"] not in alerts_sources:
            alerts_sources.append(alert["objectId"])
    skyportal_sources = skyportal_api.api(
        "GET",
        f"http://localhost:5000/api/sources?numPerPage=100",
        token=skyportal_token,
    ).json()["data"]["sources"]
    assert (len(skyportal_sources) - len(demo_data["sources"])) == len(alerts_sources)

    print(skyportal_sources[0])

    # create a nest list of alerts by source
    alerts_by_source = {}
    for source in alerts:
        if source["objectId"] in alerts_by_source:
            alerts_by_source[source["objectId"]].append(source)
        else:
            alerts_by_source[source["objectId"]] = [source]

    for source in alerts_by_source:
        skyportal_photometries = skyportal_api.api(
            "GET",
            f"http://localhost:5000/api/sources/{source}/photometry?numPerPage=100",
            token=skyportal_token,
        ).json()["data"]
        for photometry in alerts_by_source[source]:
            # get list of mjd from skyportal_photometries
            assert round(photometry["candidate"]["ra"], 17) in [
                round(skyportal_photometry["ra"], 17)
                for skyportal_photometry in skyportal_photometries
            ]
            assert round(photometry["candidate"]["dec"], 17) in [
                round(skyportal_photometry["dec"], 17)
                for skyportal_photometry in skyportal_photometries
            ]
            assert round(photometry["candidate"]["magpsf"], 17) in [
                round(skyportal_photometry["mag"], 17)
                for skyportal_photometry in skyportal_photometries
            ]
            assert round(photometry["candidate"]["sigmapsf"], 17) in [
                round(skyportal_photometry["magerr"], 17)
                for skyportal_photometry in skyportal_photometries
            ]
            assert round(photometry["candidate"]["diffmaglim"], 17) in [
                round(skyportal_photometry["limiting_mag"], 17)
                for skyportal_photometry in skyportal_photometries
            ]
