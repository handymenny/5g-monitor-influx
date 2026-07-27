# 5G Monitor InfluxDB Exporter

Monitor 5G/cellular modem metrics via SSH AT commands and export them in InfluxDB line protocol format. Perfect for integration with Telegraf, InfluxDB, and monitoring stacks.

The project was inspired by [quectel-5g-tools](https://github.com/vjt/quectel-5g-tools).

## Features

- **SSH-based AT command execution** on remote Quectel modems
- **InfluxDB line protocol output** for seamless ingestion
- **Flexible configuration** with YAML config files
- **Support for multiple cellular metrics**: signal strength (RSRP, RSRQ, SINR), cell information (PCI, Cell ID, TAC), and more
- **Static and derived tags** for easy metric organization
- **Debug mode** for troubleshooting AT command responses
- **Telegraf integration** ready

## Requirements

- Python 3.10 or higher
- SSH access to a Quectel modem
- Dependencies: `paramiko`, `pyyaml`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/handymenny/5g-monitor-influx.git
cd 5g-monitor-influx
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create or edit `config/export_config.yaml` with your modem details:

```yaml
# SSH Connection Settings
ssh_host: 192.168.1.1          # Modem IP address
ssh_user: root                 # SSH username
ssh_port: 22                   # SSH port
ssh_password: your_password    # SSH password
timeout: 10.0                  # Command timeout in seconds

# InfluxDB Measurement
measurement: modem_cells       # InfluxDB measurement name

# Static tags (applied to all metrics)
static_tags:
  host: 192.168.1.1           # Modem identifier
  model: NR7302               # Modem model
  location: site-a            # Optional: deployment location

# Allowed fields to collect
allowed_fields:
  - pci                        # Physical Cell ID
  - rsrp                       # Reference Signal Received Power
  - rsrq                       # Reference Signal Received Quality
  - sinr                       # Signal-to-Interference + Noise Ratio
  - rssi                       # Received Signal Strength Indicator
  - arfcn                      # Absolute Radio Frequency Channel Number
  - band                       # Cellular band
  - dl_bandwidth              # Downlink bandwidth
  - cell_id                    # Cell ID
  - tac                        # Tracking Area Code
  - state                      # Cell state

# Derived tags (extracted from metric data)
derived_tags:
  carrier_idx: carrier_idx     # Carrier index
  type: type                   # Cell type
  pci: pci                     # Physical Cell ID
  arfcn: arfcn                # ARFCN
```

## Usage

### Basic Usage

Run the exporter with default configuration:

```bash
python src/main.py
```

Or specify a custom config file:

```bash
python src/main.py --config config/export_config.yaml
```

### Debug Mode

Enable debug output to see raw AT command responses:

```bash
python src/main.py --debug
```

## Integration with Telegraf

Configure Telegraf's `exec` input plugin to collect metrics:

```toml
[[inputs.exec]]
  commands = ["python /path/to/5g-monitor-influx/src/main.py --config /path/to/config.yaml"]
  interval = "60s"
  timeout = "15s"
  data_format = "influx"
```

## Project Structure

```
src/
├── main.py                     # Entry point
└── monitor/
    ├── config/                 # Configuration handling
    ├── export/                 # InfluxDB export logic
    ├── model/                  # Data models and mappings
    ├── parsing/                # AT command response parsing
    └── runner/                 # Monitoring execution engine
```


## License

See LICENSE file for details.
