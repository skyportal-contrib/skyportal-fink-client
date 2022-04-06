from genericpath import exists
import requests
from astropy.time import Time
import time
import sys
import os

from itertools import chain

def api(
    method, endpoint, data=None, token=None,
):
    headers = {'Authorization': f'token {token}'}
    response = requests.request(method, endpoint, json=data, headers=headers)
    return response


def get_all_group_ids(url, token):
    groups = api("GET", f"{url}/api/groups", token=token)

    data = []
    if groups.status_code == 200:
        data = [group['id'] for group in groups.json()['data']['all_groups']]
    return groups.status_code, data


def get_group_ids_and_name(url, token):
    groups = api("GET", f"{url}/api/groups", token=token)

    data = {}
    if groups.status_code == 200:
        data = {
            group['name']: group['id']
            for group in groups.json()['data']['user_accessible_groups']
        }
    return groups.status_code, data


def get_all_instruments(url, token):
    instruments = api(
        "GET", f"{url}/api/instrument", token=token
    )

    data = {}
    if instruments.status_code == 200:
        data = {
            instrument['name']: instrument['id']
            for instrument in instruments.json()['data']
        }
    return instruments.status_code, data


def get_all_source_ids(url, token):
    sources = api(
        "GET", f"{url}/api/sources", token=token
    )

    data = []
    if sources.status_code == 200:
        data = [source['id'] for source in sources.json()['data']['sources']]
    return sources.status_code, data


def get_all_candidate_ids(url, token):
    candidates = api(
        "GET", f"{url}/api/candidates", token=token
    )

    return candidates.status_code, [
        candidate['id'] for candidate in candidates.json()['data']['candidates']
    ]


def get_all_streams(url, token):
    streams = api(
        "GET", f"{url}/api/streams", token=token
    )

    return streams.status_code, streams.json()['data']

def get_all_stream_ids(url, token):
    streams = api(
        "GET", f"{url}/api/streams", token=token
    )

    data = []
    if streams.status_code == 200:
        data = [stream['id'] for stream in streams.json()['data']]
    return streams.status_code, data

def classification_exists_for_objs(object_id, url, token):
    classifications = api(
        "GET",
        f"{url}/api/sources/classifications/{object_id}",
        token=token,
    )
    return classifications.json()['data'] != {}


def classification_id_for_objs(object_id, url, token):
    classifications = api(
        "GET",
        f"{url}/api/sources/classifications/{object_id}",
        token=token,
    )
    data = {}
    if classifications.status_code == 200:
        data = {
            'id': classifications.json()['data'][0]['id'],
            'author_id': classifications.json()['data'][0]['author_id'],
        }
    return classifications.status_code, data


def post_source(object_id, ra, dec, group_ids, url, token):
    data = {
        "ra": ra,
        "dec": dec,
        "id": object_id,
        # "ra_dis": 0,
        # "dec_dis": 0,
        # "ra_err": 0,
        # "dec_err": 0,
        # "offset": 0,
        # "redshift": 0,
        # "redshift_error": 0,
        # "altdata": null,
        # "dist_nearest_source": 0,
        # "mag_nearest_source": 0,
        # "e_mag_nearest_source": 0,
        # "transient": true,
        # "varstar": true,
        # "is_roid": true,
        # "score": 0,
        # "origin": "string",
        # "alias": null,
        # "detect_photometry_count": 0,
        "group_ids": group_ids,
    }

    response = api(
        'POST', f"{url}/api/sources", data, token=token
    )
    if response.status_code in (200, 400):
        print(f'JSON response: {response.json()}')
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else {},
    )


def post_candidate(object_id, ra, dec, filter_ids, passed_at, url, token):
    print(filter_ids)
    data = {
        "ra": ra,
        "dec": dec,
        "id": object_id,
        # "ra_dis": 0,
        # "dec_dis": 0,
        # "ra_err": 0,
        # "dec_err": 0,
        # "offset": 0,
        # "redshift": 0,
        # "redshift_error": 0,
        # "altdata": null,
        # "dist_nearest_source": 0,
        # "mag_nearest_source": 0,
        # "e_mag_nearest_source": 0,
        # "transient": true,
        # "varstar": true,
        # "is_roid": true,
        # "score": 0,
        # "origin": "string",
        # "alias": null,
        # "detect_photometry_count": 0,
        # /!\ HARDCODED FILTER ID TO ONE, ISSUES WITH IT FOR THE MOMENT
        "filter_ids": [1],
        # "passing_alert_id": 0,
        "passed_at": passed_at,
    }
    response = api(
        'POST', f"{url}/api/candidates", data, token=token
    )
    if response.status_code in (200, 400):
        print(f'JSON response: {response.json()}')
    return (
        response.status_code,
        response.json()['data']['ids'] if response.json()['data'] != {} else {},
    )


