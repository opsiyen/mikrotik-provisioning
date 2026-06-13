import logging


def ensure_identity(conn, expected_name, dry_run=False):
    """Set identity hanya jika belum sesuai"""
    output = conn.send_command("/system identity print")
    # output biasanya "name: xxx"
    current_name = output.split(":")[1].strip() if "name:" in output else None
    if current_name == expected_name:
        logging.info(f"󰡕 Identity sudah '{expected_name}', lewati perubahan")
        return
    else:
        if dry_run:
            logging.info(
                f" Akan mengubah identity dari '{current_name}' menjadi '{expected_name}'"
            )
        else:
            logging.info(
                f" Mengubah identity dari '{current_name}' menjadi '{expected_name}'"
            )
            # expect_string untuk mengantisipasi perubahan prompt
            conn.send_command(
                f"/system identity set name={expected_name}",
                expect_string=r"\] >",
                read_timeout=30,
            )
            # logging.info(f"󰡕 Identity berhasil diubah menjadi '{expected_name}'")
