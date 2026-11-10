"""
Network scanner module using ARP protocol
"""

from scapy.all import ARP, Ether, srp


def mock_scan():
    """
    Simulates network scan for testing without network access
    Returns fake device data
    """
    return [
        {'ip': '192.168.1.1', 'mac': '00:11:22:33:44:55', 'hostname': 'router'},
        {'ip': '192.168.1.10', 'mac': 'AA:BB:CC:DD:EE:FF', 'hostname': 'laptop'},
        {'ip': '192.168.1.15', 'mac': '12:34:56:78:90:AB', 'hostname': 'phone'},
        {'ip': '192.168.1.20', 'mac': 'FF:EE:DD:CC:BB:AA', 'hostname': 'tablet'},
    ]


def scan_network(ip_range):
    """
    Scan a network range and return list of active devices
    
    Args:
        ip_range: Network range to scan (e.g., "192.168.1.0/24")
    
    Returns:
        List of dictionaries with 'ip' and 'mac' keys
    """
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=0)[0]   
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices


if __name__ == "__main__":
    print("Running in TEST MODE (mock data)...")

    # Use mock data instead of real scan
    devices = mock_scan()
    # To use real scanning: devices = scan_network("192.168.1.0/24")

    print(f"\nFound {len(devices)} devices:")
    for device in devices:
        print(f"IP: {device['ip']:16} MAC: {device['mac']}")
    