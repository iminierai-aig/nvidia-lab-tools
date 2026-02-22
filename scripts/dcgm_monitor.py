#!/usr/bin/env python3
"""
DCGM Health Monitor
Automated GPU health monitoring using DCGM metrics.

Features:
- Real-time GPU monitoring
- Alert on threshold violations
- Health check reports
- Integration with existing tools

Usage:
    python dcgm_monitor.py monitor --interval 5
    python dcgm_monitor.py health
    python dcgm_monitor.py diag --level 1
    python dcgm_monitor.py report
"""

import subprocess
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Demo mode for testing without DCGM
DEMO_MODE = True


class DCGMMonitor:
    """Monitor GPUs using DCGM."""
    
    # Alert thresholds
    THRESHOLDS = {
        'gpu_temp': {'warning': 75, 'critical': 85},
        'mem_temp': {'warning': 85, 'critical': 95},
        'power_percent': {'warning': 90, 'critical': 95},
        'ecc_dbe': {'warning': 1, 'critical': 1},
        'xid_errors': {'warning': 1, 'critical': 1}
    }
    
    # Key field IDs
    FIELDS = {
        'gpu_temp': 150,
        'mem_temp': 140,
        'power': 155,
        'power_limit': 160,
        'gpu_util': 203,
        'mem_util': 204,
        'sm_clock': 100,
        'mem_clock': 101,
        'fan_speed': 191,
        'pstate': 190
    }
    
    def __init__(self):
        self.demo_mode = DEMO_MODE
        if self.demo_mode:
            print("[DEMO MODE] Running with simulated data")
            self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize demo GPU data."""
        self.demo_gpus = [
            {
                'id': 0, 'name': 'NVIDIA B200',
                'uuid': 'GPU-12345-abcde',
                'gpu_temp': 52, 'mem_temp': 48,
                'power': 285, 'power_limit': 1000,
                'gpu_util': 78, 'mem_util': 65,
                'sm_clock': 1980, 'mem_clock': 2619,
                'fan_speed': 45, 'pstate': 0,
                'ecc_sbe': 0, 'ecc_dbe': 0,
                'fb_total': 192000, 'fb_used': 124800
            },
            {
                'id': 1, 'name': 'NVIDIA B200',
                'uuid': 'GPU-67890-fghij',
                'gpu_temp': 55, 'mem_temp': 51,
                'power': 310, 'power_limit': 1000,
                'gpu_util': 92, 'mem_util': 78,
                'sm_clock': 2100, 'mem_clock': 2619,
                'fan_speed': 52, 'pstate': 0,
                'ecc_sbe': 0, 'ecc_dbe': 0,
                'fb_total': 192000, 'fb_used': 149760
            }
        ]
    
    def _run_dcgmi(self, args: List[str]) -> Tuple[int, str, str]:
        """Run dcgmi command and return output."""
        if self.demo_mode:
            return 0, "", ""
        
        try:
            result = subprocess.run(
                ['dcgmi'] + args,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except FileNotFoundError:
            return 1, "", "dcgmi not found"
    
    def discover_gpus(self) -> List[Dict]:
        """Discover all GPUs on the system."""
        if self.demo_mode:
            return [{'id': g['id'], 'name': g['name'], 'uuid': g['uuid']} 
                    for g in self.demo_gpus]
        
        ret, stdout, stderr = self._run_dcgmi(['discovery', '-l'])
        # Parse output...
        return []
    
    def get_gpu_metrics(self, gpu_id: int = None) -> List[Dict]:
        """Get current GPU metrics."""
        if self.demo_mode:
            if gpu_id is not None:
                return [g for g in self.demo_gpus if g['id'] == gpu_id]
            return self.demo_gpus
        
        # Real implementation would parse dcgmi dmon output
        return []
    
    def check_health(self) -> Dict:
        """Run health check on all GPUs."""
        if self.demo_mode:
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'gpus': [
                    {'id': 0, 'status': 'healthy', 'issues': []},
                    {'id': 1, 'status': 'healthy', 'issues': []}
                ]
            }
        
        ret, stdout, stderr = self._run_dcgmi(['health', '-c'])
        # Parse health output
        return {'status': 'unknown', 'output': stdout}
    
    def run_diagnostics(self, level: int = 1, gpu_ids: List[int] = None) -> Dict:
        """Run DCGM diagnostics."""
        if self.demo_mode:
            return {
                'level': level,
                'timestamp': datetime.now().isoformat(),
                'result': 'Pass',
                'tests': [
                    {'name': 'Deployment', 'result': 'Pass'},
                    {'name': 'NVML Library', 'result': 'Pass'},
                    {'name': 'Permissions', 'result': 'Pass'},
                    {'name': 'Persistence Mode', 'result': 'Pass'}
                ]
            }
        
        args = ['diag', '-r', str(level), '-j']
        if gpu_ids:
            args.extend(['-i', ','.join(map(str, gpu_ids))])
        
        ret, stdout, stderr = self._run_dcgmi(args)
        try:
            return json.loads(stdout)
        except:
            return {'error': stderr or 'Failed to run diagnostics'}
    
    def check_alerts(self, metrics: List[Dict]) -> List[Dict]:
        """Check metrics against thresholds."""
        alerts = []
        
        for gpu in metrics:
            gpu_id = gpu['id']
            
            # Temperature check
            if gpu['gpu_temp'] >= self.THRESHOLDS['gpu_temp']['critical']:
                alerts.append({
                    'gpu': gpu_id,
                    'level': 'CRITICAL',
                    'metric': 'gpu_temp',
                    'value': gpu['gpu_temp'],
                    'threshold': self.THRESHOLDS['gpu_temp']['critical'],
                    'message': f"GPU {gpu_id} temperature CRITICAL: {gpu['gpu_temp']}°C"
                })
            elif gpu['gpu_temp'] >= self.THRESHOLDS['gpu_temp']['warning']:
                alerts.append({
                    'gpu': gpu_id,
                    'level': 'WARNING',
                    'metric': 'gpu_temp',
                    'value': gpu['gpu_temp'],
                    'threshold': self.THRESHOLDS['gpu_temp']['warning'],
                    'message': f"GPU {gpu_id} temperature WARNING: {gpu['gpu_temp']}°C"
                })
            
            # Power check
            power_percent = (gpu['power'] / gpu['power_limit']) * 100
            if power_percent >= self.THRESHOLDS['power_percent']['critical']:
                alerts.append({
                    'gpu': gpu_id,
                    'level': 'CRITICAL',
                    'metric': 'power',
                    'value': power_percent,
                    'threshold': self.THRESHOLDS['power_percent']['critical'],
                    'message': f"GPU {gpu_id} power CRITICAL: {power_percent:.1f}%"
                })
            
            # ECC check
            if gpu.get('ecc_dbe', 0) >= self.THRESHOLDS['ecc_dbe']['critical']:
                alerts.append({
                    'gpu': gpu_id,
                    'level': 'CRITICAL',
                    'metric': 'ecc_dbe',
                    'value': gpu['ecc_dbe'],
                    'threshold': self.THRESHOLDS['ecc_dbe']['critical'],
                    'message': f"GPU {gpu_id} ECC Double-Bit Errors: {gpu['ecc_dbe']}"
                })
        
        return alerts
    
    def monitor_loop(self, interval: int = 5, duration: int = None):
        """Continuous monitoring loop."""
        print(f"Starting GPU monitoring (interval: {interval}s)")
        print("-" * 80)
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                metrics = self.get_gpu_metrics()
                
                # Print header every 10 iterations
                if iteration % 10 == 1:
                    print(f"\n{'Time':8} {'GPU':4} {'Temp':6} {'Power':8} {'GPU%':6} {'Mem%':6} {'SMClk':6} {'PState':6}")
                    print("-" * 80)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                for gpu in metrics:
                    print(f"{timestamp:8} {gpu['id']:4} {gpu['gpu_temp']:5}°C "
                          f"{gpu['power']:6}W {gpu['gpu_util']:5}% "
                          f"{gpu['mem_util']:5}% {gpu['sm_clock']:5} {gpu['pstate']:6}")
                
                # Check for alerts
                alerts = self.check_alerts(metrics)
                for alert in alerts:
                    print(f"  [!{alert['level']}] {alert['message']}")
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    print(f"\nMonitoring complete ({duration}s)")
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def generate_report(self) -> str:
        """Generate a comprehensive health report."""
        report = []
        report.append("=" * 60)
        report.append("GPU HEALTH REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 60)
        
        # Discovery
        report.append("\n--- GPU Discovery ---")
        gpus = self.discover_gpus()
        for gpu in gpus:
            report.append(f"  GPU {gpu['id']}: {gpu['name']} ({gpu['uuid'][:16]}...)")
        
        # Current metrics
        report.append("\n--- Current Metrics ---")
        metrics = self.get_gpu_metrics()
        for gpu in metrics:
            report.append(f"\n  GPU {gpu['id']} ({gpu['name']}):")
            report.append(f"    Temperature: {gpu['gpu_temp']}°C (Memory: {gpu['mem_temp']}°C)")
            report.append(f"    Power: {gpu['power']}W / {gpu['power_limit']}W ({(gpu['power']/gpu['power_limit']*100):.1f}%)")
            report.append(f"    Utilization: GPU {gpu['gpu_util']}%, Memory {gpu['mem_util']}%")
            report.append(f"    Clocks: SM {gpu['sm_clock']} MHz, Memory {gpu['mem_clock']} MHz")
            report.append(f"    Memory: {gpu['fb_used']/1024:.1f} GB / {gpu['fb_total']/1024:.1f} GB")
            report.append(f"    ECC Errors: SBE={gpu['ecc_sbe']}, DBE={gpu['ecc_dbe']}")
        
        # Health check
        report.append("\n--- Health Check ---")
        health = self.check_health()
        report.append(f"  Overall Status: {health['status'].upper()}")
        for gpu in health.get('gpus', []):
            status_icon = '✓' if gpu['status'] == 'healthy' else '✗'
            report.append(f"  {status_icon} GPU {gpu['id']}: {gpu['status']}")
        
        # Alerts
        report.append("\n--- Active Alerts ---")
        alerts = self.check_alerts(metrics)
        if alerts:
            for alert in alerts:
                report.append(f"  [{alert['level']}] {alert['message']}")
        else:
            report.append("  No active alerts")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='DCGM Health Monitor')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Real-time monitoring')
    monitor_parser.add_argument('-i', '--interval', type=int, default=5, help='Interval in seconds')
    monitor_parser.add_argument('-d', '--duration', type=int, help='Duration in seconds')
    
    # Health command
    subparsers.add_parser('health', help='Quick health check')
    
    # Diag command
    diag_parser = subparsers.add_parser('diag', help='Run diagnostics')
    diag_parser.add_argument('-l', '--level', type=int, default=1, choices=[1,2,3,4])
    diag_parser.add_argument('-g', '--gpus', help='Comma-separated GPU IDs')
    
    # Report command
    subparsers.add_parser('report', help='Generate health report')
    
    # Demo command
    subparsers.add_parser('demo', help='Run demo')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    monitor = DCGMMonitor()
    
    if args.command == 'monitor':
        monitor.monitor_loop(interval=args.interval, duration=args.duration)
    
    elif args.command == 'health':
        health = monitor.check_health()
        print(f"Health Status: {health['status'].upper()}")
        for gpu in health.get('gpus', []):
            print(f"  GPU {gpu['id']}: {gpu['status']}")
    
    elif args.command == 'diag':
        gpu_ids = [int(x) for x in args.gpus.split(',')] if args.gpus else None
        print(f"Running Level {args.level} diagnostics...")
        result = monitor.run_diagnostics(level=args.level, gpu_ids=gpu_ids)
        print(f"Result: {result.get('result', 'Unknown')}")
        for test in result.get('tests', []):
            icon = '✓' if test['result'] == 'Pass' else '✗'
            print(f"  {icon} {test['name']}: {test['result']}")
    
    elif args.command == 'report':
        print(monitor.generate_report())
    
    elif args.command == 'demo':
        print("=== DCGM Monitor Demo ===\n")
        
        print("1. GPU Discovery:")
        for gpu in monitor.discover_gpus():
            print(f"   {gpu['id']}: {gpu['name']}")
        
        print("\n2. Current Metrics:")
        for gpu in monitor.get_gpu_metrics():
            print(f"   GPU {gpu['id']}: {gpu['gpu_temp']}°C, {gpu['power']}W, {gpu['gpu_util']}%")
        
        print("\n3. Health Check:")
        health = monitor.check_health()
        print(f"   Status: {health['status']}")
        
        print("\n4. Quick Report:")
        print(monitor.generate_report())


if __name__ == '__main__':
    main()
