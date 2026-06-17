import logging


def ensure_vlan_exists(conn, vlan_cfg, dry_run=False):
    vlan_name = vlan_cfg["name"]
    vlan_id = vlan_cfg["vlan_id"]
    vlan_interface = vlan_cfg["interface"]

    """Buat vlan hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah vlan sudah ada
    output = conn.send_command(f"/interface vlan print where name={vlan_name}")
    if vlan_name in output and vlan_interface in output:
        logging.info(
            f"󰡕 Vlan '{vlan_name}' sudah ada di '{vlan_interface}', lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(
                f" Akan membuat vlan '{vlan_name}' id:'{vlan_id}' di '{vlan_interface}'"
            )
        else:
            logging.info(
                f" Membuat vlan '{vlan_name}' id:'{vlan_id}' di '{vlan_interface}'"
            )
            conn.send_command(
                f"/interface vlan add name={vlan_name} vlan-id={vlan_id} interface={vlan_interface}"
            )
