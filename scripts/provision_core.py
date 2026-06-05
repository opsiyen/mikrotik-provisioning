import os
import logging
from datetime import datetime
from netmiko import ConnectHandler
from dotenv import load_dotenv


# ========== 1. Setup ==========
def setup_logging():
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/provision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


def load_credentials():
    load_dotenv()
    return {
        "device_type": "mikrotik_routeros",
        "host": os.getenv("MIKROTIK_HOST"),
        "username": os.getenv("MIKROTIK_USERNAME"),
        "password": os.getenv("MIKROTIK_PASSWORD"),
    }


# ========== 2. Core Functions ==========
def connect_to_router(device_dict):
    try:
        conn = ConnectHandler(**device_dict)
        logging.info(f"Terhubung ke {device_dict['host']}")
        return conn
    except Exception as e:
        logging.error(f"Gagal koneksi: {e}")
        raise


def read_commands(config_path="config/base_config.txt"):
    with open(config_path, "r") as f:
        commands = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
    logging.info(f"Membaca {len(commands)} perintah dari {config_path}")
    return commands


def apply_commands(conn, commands):
    for cmd in commands:
        logging.info(f"Menjalankan: {cmd}")
        output = conn.send_command(cmd)
        if output:
            logging.debug(f"Output: {output}")


def verify_identity(conn, expected_name):
    """Verifikasi system identity sesuai harapan"""
    output = conn.send_command("/system identity print")
    # Output biasanya "name: xxx"
    if f"name: {expected_name}" in output:
        logging.info(f"✅ Identity berhasil diubah menjadi '{expected_name}'")
        return True
    else:
        logging.error(f"❌ Identity gagal: '{output}'")
        return False


def verify_bridge_exists(conn, bridge_name):
    """Verifikasi apakah bridge dengan nama tertentu sudah ada"""
    output = conn.send_command(f"/interface bridge print where name={bridge_name}")
    # Jika bridge ditemukan, output tidak kosong
    if bridge_name in output:
        logging.info(f"✅ Bridge '{bridge_name}' ditemukan")
        return True
    else:
        logging.error(f"❌ Bridge '{bridge_name}' tidak ditemukan")
        return False


# ========== 3. Main ==========
def main():
    setup_logging()
    device = load_credentials()
    if not all([device["host"], device["username"], device["password"]]):
        logging.error("Kredensial tidak lengkap")
        return

    conn = connect_to_router(device)
    commands = read_commands()
    apply_commands(conn, commands)

    # Verifikasi
    logging.info("=== Verifikasi konfigurasi ===")
    verify_identity(conn, "router-netmiko")  # sesuaikan dengan nama yang diset
    verify_bridge_exists(conn, "bridge-lan")
    verify_bridge_exists(conn, "bridge-wan")

    conn.disconnect()
    logging.info("Provisioning selesai")


if __name__ == "__main__":
    main()
