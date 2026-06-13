import logging


def ensure_dns(conn, servers, allow_remote, dry_run=False):
    output = conn.send_command("/ip dns print")
    allow_str = "yes" if allow_remote else "no"

    # Gabungkan semua baris menjadi satu string (hapus newline)
    output_block = " ".join(output.splitlines())

    # Cek apakah servers dan allow ada di output
    if (
        servers in output_block
        and f"allow-remote-requests: {allow_str}" in output_block
    ):
        logging.info(f"󰡕 DNS sudah sesuai (servers={servers}, allow={allow_str})")
        return

    if dry_run:
        logging.info(
            f" Akan menambahkan servers={servers}, dan allow-remote-requests={allow_str} pada DNS"
        )
        return

    conn.send_command(
        f"/ip dns set servers={servers} allow-remote-requests={allow_str}"
    )
    logging.info(f" DNS berhasil dikonfigurasi {servers}")
