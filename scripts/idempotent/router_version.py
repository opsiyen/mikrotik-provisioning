import logging


def get_routeros_version(conn):
    """
    Mengembalikan versi mayor RouterOS (6 atau 7) dengan caching per koneksi.
    """
    # Caching sederhana: simpan di attribute connection
    if hasattr(conn, "_routeros_version"):
        return conn._routeros_version

    output = conn.send_command("/system resource print")
    for line in output.splitlines():
        if "version:" in line:
            version_str = line.split(":", 1)[1].strip()
            major = int(version_str.split(".")[0])
            conn._routeros_version = major
            logging.debug(f"Detected RouterOS version: {major}")
            return major
    raise Exception("Tidak dapat mendeteksi versi RouterOS")
