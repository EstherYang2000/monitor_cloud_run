import yaml
import sys


def load_config():
    """
    Load config yaml file
    """

    with open("/home/icsd_user05_tsmc_hackathon_cloud/app/monitor/data/config.yaml") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg
config = load_config()
