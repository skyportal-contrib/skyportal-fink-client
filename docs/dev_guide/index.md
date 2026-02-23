# Developer Guide

## Architecture

The client is structured around three stages:

```
Fink Kafka broker
       │
       ▼
  init_consumer()       ← creates an AlertConsumer (fink-client ≥ 10.0)
       │
       ▼
  poll_alert()          ← polls one message, returns (topic, alert)
       │
       ▼
  extract_alert_data()  ← dispatches to survey-specific extractor
  ├── _extract_ztf_data()
  └── _extract_lsst_data()
       │
       ▼
  skyportal_api.from_fink_to_skyportal()
       │
       ▼
  SkyPortal instance
```

The entry point is `poll_alerts()` in `skyportal_fink_client/skyportal_fink_client.py`, which ties everything together in a loop. It accepts an optional `config_path` argument to load a specific config file, enabling multiple instances to run simultaneously with different configs (e.g. one for ZTF, one for LSST).

## Module overview

### `skyportal_fink_client`

The main module. Key functions:

| Function | Role |
|---|---|
| `poll_alerts()` | Main loop. Reads config (via optional `config_path`), initialises SkyPortal and the consumer, then polls forever. |
| `init_skyportal()` | Creates the group/stream/filter in SkyPortal and uploads the Fink taxonomy. |
| `init_consumer()` | Builds and returns a fink-client `AlertConsumer`. |
| `poll_alert()` | Polls one alert from Kafka. Returns `(topic, alert)` or `(None, None)` on timeout/error. |
| `extract_alert_data()` | Dispatches to `_extract_ztf_data` or `_extract_lsst_data` based on `survey`. |
| `_extract_ztf_data()` | Parses a ZTF alert dict into a flat list of standardised fields. Uses `fink-filters` ML classifier. |
| `_extract_lsst_data()` | Parses an LSST/Rubin alert dict into the same format. |
| `_topic_to_classification()` | Converts a Kafka topic name to a human-readable classification string. |

### `utils/skyportal_api`

Handles all HTTP calls to SkyPortal (create candidate, add photometry, post taxonomy, etc.).

See [Utils - SkyPortal API Helper](skyportal_api.md).

### `utils/switchers`

Pure conversion functions with no side effects:

| Function | Role |
|---|---|
| `fid_to_filter_ztf(fid)` | ZTF filter id (1/2/3) → filter name (`ztfg`/`ztfr`/`ztfi`) |
| `band_to_filter_lsst(band)` | LSST band letter → SkyPortal filter name (`lsstu` … `lssty`) |
| `flux_to_mag(flux_nJy)` | Flux in nJy → AB magnitude |
| `flux_err_to_mag_err(flux, flux_err)` | Flux + flux error → magnitude error |

See [Utils - Switchers](switchers.md).

### `utils/files`

Helpers for reading YAML files and resolving paths. See [Utils - Files Helper](files.md).

## Adding a new survey

1. Add a new `_extract_<survey>_data(topic, alert)` function in `skyportal_fink_client.py` that returns:
   ```python
   [object_id, mjd, instruments, filter_, mag, magerr, limiting_mag, magsys, ra, dec, classification]
   ```
2. Add the survey branch in `extract_alert_data()`.
3. Add any needed filter-name converters in `utils/switchers.py`.
4. Add the corresponding classifications to `skyportal_fink_client/data/taxonomy.yaml` and bump the version.
5. Update `_topic_to_classification()` if the topic suffix convention differs.

## Adding new LSST classifications

Classifications are derived from topic names via `_topic_to_classification()`. To support a new topic:

1. Check what the function produces for that topic:
   ```python
   _topic_to_classification("fink_my_new_topic_lsst")  # → "My New Topic"
   ```
2. Add the matching class to `skyportal_fink_client/data/taxonomy.yaml` under `Fink LSST classifiers`.
3. Bump the taxonomy `version` field — SkyPortal will re-upload it automatically on next start.

## Testing

Set `testing: true` in `config.yaml`. This overrides the broker address to `localhost:9093`.

Produce fake ZTF alerts:
```bash
python tests/produce_fake.py
```

This starts a Docker Compose Kafka stack and publishes sample alerts to the topics listed in `config.yaml`. Requires Docker Engine with the Compose v2 plugin:
```bash
sudo apt-get install docker.io
sudo usermod -aG docker $USER  # then log out/in
```

Run the client against the fake stream:
```bash
make poll_alerts
```