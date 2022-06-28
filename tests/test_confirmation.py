import os
import yaml
from fink_client.avroUtils import AlertReader
import skyportal_fink_client.utils.skyportal_api as skyportal_api
import skyportal_fink_client.utils.files as files

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = basedir + "/sample.avro"

conf = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml"
)
skyportal_token = conf["skyportal_token"]

demo_data = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__)))
    + "/../skyportal/data/db_demo.yaml"
)


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

    skyportal_candidates = skyportal_api.api(
        "GET",
        f"http://localhost:5000/api/candidates?numPerPage=100",
        token=skyportal_token,
    ).json()["data"]["candidates"]
    assert (len(skyportal_candidates) - len(demo_data["candidates"])) == 1

    alerts_sources = []
    for alert in alerts:
        if alert["objectId"] not in alerts_sources:
            alerts_sources.append(alert["objectId"])
    skyportal_sources = skyportal_api.api(
        "GET",
        f"http://localhost:5000/api/sources?numPerPage=100",
        token=skyportal_token,
    ).json()["data"]["sources"]
    # in test_skyportal_fink_client.py, we only posted one alert to skyportal, here we verify that it was posted.
    assert (len(skyportal_sources) - len(demo_data["sources"])) == 1

    # fin the objectID of the alerts we posted to skyportal
    object_ids = []
    for source in skyportal_sources:
        if source["id"] in alerts_sources:
            object_ids.append(source["id"])

    # we posted only one alert so the length of object_ids should be 1
    assert len(object_ids) == 1

    # create a nested list of alerts by source, this is useful especially if during the tests you added multiple alerts to skyportal.
    # in the alerts list, keep only the alert with its obj_id in the object_ids list.
    alerts = [alert for alert in alerts if alert["objectId"] in object_ids]
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
