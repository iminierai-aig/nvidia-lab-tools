#!/usr/bin/env python3
"""
Automated GPU Health Check System
Designed for datacenter operations with T4/DGX systems
Supports cron scheduling and webhook alerts
"""

import subprocess
import json
import sys
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
import argparse

# Configuration
CONFIG = {
    'thresholds': {
        'temperature_warn': 70,
        'temperature_crit': 80,
        'memory_warn': 85,
        'memory_crit': 95,
        'power_warn': 90,  # Percent of limit
        'power_crit': 100,
        'ecc_single_warn': 10,
        'ecc_double_crit': 1
    },
    'log_file': '/var/log/gpu_health.log',
    'report_dir': os.path.expanduser('~/nvidia-lab-tools/reports'),
    'alert_webhook': None,  # Set your webhook URL
    'email_config': None    # Set {'server': '', 'user': '', 'pass': '', 'to': ''}
}

class GPUHealthChecker:
    def __init__(self):
        self.timestamp = datetime.now()
        self.results = {'status': 'HEALTHY', 'checks': [], 'metrics': {}, 'alerts': []}
    
    def run_command(self, cmd):
        """Execute shell command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception as e:
            return None
    
    def check_gpu_presence(self):
        """Verify GPU is detected"""
        output = self.run_command('nvidia-smi --query-gpu=name --format=csv,noheader')
        if output:
            self.results['checks'].append({'name': 'GPU Detection', 'status': 'PASS', 'value': output})
            self.results['metrics']['gpu_name'] = output
            return True
        else:
            self.results['checks'].append({'name': 'GPU Detection', 'status': 'FAIL', 'value': 'No GPU detected'})
            self.results['status'] = 'CRITICAL'
            return False
    
    def check_driver(self):
        """Verify driver is loaded and version"""
        output = self.run_command('nvidia-smi --query-gpu=driver_version --format=csv,noheader')
        if output:
            self.results['checks'].append({'name': 'Driver', 'status': 'PASS', 'value': output})
            self.results['metrics']['driver_version'] = output
        else:
            self.results['checks'].append({'name': 'Driver', 'status': 'FAIL', 'value': 'Driver not loaded'})
            self.results['status'] = 'CRITICAL'
    
    def check_temperature(self):
        """Check GPU temperature"""
        output = self.run_command('nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits')
        if output:
            temp = float(output)
            self.results['metrics']['temperature'] = temp
            
            if temp >= CONFIG['thresholds']['temperature_crit']:
                self.results['checks'].append({'name': 'Temperature', 'status': 'CRITICAL', 'value': f'{temp}°C'})
                self.results['alerts'].append(f'CRITICAL: GPU temperature {temp}°C exceeds {CONFIG["thresholds"]["temperature_crit"]}°C')
                self.results['status'] = 'CRITICAL'
            elif temp >= CONFIG['thresholds']['temperature_warn']:
                self.results['checks'].append({'name': 'Temperature', 'status': 'WARNING', 'value': f'{temp}°C'})
                self.results['alerts'].append(f'WARNING: GPU temperature {temp}°C exceeds {CONFIG["thresholds"]["temperature_warn"]}°C')
                if self.results['status'] == 'HEALTHY':
                    self.results['status'] = 'WARNING'
            else:
                self.results['checks'].append({'name': 'Temperature', 'status': 'PASS', 'value': f'{temp}°C'})
    
    def check_memory(self):
        """Check GPU memory usage"""
        output = self.run_command('nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits')
        if output:
            used, total = map(float, output.split(', '))
            pct = (used / total) * 100
            self.results['metrics']['memory_used_mb'] = used
            self.results['metrics']['memory_total_mb'] = total
            self.results['metrics']['memory_percent'] = round(pct, 1)
            
            if pct >= CONFIG['thresholds']['memory_crit']:
                self.results['checks'].append({'name': 'Memory', 'status': 'CRITICAL', 'value': f'{pct:.1f}%'})
                self.results['alerts'].append(f'CRITICAL: GPU memory {pct:.1f}% exceeds {CONFIG["thresholds"]["memory_crit"]}%')
                self.results['status'] = 'CRITICAL'
            elif pct >= CONFIG['thresholds']['memory_warn']:
                self.results['checks'].append({'name': 'Memory', 'status': 'WARNING', 'value': f'{pct:.1f}%'})
                if self.results['status'] == 'HEALTHY':
                    self.results['status'] = 'WARNING'
            else:
                self.results['checks'].append({'name': 'Memory', 'status': 'PASS', 'value': f'{pct:.1f}%'})
    
    def check_power(self):
        """Check GPU power draw"""
        output = self.run_command('nvidia-smi --query-gpu=power.draw,power.limit --format=csv,noheader,nounits')
        if output:
            parts = output.split(', ')
            draw = float(parts[0]) if parts[0] != '[N/A]' else None
            limit = float(parts[1]) if parts[1] != '[N/A]' else 70  # T4 default
            
            if draw:
                pct = (draw / limit) * 100
                self.results['metrics']['power_draw'] = draw
                self.results['metrics']['power_limit'] = limit
                self.results['metrics']['power_percent'] = round(pct, 1)
                
                if pct >= CONFIG['thresholds']['power_crit']:
                    self.results['checks'].append({'name': 'Power', 'status': 'WARNING', 'value': f'{draw:.1f}W ({pct:.1f}%)'})
                else:
                    self.results['checks'].append({'name': 'Power', 'status': 'PASS', 'value': f'{draw:.1f}W ({pct:.1f}%)'})
    
    def check_ecc(self):
        """Check ECC memory errors"""
        output = self.run_command('nvidia-smi --query-gpu=ecc.errors.corrected.volatile.total,ecc.errors.uncorrected.volatile.total --format=csv,noheader')
        if output and 'N/A' not in output:
            parts = output.split(', ')
            single = int(parts[0]) if parts[0].isdigit() else 0
            double = int(parts[1]) if parts[1].isdigit() else 0
            
            self.results['metrics']['ecc_single'] = single
            self.results['metrics']['ecc_double'] = double
            
            if double >= CONFIG['thresholds']['ecc_double_crit']:
                self.results['checks'].append({'name': 'ECC Errors', 'status': 'CRITICAL', 'value': f'SBE:{single} DBE:{double}'})
                self.results['alerts'].append(f'CRITICAL: {double} double-bit ECC errors detected')
                self.results['status'] = 'CRITICAL'
            elif single >= CONFIG['thresholds']['ecc_single_warn']:
                self.results['checks'].append({'name': 'ECC Errors', 'status': 'WARNING', 'value': f'SBE:{single} DBE:{double}'})
            else:
                self.results['checks'].append({'name': 'ECC Errors', 'status': 'PASS', 'value': f'SBE:{single} DBE:{double}'})
        else:
            self.results['checks'].append({'name': 'ECC Errors', 'status': 'N/A', 'value': 'Not supported'})
    
    def check_persistence_mode(self):
        """Check if persistence mode is enabled"""
        output = self.run_command('nvidia-smi --query-gpu=persistence_mode --format=csv,noheader')
        if output:
            enabled = output.lower() == 'enabled'
            self.results['metrics']['persistence_mode'] = enabled
            status = 'PASS' if enabled else 'INFO'
            self.results['checks'].append({'name': 'Persistence Mode', 'status': status, 'value': output})
    
    def check_xid_errors(self):
        """Check for XID errors in dmesg"""
        output = self.run_command('dmesg | grep -i "NVRM: Xid" | tail -5')
        if output:
            self.results['checks'].append({'name': 'XID Errors', 'status': 'WARNING', 'value': 'XID errors found'})
            self.results['alerts'].append('WARNING: XID errors detected in kernel log')
            self.results['metrics']['xid_errors'] = output.split('\n')
            if self.results['status'] == 'HEALTHY':
                self.results['status'] = 'WARNING'
        else:
            self.results['checks'].append({'name': 'XID Errors', 'status': 'PASS', 'value': 'None'})
    
    def run_all_checks(self):
        """Run all health checks"""
        self.results['timestamp'] = self.timestamp.isoformat()
        
        if not self.check_gpu_presence():
            return self.results
        
        self.check_driver()
        self.check_temperature()
        self.check_memory()
        self.check_power()
        self.check_ecc()
        self.check_persistence_mode()
        self.check_xid_errors()
        
        return self.results
    
    def print_report(self):
        """Print human-readable report"""
        print(f"\n{'='*60}")
        print(f"GPU HEALTH CHECK REPORT")
        print(f"Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Status: {self.results['status']}")
        print(f"{'='*60}\n")
        
        for check in self.results['checks']:
            status_icon = {'PASS': '✓', 'WARNING': '⚠', 'CRITICAL': '✗', 'INFO': 'ℹ', 'N/A': '-'}.get(check['status'], '?')
            print(f"  [{status_icon}] {check['name']}: {check['value']}")
        
        if self.results['alerts']:
            print(f"\n{'='*60}")
            print("ALERTS:")
            for alert in self.results['alerts']:
                print(f"  • {alert}")
        
        print(f"\n{'='*60}\n")
    
    def save_report(self):
        """Save JSON report to file"""
        os.makedirs(CONFIG['report_dir'], exist_ok=True)
        filename = os.path.join(CONFIG['report_dir'], f"health_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json")
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        return filename

def main():
    parser = argparse.ArgumentParser(description='GPU Health Check System')
    parser.add_argument('--json', action='store_true', help='Output JSON only')
    parser.add_argument('--save', action='store_true', help='Save report to file')
    parser.add_argument('--quiet', action='store_true', help='Only output on failure')
    args = parser.parse_args()
    
    checker = GPUHealthChecker()
    results = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.quiet or results['status'] != 'HEALTHY':
        checker.print_report()
    
    if args.save:
        filename = checker.save_report()
        print(f"Report saved to: {filename}")
    
    # Exit code based on status
    exit_codes = {'HEALTHY': 0, 'WARNING': 1, 'CRITICAL': 2}
    sys.exit(exit_codes.get(results['status'], 3))

if __name__ == '__main__':
    main()
