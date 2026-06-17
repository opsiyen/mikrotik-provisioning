import logging


def ensure_interface_list_exists(conn, list_cfg, dry_run=False):
    list_name = list_cfg["name"]
    list_comment = list_cfg["comment"]

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
                f'/interface list add name={list_name} comment="{list_comment}"'
            )


def ensure_list_member_exists(conn, list_member_cfg, dry_run=False):
    member_name = list_member_cfg["list"]
    member_interface = list_member_cfg["interface"]

    """Buat list member hanya jika belum ada. Mode dry_run hanya mencetak."""
    # cek apakah list member sudah ada
    output = conn.send_command(f"/interface list member print where list={member_name}")
    if member_name in output and member_interface in output:
        logging.info(
            f"󰡕 '{member_interface}' sudah ada di list '{member_name}', lewati pembuatan"
        )
        return
    else:
        if dry_run:
            logging.info(
                f" Akan memasukkan interface '{member_interface}' ke dalam list '{member_name}'"
            )
        else:
            logging.info(
                f" Memasukkan interface '{member_interface}' ke dalam list '{member_name}'"
            )
            conn.send_command(
                f"/interface list member add interface={member_interface} list={member_name}"
            )
