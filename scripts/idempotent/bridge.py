import logging


def ensure_bridge_exists(conn, bridge_cfg, dry_run=False):
    bridge_name = bridge_cfg["name"]

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


def ensure_bridge_port_exists(conn, bridge_port_cfg, dry_run=False):
    interface = bridge_port_cfg["interface"]
    bridge_port = bridge_port_cfg["bridge"]

    """Buat bridge port interface hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah bridge port interface sudah ada
    output = conn.send_command(
        f'/interface bridge port print where interface="{interface}"'
    )
    if interface in output and bridge_port in output:
        logging.info(
            f"󰡕 Interface '{interface}' sudah ada di '{bridge_port}', lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(
                f" Akan memasukkan interface '{interface}' ke dalam '{bridge_port}'"
            )
        else:
            logging.info(
                f" Memasukkan interface '{interface}' ke dalam '{bridge_port}'"
            )
            conn.send_command(
                f"/interface bridge port add interface={interface} bridge={bridge_port}"
            )
