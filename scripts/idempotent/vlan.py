import logging


def ensure_vlan_exists(conn, vlan_name, vlan_id, interface, dry_run=False):
    """Buat vlan hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah vlan sudah ada
    output = conn.send_command(f"/interface vlan print where name={vlan_name}")
    if vlan_name in output and interface in output:
        logging.info(
            f"󰡕 Vlan '{vlan_name}' sudah ada di '{interface}', lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(
                f" Akan membuat vlan '{vlan_name}' id:'{vlan_id}' di '{interface}'"
            )
        else:
            logging.info(
                f" Membuat vlan '{vlan_name}' id:'{vlan_id}' di '{interface}'"
            )
            conn.send_command(
                f"/interface vlan add name={vlan_name} vlan-id={vlan_id} interface={interface}"
            )
