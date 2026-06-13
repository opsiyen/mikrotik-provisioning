import logging
from .router_version import get_routeros_version


def ensure_ntp_client(conn, enabled, server, dry_run=False):
    """Konfigurasi NTP client secara idempotent (support v6 dan v7)"""
    version = get_routeros_version(conn)

    # Baca konfigurasi saat ini
    output = conn.send_command("/system ntp client print")
    logging.debug(f"Output NTP print: {output}")

    # Parsing berdasarkan versi
    current_enabled = None
    current_server = None
    for line in output.splitlines():
        if "enabled:" in line:
            current_enabled = line.split(":")[1].strip()
        if version == 7 and "servers:" in line:
            current_server = line.split(":")[1].strip()
        elif version == 6 and "server-dns-names:" in line:
            current_server = line.split(":")[1].strip()

    enabled_str = "yes" if enabled else "no"

    # Cek apakah sudah sesuai
    if current_enabled == enabled_str and current_server == server:
        logging.info(
            f"󰡕 NTP client sudah sesuai (enabled={enabled_str}, server={server})"
        )
        return

    # Dry-run
    if dry_run:
        if version == 7:
            cmd_display = (
                f"/system ntp client set enabled={enabled_str} servers={server}"
            )
        else:
            cmd_display = f"/system ntp client set enabled={enabled_str} server-dns-names={server}"
        logging.info(f" Akan menjalankan: {cmd_display}")
        return

    # Eksekusi nyata
    # logging.info(
    #     f" Mengatur NTP client: enabled={enabled_str}, server={server} (versi {version})"
    # )
    if version == 7:
        cmd = f"/system ntp client set enabled={enabled_str} servers={server}"
    else:
        cmd = f"/system ntp client set enabled={enabled_str} server-dns-names={server}"
    conn.send_command(cmd, expect_string=r"\] >", read_timeout=30)
    logging.info(f" Berhasil mengatur server={server} pada ntp client")
