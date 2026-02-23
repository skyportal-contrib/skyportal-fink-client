# User Guide

## Setup

#### System Dependencies

SkyPortal Fink Client requires the following software to be installed on your system:

- Python 3.10 or later
- `fink-client` >= 10.0

#### Source download

Clone the skyportal-fink-client repository:

```bash
git clone https://github.com/skyportal-contrib/skyportal-fink-client.git
```

#### Python environment and dependencies

Create a virtual environment and install dependencies:

```bash
cd skyportal-fink-client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Configuration

All configuration are in `config.yaml`. Here is a full reference:

```yaml
# Survey to subscribe to: "ztf" or "lsst"
survey: lsst

# Fink broker
fink_topics:
  - fink_extragalactic_new_candidate_lsst  # LSST example
  # - fink_sn_candidates_ztf               # ZTF example
fink_username: your_fink_username
fink_password: null          # leave null if your account has no password
fink_group_id: my_unique_group_id
fink_servers: fink_url

# SkyPortal instance
skyportal_url: http://localhost:5000
skyportal_token: your_skyportal_api_token
skyportal_group: Fink

# Options
testing: false     # set to true to use a local Kafka instance with fake alerts
whitelisted: false # set to true to skip the 1-second inter-alert delay
```

#### Survey

Set `survey` to `ztf` or `lsst`. This controls how alerts are decoded and which broker server to use.

#### Fink credentials

`fink_username` and `fink_password` are your Fink broker credentials. Apply for access [here](https://forms.gle/2td4jysT4e9pkf889).

`fink_group_id` is a Kafka consumer group identifier. Choose a unique stable name per deployment (e.g. `skyportal-prod-lsst-v1`). Kafka uses this to track your position in the stream — restarting with the same group ID resumes from where you left off without reprocessing alerts.

#### Fink topics

`fink_topics` is a list of topics to subscribe to. Each topic corresponds to a Fink filter (one filter = one topic). Available topics are listed in the [Fink broker documentation](https://fink-broker.readthedocs.io/en/latest/topics/).

The classification assigned to each alert in SkyPortal is derived from the topic name (e.g. `fink_extragalactic_new_candidate_lsst` → `Extragalactic New Candidate`). For ZTF, the classification is also re-computed locally using the Fink ML classifiers embedded in each alert.

#### SkyPortal credentials

`skyportal_url` is the address of your SkyPortal instance.

`skyportal_token` is an API token from your SkyPortal user profile.

`skyportal_group` is the group that will own the ingested alerts. Users who want to see the data must be members of this group.

`whitelisted`: SkyPortal rate-limits API calls. If your IP is whitelisted in SkyPortal, set this to `true` to skip the 1-second inter-alert delay.


## Running the client

Activate the virtual environment and run:

```bash
source venv/bin/activate
make poll_alerts
```

To use a specific config file:

```bash
python __main__.py --config /path/to/config_lsst.yaml
```

Alerts are processed and pushed to SkyPortal as they arrive. Stop with `Ctrl+C`.


## Running in production (systemd)

Two service files are provided to run ZTF and LSST streams independently:

- `skyportal-fink-client-ztf.service`
- `skyportal-fink-client-lsst.service`

Each service points to its own config file via `--config`.

1. Copy and edit the service files:

```bash
sudo cp skyportal-fink-client-ztf.service /etc/systemd/system/
sudo cp skyportal-fink-client-lsst.service /etc/systemd/system/
```

Adjust `WorkingDirectory` and `ExecStart` paths in each file to match your installation.

2. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now skyportal-fink-client-ztf
sudo systemctl enable --now skyportal-fink-client-lsst
```

3. Check status and logs independently:

```bash
sudo systemctl status skyportal-fink-client-ztf
sudo journalctl -u skyportal-fink-client-ztf -f

sudo systemctl status skyportal-fink-client-lsst
sudo journalctl -u skyportal-fink-client-lsst -f
```

Because Kafka tracks offsets per `fink_group_id`, each service resumes from where it left off after a restart — no alerts are duplicated or missed (within the broker's 7-day retention window).


## Running the tests

### Additional dependencies

The test suite uses a local Kafka instance via Docker. Install Docker Engine (which includes Docker Compose v2):

```bash
sudo apt-get install docker.io
# Add yourself to the docker group (requires logout/login to take effect)
sudo usermod -aG docker $USER
```

### Running fake alerts

Set `testing: true` in `config.yaml`, then produce fake alerts:

```bash
python tests/produce_fake.py
```

This starts a local Kafka container on `localhost:9093` and publishes sample ZTF alerts to the configured topics.

### Running the client in test mode

```bash
make poll_alerts
```

### Running the test suite

```bash
pytest --disable-warnings tests/
```


## Code Documentation

### Main: skyportal_fink_client

See [Main - SkyPortal Fink Client](skyportal_fink_client.md)

### Utils: skyportal_api

See [Utils - SkyPortal API Helper](skyportal_api.md)

### Utils: files

See [Utils - Files Helper](files.md)

### Utils: switchers

See [Utils - Switchers](switchers.md)
