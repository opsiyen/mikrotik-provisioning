import logging


def ensure_ip_pool_exists(conn, pool_cfg, dry_run=False):
    name = pool_cfg["name"]
    ranges = pool_cfg["ranges"]

    """Buat ip pool hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah ip pool sudah ada
    output = conn.send_command(f'/ip pool print where name="{name}"')
    if name in output and ranges in output:
        logging.info(
            f"󰡕 Ip pool '{name}' sudah ada di range '{ranges}', lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(f" Akan membuat ip pool '{name}' di range '{ranges}'")
        else:
            logging.info(f" Membuat ip pool '{name}' di range '{ranges}'")
            conn.send_command(f"/ip pool add name={name} ranges={ranges}")
