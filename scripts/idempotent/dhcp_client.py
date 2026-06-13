import logging


def ensure_dhcp_client(
    conn, interface, use_peer_dns=False, disabled=False, dry_run=False
):
    """
    Pastikan DHCP client aktif pada interface tertentu (idempotent).
    """
    # Ambil output print biasa tanpa filter
    output = conn.send_command("/ip dhcp-client print")
    logging.debug(f"DHCP client raw output: {repr(output)}")

    # Cari baris yang mengandung "interface=bridge-wan" (tanpa filter where)
    found = False
    for line in output.splitlines():
        if f"interface={interface}" in line:
            found = True
            break

    # Jika tidak ditemukan, coba dengan where (untuk jaga-jaga)
    if not found:
        output_where = conn.send_command(
            f"/ip dhcp-client print where interface={interface}"
        )
        logging.debug(f"Output with where: {repr(output_where)}")
        if interface in output_where:
            found = True

    if found:
        logging.info(f"󰡕 DHCP client pada {interface} sudah ada, lewati pembuatan")
        return

    if dry_run:
        logging.info(f" Akan membuat DHCP client pada {interface}")
        return

    logging.info(f" Membuat DHCP client pada {interface}")
    cmd = f"/ip dhcp-client add interface={interface} use-peer-dns={'yes' if use_peer_dns else 'no'} disabled={'yes' if disabled else 'no'}"
    conn.send_command(cmd)
    # logging.info("DHCP client berhasil ditambahkan")
