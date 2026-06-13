import logging


def ensure_interface_list_exists(conn, list_name, comment, dry_run=False):
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


def ensure_list_member_exists(conn, listm, interface, dry_run=False):
    """Buat list member hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah list member sudah ada
    output = conn.send_command(f"/interface list member print where list={listm}")
    if listm in output and interface in output:
        logging.info(f"󰡕 '{interface}' sudah ada di list '{listm}', lewati pembuatan")
        return
    else:
        if dry_run:
            logging.info(
                f" Akan memasukkan interface '{interface}' ke dalam list '{listm}'"
            )
        else:
            logging.info(
                f" Memasukkan interface '{interface}' ke dalam list '{listm}'"
            )
            conn.send_command(
                f"/interface list member add interface={interface} list={listm}"
            )
