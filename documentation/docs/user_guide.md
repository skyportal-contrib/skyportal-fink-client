# User Guide

## Setup

#### System Dependencies

SkyPortal Fink Client requires the following software to be installed on your system:

- Python 3.8 or later

#### Source download

Clone the skyportal-fink-client repository and start a new virtual environment:

```
git clone https://github.com/skyportal-contrib/skyportal-fink-client.git
```

(You can also use `conda` or `pipenv` to create your environment.)

#### Python environment and dependencies

Lets install the dependencies required in a python virtual environment:

```
cd skyportal-fink-client
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```


## Configuration

Now that the dependencies are installed, the last step before using the client is to configure it. In order to do this, we'll guide you on what to edit in the `config.yaml` configuration file.

#### Overview

Here's a quick overview of the configuration file:

```
username: 'fink_user_name'
password: 'fink_user_password'
group_id: 'your_fink_group'
servers: localhost:9093
mytopics:
  test_stream:
    classification: kilonova
    probability: 0.75
testing: false
skyportal_url: http://localhost:5000
skyportal_token: 9d2530a0-a3dc-446b-9cf9-968736699e5a
```

#### Fink credentials

Let's start by looking at the `username` and `password` fields. These are the credentials used to authenticate with Fink broker. If you don't have those credentials, you can apply [HERE](https://forms.gle/2td4jysT4e9pkf889) to get them.

You can simply replace the `fink_user_name` and `fink_user_password` with your credentials.

Same procedure as above for the `servers` and `group_id` field. These are the address of the Fink broker's server and port you want to connect to, and the fink broker group that your user is in. You received those along with your credentials.

#### Fink Topics and classification

The `mytopics` field is a list of topics that you want to subscribe to. For each topic, you can specify a classification and a probability. The classification is used when adding the alert to SkyPortal, as well as the probability.
Example: you poll an alert coming from the `fink_test_stream` topic, and you want to add it to SkyPortal classified as a `kilonova` event with a `0.75` probability.

#### Testing

This simple argument is a boolean that indicates whether you want to run the client in testing mode. This is meant for development purposes, and should be set to `false` in production (when a normal user uses it with a real instance of SkyPortal).

#### SkyPortal Credentials

The `skyportal_url` and `skyportal_token` fields are used to connect to the SkyPortal instance. The url is simply the address of the SkyPortal instance, and the token is an api token that you can create and/or find in your SkyPortal's user profile.
