import logging


def ensure_ip_address_exists(conn, address, interface, dry_run=False):
    """Buat ip address hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah ip address sudah ada
    output = conn.send_command(f'/ip address print where address="{address}"')
    if address in output and interface in output:
        logging.info(
            f"󰡕 Ip address '{address}' sudah ada di '{interface}', lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(f" Akan membuat ip address '{address}' untuk '{interface}'")
        else:
            logging.info(f" Membuat ip address '{address}' untuk '{interface}'")
            conn.send_command(
                f"/ip address add address={address} interface={interface}"
            )
