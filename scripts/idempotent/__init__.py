from .identity import ensure_identity
from .bridge import ensure_bridge_exists, ensure_bridge_port_exists
from .dhcp_client import ensure_dhcp_client
from .dns_server import ensure_dns
from .nat_masquerade import ensure_nat_masquerade
from .vlan import ensure_vlan_exists
from .ip_address import ensure_ip_address_exists
from .lists import ensure_interface_list_exists, ensure_list_member_exists
from .ip_pool import ensure_ip_pool_exists
from .dhcp_server import ensure_dhcp_server
from .ntp_client import ensure_ntp_client
from .neighboar_macserver import ensure_neighbor_discovery


def apply_all(conn, config, dry_run=False):
    """
    Fungsi praktis untuk menjalankan semua konfigurasi idempotent berdasarkan config dictionary.
    """
    # 1. IDENTITY - OK
    if "identity" in config:
        ensure_identity(conn, config["identity"]["name"], dry_run)

    # 2. BRIDGES - OK
    for bridge_cfg in config.get("bridges", []):
        ensure_bridge_exists(conn, bridge_cfg, dry_run)

    # 3. BRIDGE PORT - OK
    for bridge_port_cfg in config.get("bridge_ports", []):
        ensure_bridge_port_exists(conn, bridge_port_cfg, dry_run)

    # 4. DHCP CLIENT - OK
    if "dhcp_client" in config:
        dhcp = config["dhcp_client"]
        ensure_dhcp_client(
            conn,
            dhcp["interface"],
            use_peer_dns=dhcp.get("use_peer_dns", False),
            disabled=dhcp.get("disabled", False),
            dry_run=dry_run,
        )

    # 5. DNS - OK
    if "dns" in config:
        dns = config["dns"]
        ensure_dns(conn, dns["servers"], dns["allow_remote_requests"], dry_run)

    # 6. NAT MASQUERADE - OK
    if "nat_masquerade" in config:
        nat_cfg = config["nat_masquerade"]
        ensure_nat_masquerade(
            conn,
            out_interface=nat_cfg["out_interface"],
            chain=nat_cfg.get("chain", "srcnat"),
            action=nat_cfg.get("action", "masquerade"),
            dry_run=dry_run,
        )

    # 7. VLANs - OK
    for vlan_cfg in config.get("vlans", []):
        ensure_vlan_exists(conn, vlan_cfg, dry_run)

    # 8. IP ADDRESS - OK
    for ip_addr_cfg in config.get("ip_addresses", []):
        ensure_ip_address_exists(conn, ip_addr_cfg, dry_run)

    # 9. IP POOL - OK
    for pool_cfg in config.get("ip_pool", []):
        ensure_ip_pool_exists(conn, pool_cfg, dry_run)

    # 10. DHCP SERVER -
    for dhcp_config in config.get("dhcp_server", []):
        ensure_dhcp_server(conn, dhcp_config, dry_run)

    # 11. INTERFACE LIST - OK
    for list_cfg in config.get("interface_lists", []):
        ensure_interface_list_exists(conn, list_cfg, dry_run)

    # 12. LIST MEMBER - OK
    for list_member_cfg in config.get("list_members", []):
        ensure_list_member_exists(conn, list_member_cfg, dry_run)

    # 13. NTP CLIENT - OK
    if "ntp_client" in config:
        ntp = config["ntp_client"]
        ensure_ntp_client(conn, ntp["enabled"], ntp["server"], dry_run)

    # Neighbor Discovery
    if "neighbor_discovery" in config:
        nd_cfg = config["neighbor_discovery"]
        ensure_neighbor_discovery(conn, nd_cfg["allowed_interface_list"], dry_run)
