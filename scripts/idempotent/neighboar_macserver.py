import logging


def ensure_neighbor_discovery(conn, allowed_list_name, dry_run=False):
    """
    Batasi neighbor discovery (mac-server, mac-winbox, ip neighbor discovery)
    hanya pada interface list tertentu.
    """
    changes_needed = False
    config = {}

    # Ambil setting saat ini
    # 1. IP Neighbor Discovery
    nd_out = conn.send_command("/ip neighbor discovery-settings print")
    for line in nd_out.splitlines():
        if "discover-interface-list:" in line:
            current = line.split(":", 1)[1].strip()
            config["discover-interface-list"] = current
            break

    # 2. MAC Server (Winbox & regular)
    mac_out = conn.send_command("/tool mac-server print")
    for line in mac_out.splitlines():
        if "allowed-interface-list:" in line:
            config["mac-server-allowed"] = line.split(":", 1)[1].strip()
            break

    mac_winbox_out = conn.send_command("/tool mac-server mac-winbox print")
    for line in mac_winbox_out.splitlines():
        if "allowed-interface-list:" in line:
            config["mac-winbox-allowed"] = line.split(":", 1)[1].strip()
            break

    # Bandingkan
    if config.get("discover-interface-list") != allowed_list_name:
        changes_needed = True
    if config.get("mac-server-allowed") != allowed_list_name:
        changes_needed = True
    if config.get("mac-winbox-allowed") != allowed_list_name:
        changes_needed = True

    if not changes_needed:
        logging.info(
            f"󰡕 Neighbor discovery & MAC-Server sudah dibatasi ke interface list '{allowed_list_name}', lewati"
        )
        return

    if dry_run:
        logging.info(
            f" Akan membatasi neighbor discovery & MAC-Server ke interface list '{allowed_list_name}'"
        )
        return

    logging.info(
        f" Membatasi neighbor discovery & MAC-Server ke interface list '{allowed_list_name}'"
    )
    conn.send_command(
        f"/ip neighbor discovery-settings set discover-interface-list={allowed_list_name}"
    )
    conn.send_command(
        f"/tool mac-server set allowed-interface-list={allowed_list_name}"
    )
    conn.send_command(
        f"/tool mac-server mac-winbox set allowed-interface-list={allowed_list_name}"
    )
