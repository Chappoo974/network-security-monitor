# Network and Security Monitor

A Python-based network monitoring tool that scans your local network, tracks known devices, and alerts you when unknown devices connect.

## 🎯 What This Project Does

- Scans your home/local network to discover connected devices
- Identifies devices by IP address, MAC address, and vendor
- Stores known devices in a SQLite database
- Sends alerts via Telegram when unknown devices are detected
- Monitors open ports on critical devices
- Provides a web dashboard to view network status

## 🚀 Features

- [x] Network scanning with ARP
- [x] Device identification (IP, MAC, hostname)
- [x] SQLite database for device tracking
- [x] Telegram bot alerts
- [ ] Port scanning (planned)
- [ ] Flask web dashboard (planned)
- [ ] Docker containerization (planned)

## 🛠️ Tech Stack

- **Python 3.x** - Core programming language
- **Scapy** - Network packet manipulation and ARP scanning
- **SQLite** - Lightweight database for device storage
- **Flask** - Web framework for dashboard
- **Docker** - Containerization
- **Telegram Bot API** - Alert notifications

## 📋 Prerequisites

- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- A network you own or have permission to scan
- Telegram account (for alerts)

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Project\ 1
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
nano .env  # Or use your preferred editor
```

Update these values in `.env`:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather) on Telegram
- `TELEGRAM_CHAT_ID` - Your chat ID (use [@userinfobot](https://t.me/userinfobot) to find it)
- `NETWORK_RANGE` - Your network range (e.g., `192.168.1.0/24`)
- `SCAN_INTERVAL` - How often to scan in seconds (default: 300)

## 🎮 Usage

### Test Mode (No Network Access Required)

Run with mock data to test without scanning:

```bash
python monitor.py --mock --once
```

### Single Scan

Run one scan and exit:

```bash
python monitor.py --once
```

### Continuous Monitoring

Run continuous network monitoring (scans every 5 minutes by default):

```bash
python monitor.py
```

Press `Ctrl+C` to stop.

### Real Network Scanning

**Note:** Real network scanning requires elevated privileges on some systems.

```bash
sudo python monitor.py --once
```

## 📊 What It Does

1. **Scans your network** - Uses ARP protocol to discover devices
2. **Tracks devices** - Stores device info in SQLite database (`data/devices.db`)
3. **Detects changes** - Alerts when:
   - New devices join the network
   - Known devices leave the network
4. **Sends notifications** - Pushes alerts to your Telegram

## 📁 Project Structure

```
Project 1/
├── monitor.py          # Main entry point
├── src/
│   ├── scanner.py      # Network scanning logic
│   ├── database.py     # SQLite database management
│   └── alerts.py       # Telegram alert system
├── data/               # Database storage
├── .env                # Configuration (not in git)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔒 Security & Ethics

**IMPORTANT:** Only scan networks you own or have explicit permission to scan. Unauthorized network scanning may be illegal in your jurisdiction.

This tool is for educational purposes and personal network monitoring only.

## 📚 What I Learned

(This section will be filled in as the project progresses)

- Network protocols (ARP, TCP/IP)
- Python security libraries
- Database design and SQLite
- API integration (Telegram)
- Web development with Flask
- Docker containerization
- Git version control

## 📝 License

This project is for educational purposes.

## 👤 Author

Built as part of my cybersecurity learning journey.
