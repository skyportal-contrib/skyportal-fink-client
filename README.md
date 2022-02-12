# example-skyportal-client

Example SkyPortal client that uses the Skyportal API. We provide an example dev environment here to allow rapid iteration against a (locally) running instance of SkyPortal. This is done using docker-compose to bring up SkyPortal and an ephemeral database container.

### Development Precursors

1. Install dev requirements

```bash
pip install -r requirements-dev.txt
```

2. Get the linters up and running

```bash
make lint-install
pre-commit install -c skyportal/.pre-commit-config.yaml 
```

3. To get started, be sure to shut down postgres unless it's listening on a different port than SP/baselayer expects. On a mac:

```bash
brew services stop postgresql
```

On other systems you should be able to bring down PG via:

```bash
pg_ctl -D /usr/local/var/postgres stop
```

### Development

Now, in the top-level client directory:

```bash
make dev
```

This will build docker containers with the pinned version of skyportal and write the initial admin token to `./.tokens.yaml`.

If you want to get a terminal in the running docker container:

```bash
docker exec -it skyportal_web_1 bash
```

To load the demo data:

```bash
make dev-demo-data-load
```

You can use this in your client code to connect to SP on port 9000 (by default) using the SP APIs (https://skyportal.io/docs/api.html).

```python
import requests
from yaml import load, Loader

auth_data = load(open("./.tokens.yaml", "r"), Loader=Loader)
token = auth_data.get('INITIAL_ADMIN')

compose_data = load(open("skyportal/docker-compose.yaml", "r"), Loader=Loader)
port = compose_data["services"]["web"]["ports"][0].split(":")[0]

URL = "http://localhost"

def api(method, endpoint, data=None):
    headers = {'Authorization': f'token {token}'}
    response = requests.request(method, endpoint, json=data, headers=headers)
    return response

response = api('GET', f'{URL}:{port}/api/sysinfo')

print(f'HTTP code: {response.status_code}, {response.reason}')
if response.status_code in (200, 400):
    print(f'JSON response: {response.json()}')
```

To stop the running SP/PG via docker-compose:

```bash
make dev-down
```
