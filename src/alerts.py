"""
Alert module for sending notifications via Telegram.
Notifies when devices join or leave the network.
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv


class TelegramAlerts:
    """Handles sending alerts via Telegram bot."""

    def __init__(self):
        """Initialize Telegram bot with credentials from .env file."""
        load_dotenv()

        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.alert_on_new = os.getenv('ALERT_ON_NEW_DEVICE', 'true').lower() == 'true'
        self.alert_on_port = os.getenv('ALERT_ON_PORT_CHANGE', 'true').lower() == 'true'

        # Telegram API endpoint
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def is_configured(self) -> bool:
        """
        Check if Telegram is properly configured.

        Returns:
            True if bot token and chat ID are set
        """
        return (self.bot_token and
                self.bot_token != 'your_bot_token_here' and
                self.chat_id and
                self.chat_id != 'your_chat_id_here')

    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message via Telegram.

        Args:
            message: The message text to send
            parse_mode: Format of the message (Markdown or HTML)

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_configured():
            print("⚠️  Telegram not configured - message not sent")
            print(f"Message: {message}")
            return False

        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }

            response = requests.post(self.api_url, json=payload, timeout=10)

            if response.status_code == 200:
                return True
            else:
                print(f"❌ Telegram API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False

    def alert_new_device(self, device: Dict) -> bool:
        """
        Send alert when a new device joins the network.

        Args:
            device: Dictionary with device info (ip, mac, hostname)

        Returns:
            True if alert sent successfully
        """
        if not self.alert_on_new:
            return False

        message = f"""
🆕 *New Device Detected*

📱 *Hostname:* {device.get('hostname', 'Unknown')}
🌐 *IP Address:* `{device['ip']}`
🔧 *MAC Address:* `{device['mac']}`
⏰ *Time:* {device.get('first_seen', 'Unknown')}
"""
        return self.send_message(message.strip())

    def alert_device_left(self, device: Dict) -> bool:
        """
        Send alert when a device leaves the network.

        Args:
            device: Dictionary with device info (ip, mac, hostname)

        Returns:
            True if alert sent successfully
        """
        if not self.alert_on_new:  # Using same setting for now
            return False

        message = f"""
👋 *Device Disconnected*

📱 *Hostname:* {device.get('hostname', 'Unknown')}
🌐 *IP Address:* `{device['ip']}`
🔧 *MAC Address:* `{device['mac']}`
⏰ *Last Seen:* {device.get('last_seen', 'Unknown')}
"""
        return self.send_message(message.strip())

    def alert_scan_complete(self, total_devices: int, new_count: int = 0, left_count: int = 0) -> bool:
        """
        Send summary alert after a scan completes.

        Args:
            total_devices: Total active devices found
            new_count: Number of new devices
            left_count: Number of devices that left

        Returns:
            True if alert sent successfully
        """
        # Only send if there were changes
        if new_count == 0 and left_count == 0:
            return False

        message = f"""
🔍 *Network Scan Complete*

✅ *Active Devices:* {total_devices}
🆕 *New Devices:* {new_count}
👋 *Devices Left:* {left_count}
"""
        return self.send_message(message.strip())

    def test_connection(self) -> bool:
        """
        Test Telegram connection by sending a test message.

        Returns:
            True if connection successful
        """
        if not self.is_configured():
            print("❌ Telegram not configured!")
            print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
            return False

        message = "✅ *Network Monitor Connected*\n\nYour Telegram alerts are working!"
        success = self.send_message(message)

        if success:
            print("✅ Telegram connection successful!")
        else:
            print("❌ Failed to send test message")

        return success


# Test code
if __name__ == "__main__":
    print("Testing Telegram Alerts...\n")

    alerts = TelegramAlerts()

    # Check configuration
    print(f"Configured: {alerts.is_configured()}")
    print(f"Alert on new devices: {alerts.alert_on_new}")
    print(f"Alert on port changes: {alerts.alert_on_port}\n")

    if alerts.is_configured():
        # Test connection
        print("Sending test message...")
        alerts.test_connection()

        # Test new device alert
        print("\nTesting new device alert...")
        test_device = {
            'ip': '192.168.1.100',
            'mac': 'AA:BB:CC:DD:EE:FF',
            'hostname': 'test-device',
            'first_seen': '2026-11-09 10:15:00'
        }
        alerts.alert_new_device(test_device)

        # Test scan complete alert
        print("\nTesting scan complete alert...")
        alerts.alert_scan_complete(total_devices=5, new_count=1, left_count=0)
    else:
        print("⚠️  Telegram not configured - using placeholder values")
        print("Update .env file with real credentials to test")
