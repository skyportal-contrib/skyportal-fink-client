import skyportal_api as skyportal_api
import yaml
import os

with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../skyportal/.tokens.yaml", "r"
    ) as stream:
        try:
            conf_skyportal = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

skyportal_token = conf_skyportal["INITIAL_ADMIN"]

def test_get_all_groups_id():
    status, data = skyportal_api.get_all_group_ids('http://localhost:5000', skyportal_token)
    assert status == 200
    assert data is not None

