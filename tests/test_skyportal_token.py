# coding: utf-8
import os
import yaml

import skyportal_fink_client.utils.files as files


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
    conf_skyportal = files.yaml_to_dict(
        os.path.abspath(os.path.join(os.path.dirname(__file__)))
        + "/../skyportal/.tokens.yaml"
    )

    skyportal_token = conf_skyportal["INITIAL_ADMIN"]
    assert skyportal_token is not None
    assert skyportal_token is not ""

    conf = files.yaml_to_dict(
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml"
    )
    conf["skyportal_token"] = skyportal_token

    files.dict_to_yaml(
        conf,
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml",
    )
