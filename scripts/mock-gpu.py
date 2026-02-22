#!/usr/bin/env python3
"""
Mock GPU Monitor - For testing without actual GPU
Generates mock GPU data to test GPU monitoring functionality on systems
without NVIDIA GPUs installed.

Author: Johnny Minier
Date: February 2026
For: NVIDIA Lab Operations
"""

import csv
import datetime
import time
import random
import argparse
import os


def get_mock_gpu_metrics(num_gpus=8):
    """
    Generate mock GPU data for testing.
    Returns list of dictionaries with GPU data matching nvidia-smi format.
    """
    gpus = []
    for i in range(num_gpus):
        # Generate realistic but random values
        gpu = {
            'index': i,
            'name': f'NVIDIA B200',
            'temperature': round(random.uniform(35, 85), 1),
            'gpu_util': round(random.uniform(0, 100), 1),
            'mem_util': round(random.uniform(0, 100), 1),
            'mem_used': round(random.uniform(0, 192000), 1),
            'mem_total': 192000.0,
            'power_draw': round(random.uniform(100, 1000), 1),
            'power_limit': 1000.0,
        }
        gpus.append(gpu)
    return gpus


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
    print(f"MOCK GPU STATUS - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    print("NOTE: This is MOCK data for testing on systems without GPUs")


def main():
    parser = argparse.ArgumentParser(
        description='Mock GPU Health Monitor - For testing without actual GPU'
    )
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
    parser.add_argument('-n', '--num-gpus', type=int, default=8,
                        help='Number of mock GPUs to simulate (default: 8)')
    
    args = parser.parse_args()
    
    print(f"Mock GPU Health Monitor Starting...")
    print(f"NOTE: This generates MOCK data for testing on systems without GPUs")
    print(f"Log file: {args.log_file}")
    print(f"Interval: {args.interval}s")
    print(f"Mock GPUs: {args.num_gpus}")
    print(f"Thresholds - Temp: {args.temp_threshold}°C, Memory: {args.mem_threshold}%")
    
    iteration = 0
    
    try:
        while True:
            gpus = get_mock_gpu_metrics(num_gpus=args.num_gpus)
            
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