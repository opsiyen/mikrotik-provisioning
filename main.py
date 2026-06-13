import os
import logging
from scripts.utils import setup_logging, load_credentials, connect_to_router
from scripts.config_loader import read_yaml_config
from scripts.idempotent import apply_all


def main():
    setup_logging()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    if dry_run:
        logging.info("===== DRY-RUN MODE AKTIF =====")

    device = load_credentials()
    if not all([device["host"], device["username"], device["password"]]):
        logging.error(" Kredensial tidak lengkap")
        return

    conn = connect_to_router(device)
    commands = read_yaml_config()
    apply_all(conn, commands, dry_run)
    conn.disconnect()
    logging.info(" Provisioning selesai")


if __name__ == "__main__":
    main()