def post_photometry(
    object_id,
    mjd,
    instrument_id,
    filter,
    mag,
    magerr,
    limiting_mag,
    magsys,
    ra,
    dec,
    group_ids,
    stream_ids,
    url,
    token,
):
    data = {
        "ra": ra,
        # "ra_unc": 0,
        "magerr": magerr,
        "magsys": magsys,
        "group_ids": group_ids,
        # "altdata": None,
        "mag": mag,
        "mjd": mjd,
        # "origin": None,
        "filter": filter,
        "limiting_mag": limiting_mag,
        # "limiting_mag_nsigma": 0,
        # "dec_unc": 0,
        # "assignment_id": None,
        "stream_ids": stream_ids,
        "dec": dec,
        "instrument_id": instrument_id,
        "obj_id": object_id,
    }

    response = api(
        'POST', f"{url}/api/photometry", data, token=token
    )

    print(f'HTTP code: {response.status_code}, {response.reason}')
    return (
        response.status_code,
        response.json()['data']['ids'] if response.json()['data'] != {} else {},
    )


def post_classification(
    object_id, classification, probability, taxonomy_id, group_ids, url, token
):
    data = {
        "classification": classification,
        "taxonomy_id": taxonomy_id,
        "probability": probability,
        "obj_id": object_id,
        "group_ids": group_ids,
    }

    response = api(
        'POST',
        f"{url}/api/classification",
        data,
        token=token,
    )

    print(f'HTTP code: {response.status_code}, {response.reason}')
    return response.status_code, response.json()


def post_user(username, url, token):
    data = {
        # "first_name": first_name,
        # "last_name": last_name,
        # "contact_email": contact_email,
        # "oauth_uid": oauth_uid,
        # "contact_phone": contact_phone,
        # "roles": roles,
        # "groupIDsAndAdmin": groupIDsAndAdmin,
        "username": username
    }

    response = api(
        'POST', f"{url}/api/user", data, token=token
    )

    print(f'HTTP code: {response.status_code}, {response.reason}')
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else {},
    )


def post_streams(name, url, token):
    data = {"name": name}

    response = api(
        'POST', f"{url}/api/streams", data, token=token
    )
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else None,
    )


def post_filters(name, stream_id, group_id, url, token):
    data = {"name": name, 'stream_id': stream_id, 'group_id': group_id}

    response = api(
        'POST', f"{url}/api/filters", data, token=token
    )
    print('HAAA')
    print(response.json()['data'])
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else None,
    )


def post_telescopes(name, nickname, diameter, url, token):
    data = {"name": name, "nickname": nickname, "diameter": diameter}
    response = api(
        'POST', f"{url}/api/telescope", data, token=token
    )
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else None,
    )


def post_instruments(name, type, telescope_id, filters, url, token):
    data = {
        "name": name,
        "type": "imager",
        "filters": filters,
        "telescope_id": telescope_id,
    }
    response = api(
        'POST', f"{url}/api/instrument", data, token=token
    )
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else {},
    )


def post_fink_group(topic, url, token):
    data = {
        "name": topic,
        "group_admins": [1],
    }
    response = api(
        'POST', f"{url}/api/groups", data, token=token
    )
    print(f'HTTP code: {response.status_code}, {response.reason}, group posting')
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else None,
    )


def post_taxonomy(name, hierarchy, version, url, token):
    data = {
        "name": name,
        "hierarchy": hierarchy,
        # "group_ids": group_ids
        "version": version,
        # "provenance": provenance,
        # "isLatest": true
    }
    response = api(
        'POST', f"{url}/api/taxonomy", data, url, token=token
    )
    print(f'HTTP code: {response.status_code}, {response.reason}')
    return (
        response.status_code,
        response.json()['data']['taxonomy_id']
        if response.json()['data'] != {}
        else None,
    )


def update_classification(
    object_id, classification, probability, taxonomy_id, group_ids, url, token
):
    data_classification = classification_id_for_objs(object_id, token)[1]
    classification_id, author_id = (
        data_classification['id'],
        data_classification['author_id'],
    )

    data = {
        "obj_id": object_id,
        "classification": classification,
        "probability": probability,
        "taxonomy_id": taxonomy_id,
        "group_ids": group_ids,
        "author_id": author_id,
        "author_name": "fink_client",
    }

    response = api(
        'PUT',
        f"{url}/api/classification/" + classification_id,
        data,
        token=token,
    )
    return response.status_code

