import logging
import yaml


def read_yaml_config(config_path="config/base_config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.info(f"󰑇 Membaca konfigurasi dari {config_path}")
    return config
