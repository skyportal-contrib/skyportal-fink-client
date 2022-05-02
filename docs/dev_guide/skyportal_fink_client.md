# Main : SkyPortal Fink Client

### poll_alerts()

Connect to and poll alerts from fink servers to post them in skyportal using its API, using a config file containing
the necessary access credentials to both fink and skyportal, as well as a list of topics to subscribe to
(corresponding to a classification in skyportal).

#### Arguments:
```
max_timeout: int
    maximum time to wait for a message to be received from a topic
    (max interval between two polling tries)
```

#### Returns:
```
None
```
