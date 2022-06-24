import os
import skyportal_fink_client.utils.skyportal_api as skyportal_api
import skyportal_fink_client.utils.files as files
from skyportal_fink_client.utils.log import make_log

conf = files.yaml_to_dict(
    os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/../config.yaml"
)

skyportal_token = conf["skyportal_token"]


def test_get_all_groups_id():
    status, data = skyportal_api.get_all_group_ids(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_get_group_ids_and_name():
    status, data = skyportal_api.get_group_ids_and_name(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_get_all_instruments():
    status, data = skyportal_api.get_all_instruments(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_get_all_source_ids():
    status, data = skyportal_api.get_all_source_ids(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_get_all_candidate_ids():
    status, data = skyportal_api.get_all_candidate_ids(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_get_all_streams():
    status, data = skyportal_api.get_all_streams(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_get_all_stream_ids():
    status, data = skyportal_api.get_all_stream_ids(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_classification_exists_for_objs():
    result = skyportal_api.classification_exists_for_objs(
        "ZTF18aabcvnq", "http://localhost:5000", skyportal_token
    )
    assert result is not None
    assert result == True


def test_classification_id_for_objs():
    status, data = skyportal_api.classification_id_for_objs(
        "ZTF18aabcvnq", "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_post_source():
    status, data = skyportal_api.post_source(
        "ZTFtestAPI",
        5,
        5,
        [1],
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_candidate():
    status, data = skyportal_api.post_candidate(
        "ZTFtestAPI",
        5,
        5,
        [1],
        "2022-04-11 06:27:01.728",
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_photometry():
    status, data = skyportal_api.post_photometry(
        "ZTF21aaqjmps",
        59580.0,
        1,
        "ztfr",
        19.0,
        0.1,
        21.0,
        "ab",
        5,
        5,
        [1],
        [1],
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_classification():
    status, data = skyportal_api.post_classification(
        "ZTF21aaqjmps",
        "kilonova",
        1,
        [1],
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_streams():
    status, data = skyportal_api.post_streams(
        "StreamTestAPI",
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


# def test_post_stream_access_to_group():
#     # post a group
#     status, group_id = skyportal_api.post_groups(
#         "StreamAccessTestGroup",
#         "http://localhost:5000",
#         skyportal_token,
#     )
#     assert status == 200
#     assert group_id is not None
#     status, stream_id = skyportal_api.post_streams(
#         "StreamTestAccessedByGroup",
#         "http://localhost:5000",
#         skyportal_token,
#     )
#     assert status == 200
#     assert stream_id is not None
#     status = skyportal_api.post_stream_access_to_group(
#         stream_id,
#         group_id,
#         "http://localhost:5000",
#         skyportal_token,
#     )
#     assert status == 200


def test_post_filters():
    status, data = skyportal_api.post_filters(
        "FilterTestAPI",
        1,
        1,
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_telescopes():
    status, data = skyportal_api.post_telescopes(
        "TelescopeTestAPI",
        "TTAPI",
        20.0,
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_instruments():
    status, data = skyportal_api.post_instruments(
        "InstrumentTestAPI",
        "imager",
        1,
        ["ztfr", "ztfg", "ztfi"],
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_groups():
    status, data = skyportal_api.post_groups(
        "GroupTestAPI",
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_post_taxonomy():
    hierarchy = {"class": "classificationTestAPI"}
    status, data = skyportal_api.post_taxonomy(
        "TaxonomyTestAPI",
        hierarchy,
        "1",
        None,
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert data is not None


def test_update_classification():
    status = skyportal_api.update_classification(
        "ZTF18aabcvnq",
        "kilonova",
        1,
        [1],
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200


def test_get_all_filters():
    status, data = skyportal_api.get_all_filters(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_get_all_taxonomies():
    status, data = skyportal_api.get_all_taxonomies(
        "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert data is not None


def test_class_exists_in_fink_taxonomy_hierarchy():
    classification_name, exists = skyportal_api.class_exists_in_fink_taxonomy_hierarchy(
        "Test",
        [{"class": "Fink Tax Test", "subclasses": [{"class": "(SIMBAD) Test"}]}],
    )
    assert classification_name is not None
    assert exists == True


def test_get_classification_in_fink_taxonomy():
    hierarchy = {"class": "Fink Tax Test", "subclasses": [{"class": "(SIMBAD) Test"}]}
    status, taxonomy_id = skyportal_api.post_taxonomy(
        "FinkTaxonomyTestAPI",
        hierarchy,
        "1",
        None,
        "http://localhost:5000",
        skyportal_token,
    )
    assert status == 200
    assert taxonomy_id is not None

    classification = skyportal_api.get_classification_in_fink_taxonomy(
        "Test", taxonomy_id, "http://localhost:5000", skyportal_token
    )
    assert classification is not None


def test_get_fink_taxonomy_id():
    hierarchy = {"class": "Fink Tax Test", "subclasses": [{"class": "(SIMBAD) Test"}]}
    status = skyportal_api.post_taxonomy(
        "Fink Taxonomy",
        hierarchy,
        "1.0",
        None,
        "http://localhost:5000",
        skyportal_token,
    )[0]
    assert status == 200
    status, id, latest = skyportal_api.get_fink_taxonomy_id(
        "1.0", "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert latest == True
    assert id is not None

    status, id, latest = skyportal_api.get_fink_taxonomy_id(
        "2.0", "http://localhost:5000", skyportal_token
    )
    assert status == 200
    assert latest == False
    assert id is not None


def test_init_skyportal_group():
    result = skyportal_api.init_skyportal_group(
        "TestInitSkyPortalGroup", "http://localhost:5000", skyportal_token
    )
    assert result is not None
    assert result[0] is not None
    assert result[1] is not None
    assert result[2] is not None


def test_from_fink_to_skyportal():

    log = make_log("fink_test")

    group_id, stream_id, filter_id = skyportal_api.init_skyportal_group(
        "fink", "http://localhost:5000", skyportal_token
    )
    assert group_id is not None
    assert stream_id is not None
    assert filter_id is not None
    taxonomy_dict = files.yaml_to_dict(
        os.path.abspath(os.path.join(os.path.dirname(__file__)))
        + "/../skyportal_fink_client/data/taxonomy.yaml"
    )
    assert taxonomy_dict is not None
    status, taxonomy_id = skyportal_api.post_taxonomy(
        taxonomy_dict["name"],
        taxonomy_dict["hierarchy"],
        taxonomy_dict["version"],
        [group_id],
        conf["skyportal_url"],
        conf["skyportal_token"],
    )
    assert status == 200
    result = skyportal_api.from_fink_to_skyportal(
        "ZTFAPITESTFINAL",
        59000.0,
        "ZTF",
        "ztfr",
        17,
        0.1,
        21,
        "ab",
        5.0,
        5.0,
        "kilonova",
        group_id,
        filter_id,
        stream_id,
        taxonomy_id,
        False,
        "http://localhost:5000",
        skyportal_token,
        log,
    )

    assert result is not None
    assert result == 200
