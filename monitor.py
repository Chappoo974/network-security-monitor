#!/usr/bin/env python3
"""
Network Monitor - Main Script
Continuously scans the network for devices and sends alerts on changes.
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add src directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scanner import scan_network, mock_scan
from database import DeviceDatabase
from alerts import TelegramAlerts


class NetworkMonitor:
    """Main network monitoring orchestrator."""

    def __init__(self, use_mock: bool = False):
        """
        Initialize the network monitor.

        Args:
            use_mock: If True, use mock data instead of real scanning
        """
        load_dotenv()

        self.use_mock = use_mock
        self.scan_interval = int(os.getenv('SCAN_INTERVAL', 300))  # Default 5 minutes
        self.network_interface = os.getenv('NETWORK_INTERFACE', 'eth0')

        # Initialize components
        self.db = DeviceDatabase()
        self.alerts = TelegramAlerts()

        print("🔧 Network Monitor Starting...")
        print(f"   Mode: {'MOCK' if use_mock else 'REAL'}")
        print(f"   Scan Interval: {self.scan_interval} seconds")
        print(f"   Interface: {self.network_interface}")
        print(f"   Telegram: {'Configured' if self.alerts.is_configured() else 'Not Configured'}")
        print()

    def setup(self):
        """Set up database and create necessary directories."""
        # Create data directory
        os.makedirs("data", exist_ok=True)

        # Connect to database
        self.db.connect()
        print("✅ Database connected")

        # Test Telegram if configured
        if self.alerts.is_configured():
            print("📱 Testing Telegram connection...")
            if self.alerts.test_connection():
                print("✅ Telegram alerts ready")
            else:
                print("⚠️  Telegram test failed - alerts may not work")
        else:
            print("⚠️  Telegram not configured - no alerts will be sent")

        print()

    def scan_and_process(self) -> dict:
        """
        Run a network scan and process results.

        Returns:
            Dictionary with scan statistics
        """
        print(f"🔍 Scanning network at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

        # Perform scan
        if self.use_mock:
            devices = mock_scan()
        else:
            # Get IP range from user or use default
            ip_range = os.getenv('NETWORK_RANGE', '192.168.1.0/24')
            devices = scan_network(ip_range)

        print(f"   Found {len(devices)} device(s)")

        # Track statistics
        new_devices = []
        updated_devices = []
        current_macs = []

        # Process each device
        for device in devices:
            current_macs.append(device['mac'])

            # Add or update in database
            is_new = self.db.add_or_update_device(
                ip=device['ip'],
                mac=device['mac'],
                hostname=device.get('hostname', 'Unknown')
            )

            if is_new:
                new_devices.append(device)
                print(f"   🆕 NEW: {device['hostname']} ({device['ip']})")
                # Send alert for new device
                self.alerts.alert_new_device(device)
            else:
                updated_devices.append(device)

        # Mark inactive devices
        self.db.mark_devices_inactive(current_macs)

        # Check for devices that left (were active before, now inactive)
        all_devices = self.db.get_all_devices()
        left_devices = [d for d in all_devices if not d['is_active']]

        # Alert for devices that just left
        for device in left_devices:
            print(f"   👋 LEFT: {device['hostname']} ({device['ip']})")
            self.alerts.alert_device_left(device)

        # Get updated counts
        counts = self.db.get_device_count()

        # Send summary if there were changes
        if new_devices or left_devices:
            self.alerts.alert_scan_complete(
                total_devices=counts['active'],
                new_count=len(new_devices),
                left_count=len(left_devices)
            )

        print(f"   Active: {counts['active']}, Total Ever Seen: {counts['total']}")
        print()

        return {
            'total_found': len(devices),
            'new': len(new_devices),
            'updated': len(updated_devices),
            'left': len(left_devices),
            'active_count': counts['active'],
            'total_count': counts['total']
        }

    def run_once(self):
        """Run a single scan cycle."""
        self.setup()
        stats = self.scan_and_process()
        self.db.close()
        return stats

    def run_continuous(self):
        """Run continuous monitoring loop."""
        self.setup()

        try:
            scan_count = 0
            while True:
                scan_count += 1
                print(f"{'='*60}")
                print(f"Scan #{scan_count}")
                print(f"{'='*60}")

                self.scan_and_process()

                # Wait for next scan
                print(f"⏳ Next scan in {self.scan_interval} seconds...")
                print(f"   (Press Ctrl+C to stop)")
                print()

                time.sleep(self.scan_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping monitor...")
            self.db.close()
            print("✅ Database closed")
            print("👋 Network Monitor stopped")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.db.close()
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Network Device Monitor')
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock data instead of real network scanning'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run a single scan and exit (instead of continuous monitoring)'
    )

    args = parser.parse_args()

    # Create monitor
    monitor = NetworkMonitor(use_mock=args.mock)

    # Run
    if args.once:
        print("Running single scan...\n")
        stats = monitor.run_once()
        print("\n✅ Scan complete!")
        print(f"   Found: {stats['total_found']}")
        print(f"   New: {stats['new']}")
        print(f"   Left: {stats['left']}")
    else:
        print("Starting continuous monitoring...\n")
        monitor.run_continuous()


if __name__ == "__main__":
    main()
