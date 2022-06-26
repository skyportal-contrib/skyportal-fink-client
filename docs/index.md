# SkyPortal Fink Client

SkyPortal Fink Client is a tool to feed [SkyPortal](https://skyportal.io/)'s database with alerts from [Fink](https://fink-broker.org/) in real time.
It works in 2 distinct steps:

- Polling: Polling the latest alerts from Fink using [Fink Client](https://github.com/astrolabsoftware/fink-client)
- Pushing: Pushing the alerts to [SkyPortal](https://skyportal.io/)'s database using [SkyPortal's API](https://skyportal.io/docs/api/alerts/).

It is meant to run continuously in the background, and it is primary goal is to recover alerts in real time.

## What is SkyPortal?

![SkyPortal](https://skyportal.io/docs/_images/skyportal_responsive.png)

SkyPortal is a fully open-source portal to manage and collaborate on time-domain sources and events. On the backend, it has been designed to ingest and store millions of events per night from disparate discovery streams. Here, you guessed it, that stream is [Fink](https://fink-broker.org/).

The frontend allows searching by source properties, source-level summary pages, synchronous and asynchronous source-level communication, and group and user management.

## What is Fink?

![Fink](https://fink-broker.org/images/Fink_PrimaryLogo_WEB.png)

Fink is a community driven project, open to anyone, that processes time-domains alert streams and connects them with follow-up facilities and science teams. Fink broker has been selected as a community broker to process the full stream of transient alerts from the Vera C. Rubin Observatory. Since 2020, we are processing the alert stream from the Zwicky Transient Facility (ZTF).

Fink distributes alerts via Apache Kafka topics based on one or several of the alert properties (label, classification, flux, ...). Topics are created via user-defined filters (see available topics). You can connect to existing streams, and if you would like to create a new stream, follow the tutorial or raise a new issue in fink-filters describing the alert properties and thresholds of interest.

As a user, if you wish to recover said alerts from fink, you can use the [Fink Client](https://fink-broker.readthedocs.io/en/latest/). It is a simple command line tool, as well as a python library that allows you to connect to a topic and receive alerts. Here, in skyportal-fink-client, we use its python library to connect to the topic and poll the alerts, process them and then push to SkyPortal's Database.

## Quick start

First, you need to fill the configuration file `config.yaml` as instructed [here](./user_guide/index.md).

Then, you need to [install the required dependencies](./user_guide/index.md), and you are ready to start polling alerts ! In your terminal, just navigate to the root directory of `skyportal-fink-client` and run:

```
source venv/bin/activate
```

to activate the virtual environment.

Then, run:

```
make poll
```

Now, when need alerts come in, they will be processed and pushed to SkyPortal. You'll see new candidate and sources appear in SkyPortal.

To stop polling, hit `ctrl+c` on your keyboard.

For more details, see the [user guide](./user_guide/index.md) or the [developer guide](./dev_guide/index.md).
