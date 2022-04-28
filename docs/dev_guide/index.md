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

Here, if you are running the client in testing mode, you can set the `testing` field to `true`.

#### SkyPortal Credentials

The `skyportal_url` and `skyportal_token` fields are used to connect to the SkyPortal instance. The url is simply the address of the SkyPortal instance, and the token is an api token that you can create and/or find in your SkyPortal's user profile.


## Running the Tests

### Additional dependencies

To run the test suite, we'll need to emulate fink broker alerts stream. In order to do that, we'll use docker-compose and docker to run a local Kafka server.
To install it on your system, you'll need to run:

```
sudo apt-get install docker.io docker-compose
```

After which you'll need to add yourself to the docker group so you don't need to run `sudo` during the test suite (it is an important step, it won't work otherwise).

```
sudo groupadd docker
sudo usermod -aG docker $USER
```

To complete the installation, you need to either log out and log in, or reboot your machine.

Now, you are ready to go and you just need to activate the virtualenvironment in your terminal:

```
source env/bin/activate
```

And to run the tests, just run:

```
py.test --disable-warnings tests/
```

## Code Documentation

### Main : skyportal_fink_client

You can find documentation about the `skyportal_fink_client` module on the [Main : SkyPortal Fink Client](skyportal_fink_client.md)

### Utils : skyportal_api

You can find documentation about the `skyportal_api` module on the [Utils - SkyPortal API Helper](skyportal_api.md)

### Utils : files

You can find documentation about the `files` module on the [Utils - Files Helper](files.md)

### Utils : switchers

You can find documentation about the `switchers` module on the [Utils - Switchers](switchers.md)