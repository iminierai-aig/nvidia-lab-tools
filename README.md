# NVIDIA Lab Operations Tools

Python automation scripts for NVIDIA DGX lab management.

A collection of GPU monitoring, health checking, and automation tools designed for datacenter operations with NVIDIA GPUs.

## Overview

- **Real-time Dashboard** – Web-based monitoring with historical charts (`dashboards/`)
- **Health Check Automation** – Cron-ready scripts with alerting
- **DCGM Integration** – Enterprise GPU management support
- **Jira Integration** – Automated ticket creation for GPU events (`jira/`)

Built and tested on Dell PowerEdge R640 with NVIDIA T4 (16GB); compatible with DGX systems, A100, H100, and Blackwell (B200) GPUs.

## Quick Start

```bash
pip install -r requirements.txt
python scripts/health_check.py
python dashboards/app.py
```

## Scripts

### 1. GPU Health Monitor (`gpu_monitor.py`)
Monitor GPU temperature, utilization, memory, and power.
Logs metrics to CSV and alerts on threshold violations.

```bash
python gpu_monitor.py --once           # Run once
python gpu_monitor.py -i 30            # Monitor every 30 seconds
python gpu_monitor.py -t 75 -m 85      # Custom thresholds

## How To Use GPU Monitor

# Run once and exit
python gpu_monitor.py --once

# Monitor every 30 seconds
python gpu_monitor.py -i 30

# Monitor with custom thresholds
python gpu_monitor.py -i 60 -t 75 -m 85

# Run 10 iterations then stop
python gpu_monitor.py -i 10 -c 10

# Custom log file
python gpu_monitor.py -l /var/log/gpu_metrics.csv

## How To Use Log Parser

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

# Combine multiple sources
python log_parser.py --dmesg --syslog -o full_report.txt


## How To Use Inventory Tracker

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

# Search for assets
python inventory_tracker.py search "DGX"
python inventory_tracker.py search "Rack A1"

# Show asset details
python inventory_tracker.py show ASSET-0001

# Update an asset
python inventory_tracker.py update ASSET-0001 --status maintenance --notes "Scheduled for upgrade"

# View summary
python inventory_tracker.py summary

# Export to CSV
python inventory_tracker.py export -o inventory_backup.csv

