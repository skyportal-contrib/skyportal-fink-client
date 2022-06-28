
# Main : SkyPortal API Helper functions
::: skyportal_fink_client.skyportal_fink_client
    handler: python
    rendering:
      show_root_heading: false
      show_source: false

# Details:

You will notice that the poll_alerts() method, and other methods in this file, can take as arguments some of the parameters also defined in the ``config.yaml`` file. Why this redundancy? The reason is the following: If you want to import and call any of these methods in your own code, to run it programmaticaly along with some other bits of code, you can pass specific parameters instead of having to write them to the config.

For example, we use this to run skyportal-fink-client as a microservice of SkyPortal (run at the same time as the app, no need to run it manually in a seperate terminal, and no need to get a skyportal token from your profile or the .tokens.yaml to paste to the `config.yaml`). There, when running skyportal, we can start skyportal-fink-client at the same time automatically. And thanks to these methods being able to either use the config or parameters passed to them, you can share one config file for skyportal and skyportal-fink-client for example, then pass arguments to skyportal-fink-client via skyportal, as well as pass the skyportal token automatically.

If you decide to pass parameters to these methods rather than use the `config.yaml` file, beware that if you forget any parameters, it will default to the value found in the `config.yaml` file.

You'll notice the same for the `log` function that is a parameter of most methods found here. If you want to use a different logger, you can pass it as an argument to the `pool_alerts()` method.
