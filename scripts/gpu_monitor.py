#!/usr/bin/env python3
"""
GPU Health Monitor for NVIDIA DGX Systems
Monitors GPU temperature, utilization, memory, and power
Logs to CSV and alerts on threshold violations

Author: Johnny Minier
Date: February 2026
For: NVIDIA Lab Operations
"""

import subprocess
import csv
import datetime
import time
import os
import argparse
from pathlib import Path


def get_gpu_metrics():
    """
    Query nvidia-smi for GPU metrics.
    Returns list of dictionaries with GPU data.
    """
    # nvidia-smi query command
    query_cmd = [
        'nvidia-smi',
        '--query-gpu=index,name,temperature.gpu,utilization.gpu,'
        'utilization.memory,memory.used,memory.total,power.draw,power.limit',
        '--format=csv,noheader,nounits'
    ]
    
    try:
        result = subprocess.run(
            query_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        gpus = []
        for line in result.stdout.strip().split('\n'):
            if line:
                values = [v.strip() for v in line.split(',')]
                gpu = {
                    'index': int(values[0]),
                    'name': values[1],
                    'temperature': float(values[2]) if values[2] != '[N/A]' else None,
                    'gpu_util': float(values[3]) if values[3] != '[N/A]' else None,
                    'mem_util': float(values[4]) if values[4] != '[N/A]' else None,
                    'mem_used': float(values[5]) if values[5] != '[N/A]' else None,
                    'mem_total': float(values[6]) if values[6] != '[N/A]' else None,
                    'power_draw': float(values[7]) if values[7] != '[N/A]' else None,
                    'power_limit': float(values[8]) if values[8] != '[N/A]' else None,
                }
                gpus.append(gpu)
        
        return gpus
    
    except subprocess.CalledProcessError as e:
        print(f"Error running nvidia-smi: {e}")
        return []
    except FileNotFoundError:
        print("nvidia-smi not found. Is NVIDIA driver installed?")
        return []


def check_thresholds(gpu, temp_threshold=80, mem_threshold=90, power_threshold=95):
    """
    Check if GPU metrics exceed thresholds.
    Returns list of alert messages.
    """
    alerts = []
    
    if gpu['temperature'] and gpu['temperature'] > temp_threshold:
        alerts.append(
            f"GPU {gpu['index']}: Temperature {gpu['temperature']}°C "
            f"exceeds {temp_threshold}°C"
        )
    
    if gpu['mem_used'] and gpu['mem_total']:
        mem_percent = (gpu['mem_used'] / gpu['mem_total']) * 100
        if mem_percent > mem_threshold:
            alerts.append(f"GPU {gpu['index']}: Memory {mem_percent:.1f}% exceeds {mem_threshold}%")
    
    if gpu['power_draw'] and gpu['power_limit']:
        power_percent = (gpu['power_draw'] / gpu['power_limit']) * 100
        if power_percent > power_threshold:
            alerts.append(
                f"GPU {gpu['index']}: Power {power_percent:.1f}% "
                f"exceeds {power_threshold}%"
            )
    
    return alerts


def log_to_csv(gpus, log_file):
    """
    Append GPU metrics to CSV log file.
    Creates file with headers if it doesn't exist.
    """
    file_exists = os.path.exists(log_file)
    
    with open(log_file, 'a', newline='') as f:
        fieldnames = [
            'timestamp', 'gpu_index', 'gpu_name', 'temperature_c', 
            'gpu_util_percent', 'mem_util_percent', 'mem_used_mb', 
            'mem_total_mb', 'power_draw_w', 'power_limit_w'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        timestamp = datetime.datetime.now().isoformat()
        
        for gpu in gpus:
            row = {
                'timestamp': timestamp,
                'gpu_index': gpu['index'],
                'gpu_name': gpu['name'],
                'temperature_c': gpu['temperature'],
                'gpu_util_percent': gpu['gpu_util'],
                'mem_util_percent': gpu['mem_util'],
                'mem_used_mb': gpu['mem_used'],
                'mem_total_mb': gpu['mem_total'],
                'power_draw_w': gpu['power_draw'],
                'power_limit_w': gpu['power_limit'],
            }
            writer.writerow(row)


def print_status(gpus):
    """
    Print formatted GPU status to console.
    """
    print("\n" + "="*80)
    print(f"GPU STATUS - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print(f"{'GPU':<5} {'Name':<20} {'Temp':<8} {'GPU%':<8} {'Mem%':<8} {'Power':<15}")
    print("-"*80)
    
    for gpu in gpus:
        mem_percent = 0
        if gpu['mem_used'] and gpu['mem_total']:
            mem_percent = (gpu['mem_used'] / gpu['mem_total']) * 100
        
        if gpu['power_draw']:
            power_str = f"{gpu['power_draw']:.0f}W/{gpu['power_limit']:.0f}W"
        else:
            power_str = "N/A"
        
        print(f"{gpu['index']:<5} {gpu['name'][:20]:<20} {gpu['temperature']:<8.0f} "
              f"{gpu['gpu_util']:<8.0f} {mem_percent:<8.1f} {power_str:<15}")
    
    print("="*80)


def main():
    parser = argparse.ArgumentParser(description='GPU Health Monitor for NVIDIA DGX')
    parser.add_argument('-i', '--interval', type=int, default=60,
                        help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('-l', '--log-file', type=str, default='gpu_metrics.csv',
                        help='CSV log file path (default: gpu_metrics.csv)')
    parser.add_argument('-t', '--temp-threshold', type=int, default=80,
                        help='Temperature alert threshold in °C (default: 80)')
    parser.add_argument('-m', '--mem-threshold', type=int, default=90,
                        help='Memory usage alert threshold in %% (default: 90)')
    parser.add_argument('-c', '--count', type=int, default=0,
                        help='Number of iterations (0 = infinite, default: 0)')
    parser.add_argument('-o', '--once', action='store_true',
                        help='Run once and exit')
    
    args = parser.parse_args()
    
    print(f"GPU Health Monitor Starting...")
    print(f"Log file: {args.log_file}")
    print(f"Interval: {args.interval}s")
    print(f"Thresholds - Temp: {args.temp_threshold}°C, Memory: {args.mem_threshold}%")
    
    iteration = 0
    
    try:
        while True:
            gpus = get_gpu_metrics()
            
            if gpus:
                # Print status to console
                print_status(gpus)
                
                # Log to CSV
                log_to_csv(gpus, args.log_file)
                
                # Check thresholds and print alerts
                for gpu in gpus:
                    alerts = check_thresholds(
                        gpu, 
                        temp_threshold=args.temp_threshold,
                        mem_threshold=args.mem_threshold
                    )
                    for alert in alerts:
                        print(f"⚠️  ALERT: {alert}")
            else:
                print("No GPU data available")
            
            iteration += 1
            
            # Exit conditions
            if args.once:
                break
            if args.count > 0 and iteration >= args.count:
                break
            
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    
    print(f"Total iterations: {iteration}")
    print(f"Log saved to: {args.log_file}")


if __name__ == '__main__':
    main()

