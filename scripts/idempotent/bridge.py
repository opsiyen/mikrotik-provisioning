import logging


def ensure_bridge_exists(conn, bridge_name, dry_run=False):
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


def ensure_bridge_port_exists(conn, interface, bridge, dry_run=False):
    """Buat bridge port interface hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah bridge port interface sudah ada
    output = conn.send_command(
        f'/interface bridge port print where interface="{interface}"'
    )
    if interface in output and bridge in output:
        logging.info(
            f"󰡕 Interface '{interface}' sudah ada di '{bridge}', lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(
                f" Akan memasukkan interface '{interface}' ke dalam '{bridge}'"
            )
        else:
            logging.info(f" Memasukkan interface '{interface}' ke dalam '{bridge}'")
            conn.send_command(
                f"/interface bridge port add interface={interface} bridge={bridge}"
            )
