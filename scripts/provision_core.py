import os
import logging
import yaml
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


# ========== 2. Core Functions (ensure, verify, apply_config)==========
def connect_to_router(device_dict):
    try:
        conn = ConnectHandler(**device_dict)
        logging.info(f"󰌘 Terhubung ke {device_dict['host']}")
        return conn
    except Exception as e:
        logging.error(f"󰌙 Gagal koneksi: {e}")
        raise


def read_yaml_config(config_path="config/base_config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.info(f"󰑇 Membaca konfigurasi dari {config_path}")
    return config


# ========== ensure top ==========
def get_routeros_version(conn):
    """Mengembalikan versi mayor RouterOS (6 atau 7)"""
    output = conn.send_command("/system resource print")
    # Cari baris yang mengandung "version:"
    for line in output.splitlines():
        if "version:" in line:
            version_str = line.split(":")[1].strip()
            # Misal "7.22.1" atau "6.49.19"
            major = int(version_str.split(".")[0])
            return major
    raise Exception("Tidak dapat mendeteksi versi RouterOS")


def ensure_identity(conn, expected_name, dry_run=False):
    """Set identity hanya jika belum sesuai"""
    output = conn.send_command("/system identity print")
    # output biasanya "name: xxx"
    current_name = output.split(":")[1].strip() if "name:" in output else None
    if current_name == expected_name:
        logging.info(f"󰡕 Identity sudah '{expected_name}', lewati perubahan")
        return
    else:
        if dry_run:
            logging.info(
                f" Akan mengubah identity dari '{current_name}' menjadi '{expected_name}'"
            )
        else:
            logging.info(
                f" Mengubah identity dari '{current_name}' menjadi '{expected_name}'"
            )
            # expect_string untuk mengantisipasi perubahan prompt
            conn.send_command(
                f"/system identity set name={expected_name}",
                expect_string=r"\] >",
                read_timeout=30,
            )
            logging.info(f"󰡕 Identity berhasil diubah menjadi '{expected_name}'")


def ensure_bridge(conn, bridge_name, dry_run=False):
    """Buat bridge hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah bridge sudah ada
    output = conn.send_command(f"/interface bridge print where name={bridge_name}")
    if bridge_name in output:
        logging.info(f"󰡕 Bridge '{bridge_name}' sudah ada, lewati pembuatan")
        return
    else:
        if dry_run:
            logging.info(f" Akan membuat bridge '{bridge_name}'")
        else:
            logging.info(f" Membuat bridge '{bridge_name}'")
            conn.send_command(f"/interface bridge add name={bridge_name}")


def ensure_vlan(conn, vlan_name, vlan_id, interface, dry_run=False):
    """Buat vlan hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah vlan sudah ada
    output = conn.send_command(f"/interface vlan print where name={vlan_name}")
    if vlan_name in output and interface in output:
        logging.info(f"󰡕 Vlan '{vlan_name}' sudah ada di {interface}, lewati pembuatan")
        return
    else:
        if dry_run:
            logging.info(
                f" Akan membuat vlan '{vlan_name}'(ID: {vlan_id}) di {interface}"
            )
        else:
            logging.info(f" Membuat vlan '{vlan_name}'(ID: {vlan_id}) di {interface}")
            conn.send_command(
                f"/interface vlan add name={vlan_name} vlan-id={vlan_id} interface={interface}"
            )


def ensure_ip_address(conn, address, interface, dry_run=False):
    """Buat ip address hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah ip address sudah ada
    output = conn.send_command(f'/ip address print where address="{address}"')
    if address in output and interface in output:
        logging.info(
            f"󰡕 Ip address '{address}' sudah ada di {interface}, lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(f" Akan membuat ip address '{address}' di {interface}")
        else:
            logging.info(f" Membuat ip address '{address}' di {interface}")
            conn.send_command(
                f"/ip address add address={address} interface={interface}"
            )


def ensure_interface_list(conn, list_name, comment, dry_run=False):
    """Buat list hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah list sudah ada
    output = conn.send_command(f"/interface list print where name={list_name}")
    if list_name in output:
        logging.info(f"󰡕 List '{list_name}' sudah ada, lewati pembuatan")
        return
    else:
        if dry_run:
            logging.info(f" Akan membuat list '{list_name}'")
        else:
            logging.info(f" Membuat list '{list_name}'")
            conn.send_command(
                f'/interface list add name={list_name} comment="{comment}"'
            )


def ensure_list_member(conn, listm, interface, dry_run=False):
    """Buat list member hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah list member sudah ada
    output = conn.send_command(f"/interface list member print where list={listm}")
    if listm in output and interface in output:
        logging.info(
            f"󰡕 List member '{listm}' sudah ada di {interface}, lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(f" Akan membuat list member '{listm}' di {interface}")
        else:
            logging.info(f" Membuat list member '{listm}' di {interface}")
            conn.send_command(
                f"/interface list member add list={listm} interface={interface}"
            )


def ensure_ntp_client(conn, enabled, server, dry_run=False):
    """Konfigurasi NTP client secara idempotent (support v6 dan v7)"""
    version = get_routeros_version(conn)

    # Baca konfigurasi saat ini
    output = conn.send_command("/system ntp client print")
    logging.debug(f"Output NTP print: {output}")

    # Parsing berdasarkan versi
    current_enabled = None
    current_server = None
    for line in output.splitlines():
        if "enabled:" in line:
            current_enabled = line.split(":")[1].strip()
        if version == 7 and "servers:" in line:
            current_server = line.split(":")[1].strip()
        elif version == 6 and "server-dns-names:" in line:
            current_server = line.split(":")[1].strip()

    enabled_str = "yes" if enabled else "no"

    # Cek apakah sudah sesuai
    if current_enabled == enabled_str and current_server == server:
        logging.info(
            f"󰡕 NTP client sudah sesuai (enabled={enabled_str}, server={server})"
        )
        return

    # Dry-run
    if dry_run:
        if version == 7:
            cmd_display = (
                f"/system ntp client set enabled={enabled_str} servers={server}"
            )
        else:
            cmd_display = f"/system ntp client set enabled={enabled_str} server-dns-names={server}"
        logging.info(f" Akan menjalankan: {cmd_display}")
        return

    # Eksekusi nyata
    logging.info(
        f" Mengatur NTP client: enabled={enabled_str}, server={server} (versi {version})"
    )
    if version == 7:
        cmd = f"/system ntp client set enabled={enabled_str} servers={server}"
    else:
        cmd = f"/system ntp client set enabled={enabled_str} server-dns-names={server}"
    conn.send_command(cmd, expect_string=r"\] >", read_timeout=30)
    logging.info("NTP client berhasil dikonfigurasi")


# ========== ensure bottom ==========
# ========== verify top ==========
def verify_identity(conn, expected_name):
    """Verifikasi system identity sesuai harapan"""
    output = conn.send_command("/system identity print")
    # Output biasanya "name: xxx"
    if f"name: {expected_name}" in output:
        logging.info(f"󰡕 Identity berhasil diubah menjadi '{expected_name}'")
        return True
    else:
        logging.error(f"󰛉 Identity gagal: '{output}'")
        return False


def verify_bridge_exists(conn, bridge_name):
    """Verifikasi apakah bridge dengan nama tertentu sudah ada"""
    output = conn.send_command(f"/interface bridge print where name={bridge_name}")
    # Jika bridge ditemukan, output tidak kosong
    if bridge_name in output:
        logging.info(f"󰡕 Bridge '{bridge_name}' ditemukan")
        return True
    else:
        logging.error(f"󰛉 Bridge '{bridge_name}' tidak ditemukan")
        return False


def verify_vlan_exists(conn, vlan_name):
    """Verifikasi apakah vlan dengan nama tertentu sudah ada"""
    output = conn.send_command(f"/interface vlan print where name={vlan_name}")
    # Jika vlan ditemukan, output tidak kosong
    if vlan_name in output:
        logging.info(f"󰡕 vlan '{vlan_name}' ditemukan")
        return True
    else:
        logging.error(f"󰛉 vlan '{vlan_name}' tidak ditemukan")
        return False


def verify_ip_address_exists(conn, address):
    """Verifikasi apakah ip address sudah ada"""
    output = conn.send_command(f'/ip address print where name="{address}"')
    # Jika ip address ditemukan, output tidak kosong
    if address in output:
        logging.info(f"󰡕 ip address '{address}' ditemukan")
        return True
    else:
        logging.error(f"󰛉 ip address '{address}' tidak ditemukan")
        return False


def verify_interface_list_exists(conn, list_name):
    """Verifikasi apakah list dengan nama tertentu sudah ada"""
    output = conn.send_command(f"/interface list print where name={list_name}")
    # Jika list ditemukan, output tidak kosong
    if list_name in output:
        logging.info(f"󰡕 List '{list_name}' ditemukan")
        return True
    else:
        logging.error(f"󰛉 List '{list_name}' tidak ditemukan")
        return False


def verify_list_member_exists(conn, list_member):
    """Verifikasi apakah list dengan nama tertentu sudah ada"""
    output = conn.send_command(f"/interface list member print where list={list_member}")
    # Jika list ditemukan, output tidak kosong
    if list_member in output:
        logging.info(f"󰡕 List '{list_member}' ditemukan")
        return True
    else:
        logging.error(f"󰛉 List '{list_member}' tidak ditemukan")
        return False


# ========== verify bottom ==========
# ========== apply top ==========
def apply_config(conn, config, dry_run=False):
    """Terapkan konfigurasi dari dictionary YAML menggunakan fungsi-fungsi idempotent."""
    # 1. Identity
    if "identity" in config:
        expected_name = config["identity"]["name"]
        ensure_identity(conn, expected_name, dry_run)

    # 2. Bridges
    for bridge in config.get("bridges", []):
        bridge_name = bridge["name"]
        ensure_bridge(conn, bridge_name, dry_run)

    # 3. VLANs
    for vlan in config.get("vlans", []):
        vlan_name = vlan["name"]
        vlan_id = vlan["vlan_id"]
        interface = vlan["interface"]
        ensure_vlan(conn, vlan_name, vlan_id, interface, dry_run)

    # 4. IP Addresses
    for ip in config.get("ip_addresses", []):
        address = ip["address"]
        interface = ip["interface"]
        ensure_ip_address(conn, address, interface, dry_run)

    # 5. Interface List
    for interface_list in config.get("interface_lists", []):
        list_name = interface_list["name"]
        comment = interface_list["comment"]
        ensure_interface_list(conn, list_name, comment, dry_run)

    # 6. List Member
    for list_member in config.get("list_members", []):
        listm = list_member["list"]
        interface = list_member["interface"]
        ensure_list_member(conn, listm, interface, dry_run)

    # 7. NTP Client
    if "ntp_client" in config:
        ntp = config["ntp_client"]
        ensure_ntp_client(conn, ntp["enabled"], ntp["server"], dry_run)


# ========== apply bottom==========


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
        logging.error(" Kredensial tidak lengkap")
        return

    conn = connect_to_router(device)
    commands = read_yaml_config()
    apply_config(conn, commands, dry_run)
    conn.disconnect()
    logging.info(" Provisioning selesai")


if __name__ == "__main__":
    main()
