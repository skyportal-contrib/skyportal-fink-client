# coding: utf-8
import os
import yaml


def test_getting_skyportal_admin_token():
    """
    Test getting the skyportal admin token

    Parameters
    ----------
    None

    Returns
    ----------
    None
    """

    with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../skyportal/.tokens.yaml", "r"
    ) as stream:
        try:
            conf_skyportal = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    skyportal_token = conf_skyportal["INITIAL_ADMIN"]
    assert skyportal_token == 'blabla'
    assert skyportal_token is not None
    assert skyportal_token is not ''

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