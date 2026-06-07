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


def ensure_bridge_exists(conn, bridge_name, dry_run=False):
    """Buat bridge hanya jika belum ada. Mode dry_run hanya mencetak."""
    # Cek apakah bridge sudah ada
    output = conn.send_command(f"/interface bridge print where name={bridge_name}")
    if bridge_name in output:
        logging.info(f"✅ Bridge '{bridge_name}' sudah ada, lewati pembuatan")
        return
    else:
        if dry_run:
            logging.info(f"[DRY-RUN] Akan membuat bridge '{bridge_name}'")
        else:
            logging.info(f"➕ Membuat bridge '{bridge_name}'")
            conn.send_command(f"/interface bridge add name={bridge_name}")


def ensure_identity(conn, expected_name, dry_run=False):
    """Set identity hanya jika belum sesuai"""
    output = conn.send_command("/system identity print")
    # Output biasanya "name: xxx"
    current_name = output.split(":")[1].strip() if "name:" in output else None

    if current_name == expected_name:
        logging.info(f"✅ Identity sudah '{expected_name}', lewati perubahan")
        return
    else:
        if dry_run:
            logging.info(
                f"[DRY-RUN] Akan mengubah identity dari '{current_name}' menjadi '{expected_name}'"
            )
        else:
            logging.info(
                f"🔄 Mengubah identity dari '{current_name}' menjadi '{expected_name}'"
            )
            # Gunakan expect_string untuk mengantisipasi perubahan prompt
            conn.send_command(
                f"/system identity set name={expected_name}",
                expect_string=r"\] >",
                read_timeout=30,
            )
            logging.info(f"Identity berhasil diubah menjadi '{expected_name}'")


def ensure_vlan_exists(conn, vlan_name, vlan_id, interface, dry_run=False):
    """Buat vlan hanya jika belum ada. Mode dry_run hanya mencetak."""
    # Cek apakah vlan sudah ada
    output = conn.send_command(f"/interface vlan print where name={vlan_name}")
    if vlan_name in output and interface in output:
        logging.info(
            f"✅ vlan '{vlan_name}' sudah ada di {interface}, lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(
                f"[DRY-RUN] Akan membuat vlan '{vlan_name}'(ID: {vlan_id}) di {interface}"
            )
        else:
            logging.info(f"➕ Membuat vlan '{vlan_name}'(ID: {vlan_id}) di {interface}")
            conn.send_command(
                f"/interface vlan add name={vlan_name} vlan-id={vlan_id} interface={interface}"
            )


def apply_commands(conn, commands, dry_run=False):
    """Eksekusi perintah dengan idempotency dan penanganan khusus untuk set identity."""
    for cmd in commands:
        # Handle perintah add bridge secara idempotent
        if cmd.startswith("/interface bridge add name="):
            bridge_name = cmd.split("name=")[1].split()[0].strip()
            ensure_bridge_exists(conn, bridge_name, dry_run)

        # Handle perintah set identity (perubahan prompt)
        elif cmd.startswith("/system identity set name="):
            expected_name = cmd.split("name=")[1].split()[0].strip()
            ensure_identity(conn, expected_name, dry_run)

        # Handle perintah add vlan secara idempotent
        elif cmd.startswith("/interface vlan add"):
            # Ekstraksi parameter dengan aman
            vlan_name = None
            vlan_id = None
            interface = None
            parts = cmd.split()

            for part in parts:
                if part.startswith("name="):
                    vlan_name = part.split("=")[1]
                elif part.startswith("vlan-id="):
                    vlan_id = part.split("=")[1]
                elif part.startswith("interface="):
                    interface = part.split("=")[1]

            if vlan_name and vlan_id and interface:
                ensure_vlan_exists(conn, vlan_name, vlan_id, interface, dry_run)
            else:
                logging.error(f"🚨 Format perintah VLAN tidak valid: {cmd}")

        # Perintah lain
        else:
            if dry_run:
                logging.info(f"[DRY-RUN] {cmd}")
            else:
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


def verify_vlan_exists(conn, vlan_name):
    """Verifikasi apakah vlan dengan nama tertentu sudah ada"""
    output = conn.send_command(f"/interface vlan print where name={vlan_name}")
    # Jika vlan ditemukan, output tidak kosong
    if vlan_name in output:
        logging.info(f"✅ vlan '{vlan_name}' ditemukan")
        return True
    else:
        logging.error(f"❌ vlan '{vlan_name}' tidak ditemukan")
        return False


# ========== 3. Main ==========
def main():
    setup_logging()

    # Tambahkan opsi dry-run (bisa dari environment variable atau argumen)
    # Sederhana: cek apakah ada file .dry-run atau variabel env
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    if dry_run:
        logging.info("===== DRY-RUN MODE AKTIF - TIDAK ADA PERUBAHAN NYATA =====")

    device = load_credentials()
    if not all([device["host"], device["username"], device["password"]]):
        logging.error("Kredensial tidak lengkap")
        return

    conn = connect_to_router(device)
    commands = read_commands()
    apply_commands(conn, commands, dry_run)
    conn.disconnect()
    logging.info("Provisioning selesai")


if __name__ == "__main__":
    main()
