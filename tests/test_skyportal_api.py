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

def test_get_all_groups_id(super_admin_token):
    status, data = skyportal_api.get_all_group_ids('localhost:5000', super_admin_token)
    assert status == 200
    assert data is not None

