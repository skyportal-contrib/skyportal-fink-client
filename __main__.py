import argparse

from skyportal_fink_client.skyportal_fink_client import poll_alerts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SkyPortal Fink Client")
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a config YAML file (default: config.yaml in the repo root)",
    )
    args = parser.parse_args()
    poll_alerts(config_path=args.config)
