# coding: utf-8

import sys
import os
import yaml
from fink_client.consumer import AlertConsumer
from fink_client.configuration import load_credentials

from astropy.time import Time

import post_fink_alerts

# open yaml config file
with open(os.path.abspath(os.path.join(os.path.dirname(__file__)))+'/../config.yaml', 'r') as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def fid_to_filter(fid):
    switcher = {1: 'ztfg', 2: 'ztfr', 3: 'ztfi'}
    return switcher.get(fid)

def topic_to_classification(topic):
    switcher = {
        'test_stream': 'kilonova',
        'early_sn_candidates': 'Supernova',
        'sn_candidates': 'Supernova',
        'early_kn_candidates': 'kilonova',
        'kn_candidates': 'kilonova',
        'ftest_sn_candidates_ztf': 'Supernova',
        'ftest_sso_ztf_candidates_ztf': 'Solar System Object',
        'ftest_sso_fink_candidates_ztf': 'Solar System Object',
    }
    return switcher.get(topic)


def topic_to_probability(topic):
    switcher = {
        'test_stream': 0.75,
        'early_sn_candidates': 0.5,
        'sn_candidates': 1,
        'early_kn_candidates': 0.5,
        'kn_candidates': 1,
        'ftest_sn_candidates_ztf': 0.75,
        'ftest_sso_ztf_candidates_ztf': 0.75,
        'ftest_sso_fink_candidates_ztf': 0.75,
    }
    return switcher.get(topic)


def poll_alerts():
    """Connect to and poll fink servers once.

    Parameters
    ----------
    myconfig: dic
        python dictionnary containing credentials
    topics: list of str
        List of string with topic names
    """

    fink_id, filter_id, stream_id = post_fink_alerts.init_skyportal(conf['skyportal_url'], conf['skyportal_token'])
    print('fink_id:', fink_id, 'filter_id:', filter_id, 'stream_id:', stream_id)

    myconfig = {
        "username": conf['username'],
        'bootstrap.servers': conf['servers'],
        'group_id': conf['group_id'],
    }

    if conf['password'] is not None:
        myconfig['password'] = conf['password']

    maxtimeout = 5
    # Instantiate a consumer, with a given schema if we are testing with fake alerts
    if conf['testing'] == True:
        print('Using fake alerts for testing')
        schema = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 'schemas/schema_test.avsc'
            )
        )
        consumer = AlertConsumer(conf['mytopics'], myconfig, schema_path=schema)
    else:
        print('Using Fink Broker')
        consumer = AlertConsumer(conf['mytopics'], myconfig)
    try:
        while True:
            
            # Poll the servers
            topic, alert, key = consumer.poll(maxtimeout)
            # Analyse output - we just print some values for example
            if topic is not None:
                if alert is not None:
                    object_id = alert['objectId']
                    mjd = Time(alert['candidate']['jd'], format='jd').mjd
                    instrument = "ZTF"
                    filter = fid_to_filter(
                        alert['candidate']['fid']
                    )  # fid is filter id
                    mag = alert['candidate']['magpsf']  # to be verified
                    magerr = alert['candidate']['sigmapsf']  # to be verified
                    limiting_mag = alert['candidate']['diffmaglim']  # to be verified
                    magsys = 'ab'  # seems like it is the good magsys
                    ra = alert['candidate']['ra']
                    dec = alert['candidate']['dec']
                    post_fink_alerts.from_fink_to_skyportal(
                        topic_to_classification(topic),
                        topic_to_probability(topic),
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
                        url=conf['skyportal_url'],
                        token=conf['skyportal_token'],
                    )
                    topic = None
                    alert = None

            else:
                print('No alerts received in the last {} seconds'.format(maxtimeout))

    except KeyboardInterrupt:
        print('interrupted!')
        # Close the connection to the servers
        consumer.close()


poll_alerts()
