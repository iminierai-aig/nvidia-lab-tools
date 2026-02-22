# NVIDIA Lab Operations Tools

A comprehensive Python toolkit for managing and monitoring NVIDIA DGX lab infrastructure. These scripts provide automated monitoring, log analysis, and inventory management capabilities for lab operations teams.

**Author:** Johnny Minier  
**Date:** February 2026  
**For:** NVIDIA Lab Operations

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Scripts](#scripts)
  - [GPU Health Monitor](#1-gpu-health-monitor-gpu_monitorpy)
  - [Log Parser](#2-log-parser-log_parserpy)
  - [Inventory Tracker](#3-inventory-tracker-inventory_trackerpy)
- [Usage Examples](#usage-examples)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)

---

## Overview

This toolkit consists of three main utilities designed to streamline NVIDIA DGX lab operations:

1. **GPU Health Monitor** - Real-time monitoring of GPU metrics with alerting
2. **Log Parser** - Automated analysis of system logs for GPU-related issues
3. **Inventory Tracker** - Hardware asset management with CRUD operations

All scripts are written in Python 3 and use only the standard library (no external dependencies required).

---

## Prerequisites

- **Python 3.6+** (tested with Python 3.8+)
- **NVIDIA GPU drivers** (for `gpu_monitor.py` - requires `nvidia-smi` command)
- **Linux environment** (designed for DGX systems running Linux)
- **Read access** to system logs (for `log_parser.py`)

---

## Installation

1. Clone or download this repository:
   ```bash
   git clone <repository-url>
   cd nvidia-lab-tools
   ```

2. Verify Python installation:
   ```bash
   python3 --version
   ```

3. Make scripts executable (optional):
   ```bash
   chmod +x gpu_monitor.py log_parser.py inventory_tracker.py
   ```

4. Verify NVIDIA drivers (for GPU monitoring):
   ```bash
   nvidia-smi
   ```

**Note:** No additional Python packages are required - all scripts use the standard library only.

---

## Scripts

### 1. GPU Health Monitor (`gpu_monitor.py`)

Monitors GPU health metrics including temperature, utilization, memory usage, and power consumption. Continuously logs data to CSV and provides real-time alerts when thresholds are exceeded.

#### Features

- Real-time GPU metrics collection via `nvidia-smi`
- Configurable monitoring intervals
- Customizable alert thresholds (temperature, memory, power)
- CSV logging with timestamps
- Console output with formatted status tables
- Support for single-run or continuous monitoring

#### Metrics Tracked

- GPU temperature (°C)
- GPU utilization (%)
- Memory utilization (%)
- Memory used/total (MB)
- Power draw/limit (W)

#### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--interval` | `-i` | Monitoring interval in seconds | 60 |
| `--log-file` | `-l` | CSV log file path | `gpu_metrics.csv` |
| `--temp-threshold` | `-t` | Temperature alert threshold (°C) | 80 |
| `--mem-threshold` | `-m` | Memory usage alert threshold (%) | 90 |
| `--count` | `-c` | Number of iterations (0 = infinite) | 0 |
| `--once` | | Run once and exit | False |

#### Usage Examples

```bash
# Run once and exit (quick health check)
python gpu_monitor.py --once

# Monitor every 30 seconds
python gpu_monitor.py -i 30

# Monitor with custom thresholds (temp: 75°C, memory: 85%)
python gpu_monitor.py -i 60 -t 75 -m 85

# Run 10 iterations then stop
python gpu_monitor.py -i 10 -c 10

# Custom log file location
python gpu_monitor.py -l /var/log/gpu_metrics.csv

# Continuous monitoring with custom settings
python gpu_monitor.py -i 30 -t 80 -m 90 -l /var/log/gpu_monitor.csv
```

#### Output

- **Console:** Formatted table showing GPU status with alerts
- **CSV File:** Timestamped metrics for all GPUs (one row per GPU per iteration)

---

### 2. Log Parser (`log_parser.py`)

Analyzes system logs to identify GPU-related errors, warnings, and issues. Detects NVIDIA Xid errors, ECC errors, PCIe issues, and other critical events.

#### Features

- Parses multiple log sources (dmesg, syslog, custom files/directories)
- Pattern matching for errors, warnings, and GPU-specific issues
- NVIDIA Xid error code detection and description
- Summary statistics and categorized findings
- Detailed CSV export option
- Text report generation

#### Detected Patterns

- **Errors:** General error messages
- **Warnings:** Warning messages
- **NVIDIA:** GPU/CUDA/NCCL/NVLink related entries
- **Xid Errors:** NVIDIA-specific error codes (13, 31, 32, 43, 48, 56, 74, 79, 92, 94, 95, etc.)
- **Temperature:** Thermal issues
- **Memory:** ECC errors, OOM conditions
- **PCIe:** PCI Express link issues

#### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--file` | `-f` | Parse a specific log file |
| `--directory` | `-d` | Parse all logs in directory |
| `--pattern` | `-p` | File pattern for directory parsing | `*.log` |
| `--dmesg` | | Parse dmesg output |
| `--syslog` | | Parse common system log locations |
| `--output` | `-o` | Output report file | `log_report.txt` |
| `--csv` | | Save detailed findings to CSV |

#### Usage Examples

```bash
# Parse dmesg for GPU errors
python log_parser.py --dmesg

# Parse a specific log file
python log_parser.py -f /var/log/syslog

# Parse all logs in a directory
python log_parser.py -d /var/log/ -p "*.log"

# Parse common system logs
python log_parser.py --syslog

# Save detailed CSV output
python log_parser.py --dmesg --csv detailed_findings.csv

# Combine multiple sources with custom output
python log_parser.py --dmesg --syslog -o full_report.txt

# Comprehensive analysis
python log_parser.py --dmesg --syslog -d /var/log/ -p "*.log" -o comprehensive_report.txt --csv findings.csv
```

#### Output

- **Console:** Summary report with statistics and critical findings
- **Report File:** Detailed text report (default: `log_report.txt`)
- **CSV File:** Detailed findings with line numbers (optional)

---

### 3. Inventory Tracker (`inventory_tracker.py`)

Hardware inventory management system for tracking lab assets including servers, GPUs, switches, cables, PDUs, and storage devices.

#### Features

- Full CRUD operations (Create, Read, Update, Delete)
- Asset search and filtering
- Status tracking (active, maintenance, retired, spare)
- Location management
- Serial number tracking
- Summary statistics
- CSV export functionality
- Demo data generation

#### Supported Asset Types

- `server` - DGX servers and compute nodes
- `gpu` - Individual GPU units
- `switch` - Network switches (InfiniBand, Ethernet)
- `cable` - Cables and interconnects
- `pdu` - Power distribution units
- `storage` - Storage systems
- `other` - Miscellaneous equipment

#### Asset Status Options

- `active` - Currently in use
- `maintenance` - Under maintenance
- `retired` - No longer in service
- `spare` - Available spare equipment

#### Commands

| Command | Description |
|---------|-------------|
| `demo` | Initialize with demo data |
| `list` | List all assets (with optional filters) |
| `add` | Add a new asset |
| `update` | Update an existing asset |
| `delete` | Delete an asset |
| `search` | Search assets by query |
| `show` | Show detailed asset information |
| `summary` | Display inventory statistics |
| `export` | Export inventory to CSV |

#### Usage Examples

```bash
# Initialize with demo data
python inventory_tracker.py demo

# List all assets
python inventory_tracker.py list

# List only servers
python inventory_tracker.py list --type server

# List assets in maintenance
python inventory_tracker.py list --status maintenance

# Add a new asset
python inventory_tracker.py add --type server --name "DGX-B200-05" --location "Rack B2" --serial "DGX-SN-005"

# Add asset with notes
python inventory_tracker.py add --type switch --name "Quantum-2 IB Switch" --location "Rack A1, U41" --serial "QM2-002" --notes "400G InfiniBand switch"

# Search for assets
python inventory_tracker.py search "DGX"
python inventory_tracker.py search "Rack A1"

# Show asset details
python inventory_tracker.py show ASSET-0001

# Update an asset
python inventory_tracker.py update ASSET-0001 --status maintenance --notes "Scheduled for upgrade"

# Update asset location
python inventory_tracker.py update ASSET-0001 --location "Rack B2, U1-10"

# View summary statistics
python inventory_tracker.py summary

# Export to CSV
python inventory_tracker.py export -o inventory_backup.csv

# Use custom inventory file
python inventory_tracker.py -f custom_inventory.json list
```

#### Data Storage

- **Format:** JSON file (default: `inventory.json`)
- **Structure:** Includes metadata (created/modified timestamps) and asset array
- **Backup:** Use `export` command to create CSV backups

---

## Usage Examples

### Complete Monitoring Workflow

```bash
# 1. Check GPU health
python gpu_monitor.py --once

# 2. Analyze system logs for issues
python log_parser.py --dmesg --syslog -o health_check.txt

# 3. Check inventory for maintenance schedules
python inventory_tracker.py list --status maintenance
```

### Daily Operations

```bash
# Continuous GPU monitoring (runs in background)
nohup python gpu_monitor.py -i 60 -l /var/log/gpu_metrics.csv > /dev/null 2>&1 &

# Weekly log analysis
python log_parser.py --syslog -d /var/log/ -o weekly_report.txt --csv weekly_findings.csv

# Update asset status after maintenance
python inventory_tracker.py update ASSET-0003 --status active --notes "Maintenance completed"
```

---

## Output Files

### GPU Monitor

- **`gpu_metrics.csv`** (default) - Timestamped GPU metrics
  - Columns: `timestamp`, `gpu_index`, `gpu_name`, `temperature_c`, `gpu_util_percent`, `mem_util_percent`, `mem_used_mb`, `mem_total_mb`, `power_draw_w`, `power_limit_w`

### Log Parser

- **`log_report.txt`** (default) - Summary report with statistics and findings
- **`detailed_findings.csv`** (optional) - Detailed CSV with all matched log entries

### Inventory Tracker

- **`inventory.json`** (default) - JSON database of all assets
- **`inventory_export.csv`** (export) - CSV backup/export of inventory

---

## Troubleshooting

### GPU Monitor Issues

**Problem:** `nvidia-smi not found`  
**Solution:** Ensure NVIDIA drivers are installed and `nvidia-smi` is in PATH

**Problem:** No GPU data available  
**Solution:** Check GPU visibility with `nvidia-smi` command manually

**Problem:** Permission denied writing log file  
**Solution:** Use a writable directory or run with appropriate permissions

### Log Parser Issues

**Problem:** Permission denied reading log files  
**Solution:** Run with `sudo` or ensure read access to log directories

**Problem:** No findings in report  
**Solution:** Verify log files contain relevant entries, try different log sources

### Inventory Tracker Issues

**Problem:** JSON decode error  
**Solution:** Backup and recreate `inventory.json` if corrupted, or use `demo` command

**Problem:** Asset not found  
**Solution:** Use `list` command to see all asset IDs

---

## Notes

- All scripts are designed to be run from the command line
- Scripts use Python standard library only - no pip install required
- GPU monitor requires NVIDIA drivers and `nvidia-smi` command
- Log parser may require elevated permissions for system log access
- Inventory data is stored locally in JSON format
- CSV exports can be used for backup and external analysis

---

## License

This toolkit is provided for NVIDIA Lab Operations internal use.

---

## Support

For issues or questions, contact the NVIDIA Lab Operations team.