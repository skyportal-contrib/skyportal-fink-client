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
fink_topics:
  - test_stream
fink_username: 'your_fink_user_name'
fink_password: 'your_fink_user_password'
fink_group_id: 'your_fink_group'
fink_servers: localhost:9093
skyportal_token: 611c1ef7-77d7-467b-bfe8-b2f9730e3914
skyportal_url: http://localhost:5000
skyportal_group: Fink
testing: true
whitelisted: false
```

#### Fink credentials

Let's start by looking at the `fink_username` and `fink_password` fields. These are the credentials used to authenticate with Fink broker. If you don't have those credentials, you can apply [HERE](https://forms.gle/2td4jysT4e9pkf889) to get them.

Simply replace `your_fink_user_name` and `your_fink_user_password` with your credentials.

Same procedure as above for the `fink_servers` and `fink_group_id` field. These are the address of the Fink broker's server and port you want to connect to, and the fink broker group that your user is in. You received those along with your credentials.

#### Fink Topics

The `fink_topics` field is a list of topics that you want to subscribe to. The topics are fink topics, to learn more about it, click [HERE](https://fink-broker.readthedocs.io/en/latest/topics/).

Each topic contains objects that have been classified, and then passed through specific filters that correspond to the topic (one fink filter = one topic of alerts).
By the way, after polling the alert, we will recreate the classification using [Fink Filters](https://github.com/astrolabsoftware/fink-filters), which will be used to classify the alert in SkyPortal.

#### Testing

This simple argument is a boolean that indicates whether you want to run the client in testing mode. This is meant for development purposes, and should be set to `false` in production (when a normal user uses it with a real instance of SkyPortal).

#### SkyPortal Credentials

The `skyportal_url` and `skyportal_token` fields are used to connect to the SkyPortal instance. The url is simply the address of the SkyPortal instance, and the token is an api token that you can create and/or find in your SkyPortal user profile.
The `skyportal_group` field is the group that you want the alerts to belong to. On SkyPortal, if a user wants to see the data you poll from Fink, he should be in this group.
The `whitelisted` field indicates if your IP address is whitelisted in SkyPortal. Indeed, SkyPortal limits how many API calls can be in "queue" at once. If you are not whitelisted and make too many API calls at once, they will be skipped. Therefore, we added a delay of 1 second between alerts. But if you are whitelisted, you can set this to `true` to skip that delay.

## Running the client

In your terminal, just navigate to the root directory of `skyportal-fink-client` and run:

```
source venv/bin/activate
```

to activate the virtual environment.

Then, run:

```
make poll
```

Now, when new alerts come in, they will be processed and pushed to SkyPortal. You'll see new candidate and sources appear in SkyPortal.

To stop polling, hit `ctrl+c` on your keyboard.
