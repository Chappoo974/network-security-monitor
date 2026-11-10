"""
Database module for storing and tracking network devices.
Uses SQLite to maintain a history of discovered devices.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class DeviceDatabase:
    """Manages storage and retrieval of network device information."""

    def __init__(self, db_path: str = "data/devices.db"):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Open database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create the devices table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                mac_address TEXT NOT NULL,
                hostname TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                UNIQUE(mac_address)
            )
        """)
        self.conn.commit()

    def add_or_update_device(self, ip: str, mac: str, hostname: str = "Unknown"):
        """
        Add a new device or update existing device's last_seen time.

        Args:
            ip: IP address of the device
            mac: MAC address of the device
            hostname: Hostname of the device (optional)

        Returns:
            bool: True if this is a new device, False if updated existing
        """
        now = datetime.now().isoformat()

        # Check if device already exists
        self.cursor.execute(
            "SELECT id, is_active FROM devices WHERE mac_address = ?",
            (mac,)
        )
        result = self.cursor.fetchone()

        if result:
            # Update existing device
            device_id, is_active = result
            self.cursor.execute("""
                UPDATE devices
                SET ip_address = ?,
                    hostname = ?,
                    last_seen = ?,
                    is_active = 1
                WHERE mac_address = ?
            """, (ip, hostname, now, mac))
            self.conn.commit()

            # Return True only if device was previously inactive (rejoined network)
            return is_active == 0
        else:
            # Insert new device
            self.cursor.execute("""
                INSERT INTO devices (ip_address, mac_address, hostname, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?)
            """, (ip, mac, hostname, now, now))
            self.conn.commit()
            return True

    def get_all_devices(self) -> List[Dict]:
        """
        Get all devices from the database.

        Returns:
            List of dictionaries containing device information
        """
        self.cursor.execute("""
            SELECT ip_address, mac_address, hostname, first_seen, last_seen, is_active
            FROM devices
            ORDER BY last_seen DESC
        """)

        devices = []
        for row in self.cursor.fetchall():
            devices.append({
                'ip': row[0],
                'mac': row[1],
                'hostname': row[2],
                'first_seen': row[3],
                'last_seen': row[4],
                'is_active': bool(row[5])
            })
        return devices

    def get_active_devices(self) -> List[Dict]:
        """
        Get only currently active devices.

        Returns:
            List of dictionaries containing active device information
        """
        self.cursor.execute("""
            SELECT ip_address, mac_address, hostname, first_seen, last_seen
            FROM devices
            WHERE is_active = 1
            ORDER BY last_seen DESC
        """)

        devices = []
        for row in self.cursor.fetchall():
            devices.append({
                'ip': row[0],
                'mac': row[1],
                'hostname': row[2],
                'first_seen': row[3],
                'last_seen': row[4]
            })
        return devices

    def mark_devices_inactive(self, active_macs: List[str]):
        """
        Mark devices as inactive if they're not in the current scan.

        Args:
            active_macs: List of MAC addresses found in the latest scan
        """
        if not active_macs:
            # If no devices found, mark all as inactive
            self.cursor.execute("UPDATE devices SET is_active = 0")
        else:
            # Mark devices as inactive if they weren't in this scan
            placeholders = ','.join('?' * len(active_macs))
            self.cursor.execute(f"""
                UPDATE devices
                SET is_active = 0
                WHERE mac_address NOT IN ({placeholders})
            """, active_macs)

        self.conn.commit()

    def get_device_count(self) -> Dict[str, int]:
        """
        Get count of total and active devices.

        Returns:
            Dictionary with 'total' and 'active' counts
        """
        self.cursor.execute("SELECT COUNT(*) FROM devices")
        total = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM devices WHERE is_active = 1")
        active = self.cursor.fetchone()[0]

        return {'total': total, 'active': active}

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


# Test code
if __name__ == "__main__":
    import os

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Test the database
    db = DeviceDatabase("data/test_devices.db")
    db.connect()

    print("Testing DeviceDatabase...\n")

    # Add some test devices
    print("Adding test devices:")
    is_new = db.add_or_update_device("192.168.1.10", "AA:BB:CC:DD:EE:01", "laptop")
    print(f"  Device 1 - New: {is_new}")

    is_new = db.add_or_update_device("192.168.1.11", "AA:BB:CC:DD:EE:02", "phone")
    print(f"  Device 2 - New: {is_new}")

    is_new = db.add_or_update_device("192.168.1.12", "AA:BB:CC:DD:EE:03", "tablet")
    print(f"  Device 3 - New: {is_new}")

    # Update an existing device (should return False)
    print("\nUpdating existing device:")
    is_new = db.add_or_update_device("192.168.1.10", "AA:BB:CC:DD:EE:01", "laptop-updated")
    print(f"  Device 1 updated - New: {is_new}")

    # Get all devices
    print("\nAll devices:")
    devices = db.get_all_devices()
    for device in devices:
        print(f"  {device['ip']} - {device['mac']} - {device['hostname']} - Active: {device['is_active']}")

    # Get counts
    counts = db.get_device_count()
    print(f"\nDevice counts: Total={counts['total']}, Active={counts['active']}")

    # Mark one device as inactive
    print("\nMarking some devices as inactive...")
    db.mark_devices_inactive(["AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02"])

    # Check active devices
    print("\nActive devices only:")
    active = db.get_active_devices()
    for device in active:
        print(f"  {device['ip']} - {device['mac']} - {device['hostname']}")

    counts = db.get_device_count()
    print(f"\nDevice counts: Total={counts['total']}, Active={counts['active']}")

    db.close()
    print("\nDatabase test complete!")
