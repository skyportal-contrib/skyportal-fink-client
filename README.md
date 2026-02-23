# SkyPortal Fink Client

A client that connects to the [Fink broker](https://fink-broker.org/) and forwards astronomical alerts to a [SkyPortal](https://skyportal.io/) instance.

Supports both **ZTF** and **LSST/Rubin** alert streams.

## Quick Start

```bash
git clone https://github.com/skyportal-contrib/skyportal-fink-client.git
cd skyportal-fink-client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Edit `config.yaml` with your credentials, then run:

```bash
make poll_alerts
```

## Documentation

Full documentation is available in [`docs/user_guide/index.md`](docs/user_guide/index.md), including:

- Configuration reference
- ZTF and LSST setup
- Running in production (systemd)
- Testing with fake alerts