def post_filter(name, stream_id, group_id, url, token):
    data = {"name": name, 'stream_id': stream_id, 'group_id': group_id}

    response = api(
        'POST', f"{url}/api/filters", data, token=token
    )
    return (
        response.status_code,
        response.json()['data']['id'] if response.json()['data'] != {} else None,
    )

def get_all_filters(url, token):
    response = api(
        'GET', f"{url}/api/filters", token=token
    )
    return (
        response.status_code,
        response.json()['data']
    )

def get_all_taxonomies(url, token):
    response = api(
        'GET', f"{url}/api/taxonomy", token=token
    )
    return (
        response.status_code,
        response.json()['data']
    )

def init_skyportal(url, token):
    streams = get_all_streams(url, token)[1]
    # check if a stream with name 'fink_stream' exists
    stream_id = None
    if streams:
        for stream in streams:
            if stream['name'] == 'fink_stream':
                stream_id = stream['id']
                break
    if not stream_id:
        stream_id = post_streams('fink_stream', url, token)[1]
    groups_dict = get_group_ids_and_name(url=url, token=token)[1]
    fink_id = None
    if 'Fink' not in list(groups_dict.keys()):
        fink_id = post_fink_group('Fink', url=url, token=token)[1]
    else:
        fink_id = groups_dict['Fink']
    filters = get_all_filters(url=url, token=token)[1]
    filter_id = None
    if filters:
        for filter in filters:
            if filter['name'] == 'fink_filter':
                filter_id = filter['id']
                break
    print(f'filter_id: {filter_id}')
    if not filter_id:
        filter_id = post_filters('fink_filter', stream_id, fink_id, url, token)[1]
    
    return (
        stream_id,
        fink_id,
        filter_id,
    )

# recursively look for a given class in a taxonomy hierarchy
def class_exists_in_hierarchy(classification, branch, level):
    for tax_class in branch:
        if tax_class['class'] == classification:
            return True
        else: 
            if 'subclasses' in tax_class.keys():
                exists =  class_exists_in_hierarchy(classification, tax_class['subclasses'],level+1)
                if exists is not None:
                    return exists
    


def get_taxonomy_id_including_classification(classification, url, token):
    # find the id of a taxonomy that includes a given classification in its hierarchy
    taxonomies = get_all_taxonomies(url, token)[1]
    print('*************************************************************************')
    for taxonomy in taxonomies:
        exists = class_exists_in_hierarchy(classification, [taxonomy['hierarchy']],0)
        if exists is not None:
            return taxonomy['id']





def from_fink_to_skyportal(
    classification,
    probability,
    object_id,
    mjd,
    instrument,
    filter,
    mag,
    magerr,
    limiting_mag,
    magsys,
    ra,
    dec,
    fink_id,
    filter_id,
    stream_id,
    url, 
    token,
): 
    print('fink_id:', fink_id, 'filter_id:', filter_id, 'stream_id:', stream_id)
    instruments = get_all_instruments(url=url, token=token)[1]
    instrument_id = None
    for existing_instrument in instruments.keys():
        if instrument in existing_instrument.upper():
            instrument_id = instruments[existing_instrument]
    if instrument_id is not None:
        source_ids = get_all_source_ids(url=url, token=token)[1]
        if object_id not in source_ids:
            print('this source doesnt exist yet')
            post_source(object_id, ra, dec, [fink_id], url=url, token=token)
        passed_at = Time(mjd, format='mjd').isot
        post_candidate(object_id, ra, dec, [filter_id], passed_at, url=url, token=token)
        time.sleep(2)
        post_photometry(
            object_id,
            mjd,
            instrument_id,
            filter,
            mag,
            magerr,
            limiting_mag,
            magsys,
            ra,
            dec,
            [fink_id],
            [stream_id],
            url=url, 
            token=token,
        )
        # /!\ HARDCODED TAXONOMY ID TO ONE, TO IMPLEMENT A METHOD TO FIND THE RIGHT TAXONOMY ID, AND ADD ONE IF NEEDED
        taxonomy_id = get_taxonomy_id_including_classification(classification, url, token)
        if taxonomy_id is not None:
            if classification_exists_for_objs(object_id, url=url, token=token):
                update_classification(
                    object_id, classification, probability, taxonomy_id, [fink_id], url=url, token=token
                )
            else:
                print('this classification doesnt exist yet')
                print(classification, probability)
                post_classification(
                    object_id, classification, probability, taxonomy_id, [fink_id], url=url, token=token
                )
        else:
            print("error: taxonomy id not found, this classification doesn't exist in any taxonomies")
    else:
        print('error: instrument named {} does not exist'.format(instrument))
