#!/usr/bin/env python3
"""
GPU Monitor - Local T4 Edition
Real hardware monitoring for Dell R640 + NVIDIA T4

Author: [Your Name]
Hardware: Dell R640, NVIDIA T4 16GB
Date: [Today's Date]
"""

import subprocess
import csv
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import os

class T4Monitor:
    """Monitor NVIDIA T4 GPU on local hardware."""
    
    # T4 Specifications
    T4_SPECS = {
        'name': 'NVIDIA T4',
        'memory_gb': 16,
        'tdp_watts': 70,
        'cuda_cores': 2560,
        'tensor_cores': 320,
        'architecture': 'Turing',
        'compute_capability': '7.5'
    }
    
    # Alert thresholds for T4
    THRESHOLDS = {
        'temp_warning': 75,
        'temp_critical': 85,
        'power_warning': 63,      # 90% of 70W
        'power_critical': 67,     # 95% of 70W
        'memory_warning': 14336,  # 14GB (87.5% of 16GB)
        'memory_critical': 15360  # 15GB (93.75% of 16GB)
    }
    
    def __init__(self):
        self.verify_gpu()
    
    def verify_gpu(self):
        """Verify T4 is present and accessible."""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True, text=True, timeout=10
            )
            gpu_name = result.stdout.strip()
            if 'T4' not in gpu_name:
                print(f"[WARN] Expected T4, found: {gpu_name}")
            else:
                print(f"[OK] GPU detected: {gpu_name}")
        except Exception as e:
            print(f"[ERROR] Cannot access GPU: {e}")
            raise
    
    def get_metrics(self) -> Dict:
        """Get current GPU metrics via nvidia-smi."""
        query = [
            'nvidia-smi',
            '--query-gpu=timestamp,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw,power.limit,pstate,fan.speed,clocks.sm,clocks.mem',
            '--format=csv,noheader,nounits'
        ]
        
        result = subprocess.run(query, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise RuntimeError(f"nvidia-smi failed: {result.stderr}")
        
        values = result.stdout.strip().split(', ')
        
        return {
            'timestamp': values[0],
            'name': values[1],
            'temperature': int(values[2]),
            'gpu_util': int(values[3]),
            'mem_util': int(values[4]),
            'memory_used': int(values[5]),
            'memory_total': int(values[6]),
            'power_draw': float(values[7]),
            'power_limit': float(values[8]),
            'pstate': values[9],
            'fan_speed': values[10],  # T4 is passively cooled, may show N/A
            'sm_clock': int(values[11]),
            'mem_clock': int(values[12])
        }
    
    def get_processes(self) -> List[Dict]:
        """Get GPU processes."""
        query = [
            'nvidia-smi',
            '--query-compute-apps=pid,process_name,used_memory',
            '--format=csv,noheader,nounits'
        ]
        
        result = subprocess.run(query, capture_output=True, text=True, timeout=10)
        
        processes = []
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                parts = line.split(', ')
                if len(parts) >= 3:
                    processes.append({
                        'pid': int(parts[0]),
                        'name': parts[1],
                        'memory_mb': int(parts[2])
                    })
        return processes
    
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check metrics against T4 thresholds."""
        alerts = []
        
        # Temperature
        if metrics['temperature'] >= self.THRESHOLDS['temp_critical']:
            alerts.append({
                'level': 'CRITICAL',
                'metric': 'temperature',
                'value': metrics['temperature'],
                'threshold': self.THRESHOLDS['temp_critical'],
                'message': f"Temperature CRITICAL: {metrics['temperature']}°C"
            })
        elif metrics['temperature'] >= self.THRESHOLDS['temp_warning']:
            alerts.append({
                'level': 'WARNING',
                'metric': 'temperature',
                'value': metrics['temperature'],
                'threshold': self.THRESHOLDS['temp_warning'],
                'message': f"Temperature WARNING: {metrics['temperature']}°C"
            })
        
        # Power
        if metrics['power_draw'] >= self.THRESHOLDS['power_critical']:
            alerts.append({
                'level': 'CRITICAL',
                'metric': 'power',
                'value': metrics['power_draw'],
                'threshold': self.THRESHOLDS['power_critical'],
                'message': f"Power CRITICAL: {metrics['power_draw']}W"
            })
        elif metrics['power_draw'] >= self.THRESHOLDS['power_warning']:
            alerts.append({
                'level': 'WARNING',
                'metric': 'power',
                'value': metrics['power_draw'],
                'threshold': self.THRESHOLDS['power_warning'],
                'message': f"Power WARNING: {metrics['power_draw']}W"
            })
        
        # Memory
        if metrics['memory_used'] >= self.THRESHOLDS['memory_critical']:
            alerts.append({
                'level': 'CRITICAL',
                'metric': 'memory',
                'value': metrics['memory_used'],
                'threshold': self.THRESHOLDS['memory_critical'],
                'message': f"Memory CRITICAL: {metrics['memory_used']}MB"
            })
        elif metrics['memory_used'] >= self.THRESHOLDS['memory_warning']:
            alerts.append({
                'level': 'WARNING',
                'metric': 'memory',
                'value': metrics['memory_used'],
                'threshold': self.THRESHOLDS['memory_warning'],
                'message': f"Memory WARNING: {metrics['memory_used']}MB"
            })
        
        return alerts
    
    def print_status(self, metrics: Dict, alerts: List[Dict]):
        """Print formatted status."""
        print(f"\n{'='*60}")
        print(f"  NVIDIA T4 Status - {metrics['timestamp']}")
        print(f"{'='*60}")
        print(f"  Temperature:  {metrics['temperature']:3}°C    Power:     {metrics['power_draw']:5.1f}W / {metrics['power_limit']:.0f}W")
        print(f"  GPU Util:     {metrics['gpu_util']:3}%     Memory:    {metrics['memory_used']:5}MB / {metrics['memory_total']}MB")
        print(f"  Mem Util:     {metrics['mem_util']:3}%     P-State:   {metrics['pstate']}")
        print(f"  SM Clock:     {metrics['sm_clock']:4} MHz  Mem Clock: {metrics['mem_clock']} MHz")
        
        if alerts:
            print(f"\n  {'!'*20} ALERTS {'!'*20}")
            for alert in alerts:
                print(f"  [{alert['level']}] {alert['message']}")
        else:
            print(f"\n  [OK] All metrics within normal range")
        
        print(f"{'='*60}")
    
    def monitor_loop(self, interval: int = 2, duration: int = None, csv_file: str = None):
        """Continuous monitoring loop."""
        print(f"Starting T4 monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        csv_writer = None
        if csv_file:
            f = open(csv_file, 'w', newline='')
            csv_writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'temperature', 'gpu_util', 'mem_util',
                'memory_used', 'power_draw', 'sm_clock', 'pstate'
            ])
            csv_writer.writeheader()
            print(f"Logging to: {csv_file}")
        
        start_time = time.time()
        
        try:
            while True:
                metrics = self.get_metrics()
                alerts = self.check_alerts(metrics)
                
                # Clear screen and print
                os.system('clear')
                self.print_status(metrics, alerts)
                
                # Show processes
                processes = self.get_processes()
                if processes:
                    print(f"\n  Active GPU Processes:")
                    for proc in processes:
                        print(f"    PID {proc['pid']:6}: {proc['name'][:30]:30} {proc['memory_mb']:6}MB")
                
                # Log to CSV
                if csv_writer:
                    csv_writer.writerow({
                        'timestamp': metrics['timestamp'],
                        'temperature': metrics['temperature'],
                        'gpu_util': metrics['gpu_util'],
                        'mem_util': metrics['mem_util'],
                        'memory_used': metrics['memory_used'],
                        'power_draw': metrics['power_draw'],
                        'sm_clock': metrics['sm_clock'],
                        'pstate': metrics['pstate']
                    })
                    f.flush()
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    print(f"\nMonitoring complete ({duration}s)")
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
        
        finally:
            if csv_file:
                f.close()
                print(f"Log saved to: {csv_file}")
    
    def single_check(self):
        """Single status check."""
        metrics = self.get_metrics()
        alerts = self.check_alerts(metrics)
        self.print_status(metrics, alerts)
        return len(alerts) == 0
    
    def generate_report(self) -> str:
        """Generate a full status report."""
        metrics = self.get_metrics()
        alerts = self.check_alerts(metrics)
        processes = self.get_processes()
        
        report = []
        report.append("=" * 60)
        report.append("NVIDIA T4 HEALTH REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Host: {os.uname().nodename}")
        report.append("=" * 60)
        
        report.append("\n--- GPU Information ---")
        report.append(f"  Model: {metrics['name']}")
        report.append(f"  Architecture: {self.T4_SPECS['architecture']}")
        report.append(f"  CUDA Cores: {self.T4_SPECS['cuda_cores']}")
        report.append(f"  Tensor Cores: {self.T4_SPECS['tensor_cores']}")
        report.append(f"  Memory: {self.T4_SPECS['memory_gb']} GB GDDR6")
        report.append(f"  TDP: {self.T4_SPECS['tdp_watts']}W")
        
        report.append("\n--- Current Metrics ---")
        report.append(f"  Temperature: {metrics['temperature']}°C")
        report.append(f"  Power Draw: {metrics['power_draw']}W / {metrics['power_limit']}W")
        report.append(f"  GPU Utilization: {metrics['gpu_util']}%")
        report.append(f"  Memory Utilization: {metrics['mem_util']}%")
        report.append(f"  Memory Used: {metrics['memory_used']}MB / {metrics['memory_total']}MB")
        report.append(f"  SM Clock: {metrics['sm_clock']} MHz")
        report.append(f"  Memory Clock: {metrics['mem_clock']} MHz")
        report.append(f"  Performance State: {metrics['pstate']}")
        
        report.append("\n--- Alerts ---")
        if alerts:
            for alert in alerts:
                report.append(f"  [{alert['level']}] {alert['message']}")
        else:
            report.append("  No active alerts - all metrics nominal")
        
        report.append("\n--- GPU Processes ---")
        if processes:
            for proc in processes:
                report.append(f"  PID {proc['pid']}: {proc['name']} ({proc['memory_mb']}MB)")
        else:
            report.append("  No GPU processes running")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='NVIDIA T4 Monitor - Local Edition')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Continuous monitoring')
    monitor_parser.add_argument('-i', '--interval', type=int, default=2, help='Interval in seconds')
    monitor_parser.add_argument('-d', '--duration', type=int, help='Duration in seconds')
    monitor_parser.add_argument('-o', '--output', help='CSV output file')
    
    # Check command
    subparsers.add_parser('check', help='Single health check')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate full report')
    report_parser.add_argument('-o', '--output', help='Save report to file')
    
    # Specs command
    subparsers.add_parser('specs', help='Show T4 specifications')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    monitor = T4Monitor()
    
    if args.command == 'monitor':
        monitor.monitor_loop(
            interval=args.interval,
            duration=args.duration,
            csv_file=args.output
        )
    
    elif args.command == 'check':
        healthy = monitor.single_check()
        exit(0 if healthy else 1)
    
    elif args.command == 'report':
        report = monitor.generate_report()
        print(report)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {args.output}")
    
    elif args.command == 'specs':
        print("\nNVIDIA T4 Specifications:")
        for key, value in T4Monitor.T4_SPECS.items():
            print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
