import logging


def ensure_nat_masquerade(
    conn, out_interface, chain="srcnat", action="masquerade", dry_run=False
):
    """
    Pastikan aturan NAT masquerade untuk out_interface sudah ada.
    Idempotent dengan pengecekan berdasarkan out-interface dan action.
    """
    # Cari aturan yang sudah ada
    # Gunakan print without where untuk parsing lebih sederhana
    output = conn.send_command("/ip firewall nat print")
    found = False
    for line in output.splitlines():
        # Contoh line: "0    chain=srcnat action=masquerade out-interface=bridge-wan ..."
        if f"out-interface={out_interface}" in line and f"action={action}" in line:
            found = True
            break

    if found:
        logging.info(
            f"󰡕 NAT masquerade untuk {out_interface} sudah ada, lewati pembuatan"
        )
        return

    if dry_run:
        logging.info(f" Akan menambah NAT masquerade untuk {out_interface}")
        return

    logging.info(f" Menambah NAT masquerade untuk {out_interface}")
    cmd = f"/ip firewall nat add chain={chain} out-interface={out_interface} action={action}"
    conn.send_command(cmd)
    # logging.info("NAT masquerade berhasil ditambahkan")
