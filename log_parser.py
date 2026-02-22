#!/usr/bin/env python3
"""
Log Parser for NVIDIA DGX Systems
Parses system logs for errors, warnings, and GPU-related issues
Generates summary reports

Author: Johnny Minier
Date: February 2026
For: NVIDIA Lab Operations
"""

import re
import os
import argparse
from datetime import datetime
from collections import defaultdict
from pathlib import Path


class LogParser:
    """Parse and analyze system logs for GPU-related issues."""
    
    # Patterns to search for
    PATTERNS = {
        'error': re.compile(r'\b(error|failed|failure|fatal)\b', re.IGNORECASE),
        'warning': re.compile(r'\b(warning|warn)\b', re.IGNORECASE),
        'nvidia': re.compile(r'\b(nvidia|gpu|cuda|nccl|nvlink|nvswitch)\b', re.IGNORECASE),
        'xid': re.compile(r'NVRM: Xid.*?: (\d+)', re.IGNORECASE),
        'temperature': re.compile(r'temperature|thermal|overheat', re.IGNORECASE),
        'memory': re.compile(r'(out of memory|oom|memory error|ecc)', re.IGNORECASE),
        'pcie': re.compile(r'(pcie|pci express|aer)', re.IGNORECASE),
    }
    
    # Known NVIDIA Xid error codes
    XID_DESCRIPTIONS = {
        13: "Graphics Engine Exception",
        31: "GPU memory page fault",
        32: "Invalid or corrupted push buffer stream",
        43: "GPU stopped processing",
        45: "Preemptive cleanup, due to previous errors",
        48: "Double Bit ECC Error",
        56: "Display engine error",
        57: "Display engine error",
        61: "Internal micro-controller breakpoint/warning",
        62: "Internal micro-controller halt",
        63: "ECC page retirement or row remapping recording event",
        64: "ECC page retirement or row remapper recording failure",
        68: "NVDEC0 Exception",
        69: "Graphics Engine class error",
        74: "NVLink Error",
        79: "GPU has fallen off the bus",
        92: "High single-bit ECC error rate",
        94: "Contained ECC error",
        95: "Uncontained ECC error",
    }
    
    def __init__(self):
        self.results = defaultdict(list)
        self.stats = defaultdict(int)
        self.xid_errors = defaultdict(int)
    
    def parse_line(self, line, line_num, filename):
        """Parse a single log line and categorize it."""
        findings = []
        
        # Check each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            if pattern.search(line):
                findings.append(pattern_name)
                self.stats[pattern_name] += 1
        
        # Extract Xid errors specifically
        xid_match = self.PATTERNS['xid'].search(line)
        if xid_match:
            xid_code = int(xid_match.group(1))
            self.xid_errors[xid_code] += 1
        
        # Store line if it has any findings
        if findings:
            self.results[filename].append({
                'line_num': line_num,
                'categories': findings,
                'content': line.strip()[:200]  # Truncate long lines
            })
    
    def parse_file(self, filepath):
        """Parse a single log file."""
        filename = os.path.basename(filepath)
        print(f"Parsing: {filepath}")
        
        try:
            with open(filepath, 'r', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    self.parse_line(line, line_num, filename)
        except PermissionError:
            print(f"  Permission denied: {filepath}")
        except Exception as e:
            print(f"  Error reading {filepath}: {e}")
    
    def parse_directory(self, dirpath, pattern="*.log"):
        """Parse all matching files in a directory."""
        path = Path(dirpath)
        for filepath in path.glob(pattern):
            self.parse_file(str(filepath))
    
    def parse_dmesg(self):
        """Parse dmesg output directly."""
        import subprocess
        
        print("Parsing: dmesg")
        try:
            result = subprocess.run(['dmesg'], capture_output=True, text=True)
            for line_num, line in enumerate(result.stdout.split('\n'), 1):
                self.parse_line(line, line_num, 'dmesg')
        except Exception as e:
            print(f"  Error running dmesg: {e}")
    
    def generate_report(self):
        """Generate a summary report."""
        report = []
        report.append("=" * 80)
        report.append(f"LOG ANALYSIS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        
        # Summary statistics
        report.append("\n📊 SUMMARY STATISTICS")
        report.append("-" * 40)
        for category, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {category.upper()}: {count} occurrences")
        
        # Xid errors (critical for GPU health)
        if self.xid_errors:
            report.append("\n⚠️  NVIDIA Xid ERRORS (GPU Issues)")
            report.append("-" * 40)
            for xid_code, count in sorted(self.xid_errors.items()):
                desc = self.XID_DESCRIPTIONS.get(xid_code, "Unknown error")
                report.append(f"  Xid {xid_code}: {count}x - {desc}")
        
        # Critical findings (errors + nvidia)
        report.append("\n🔴 CRITICAL FINDINGS (Errors + NVIDIA)")
        report.append("-" * 40)
        critical_count = 0
        for filename, entries in self.results.items():
            for entry in entries:
                if 'error' in entry['categories'] and 'nvidia' in entry['categories']:
                    critical_count += 1
                    if critical_count <= 20:  # Limit output
                        report.append(f"  [{filename}:{entry['line_num']}] {entry['content'][:100]}")
        
        if critical_count > 20:
            report.append(f"  ... and {critical_count - 20} more critical entries")
        elif critical_count == 0:
            report.append("  No critical NVIDIA errors found ✓")
        
        # Recent warnings
        report.append("\n🟡 RECENT WARNINGS")
        report.append("-" * 40)
        warning_count = 0
        for filename, entries in self.results.items():
            for entry in entries:
                if 'warning' in entry['categories']:
                    warning_count += 1
                    if warning_count <= 10:
                        report.append(f"  [{filename}:{entry['line_num']}] {entry['content'][:100]}")
        
        if warning_count > 10:
            report.append(f"  ... and {warning_count - 10} more warnings")
        elif warning_count == 0:
            report.append("  No warnings found ✓")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, output_file):
        """Save report to file."""
        report = self.generate_report()
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Report saved to: {output_file}")
    
    def save_detailed_csv(self, output_file):
        """Save detailed findings to CSV."""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'line_num', 'categories', 'content'])
            
            for filename, entries in self.results.items():
                for entry in entries:
                    writer.writerow([
                        filename,
                        entry['line_num'],
                        ','.join(entry['categories']),
                        entry['content']
                    ])
        
        print(f"Detailed CSV saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Log Parser for NVIDIA DGX Systems')
    parser.add_argument('-f', '--file', type=str, help='Parse a specific log file')
    parser.add_argument('-d', '--directory', type=str, help='Parse all logs in directory')
    parser.add_argument('-p', '--pattern', type=str, default='*.log',
                        help='File pattern for directory parsing (default: *.log)')
    parser.add_argument('--dmesg', action='store_true', help='Parse dmesg output')
    parser.add_argument('-o', '--output', type=str, default='log_report.txt',
                        help='Output report file (default: log_report.txt)')
    parser.add_argument('--csv', type=str, help='Save detailed findings to CSV')
    parser.add_argument('--syslog', action='store_true', 
                        help='Parse common system log locations')
    
    args = parser.parse_args()
    
    log_parser = LogParser()
    
    # Parse sources based on arguments
    if args.file:
        log_parser.parse_file(args.file)
    
    if args.directory:
        log_parser.parse_directory(args.directory, args.pattern)
    
    if args.dmesg:
        log_parser.parse_dmesg()
    
    if args.syslog:
        # Common log locations
        common_logs = [
            '/var/log/syslog',
            '/var/log/messages',
            '/var/log/kern.log',
            '/var/log/dmesg',
        ]
        for log_path in common_logs:
            if os.path.exists(log_path):
                log_parser.parse_file(log_path)
    
    # If no source specified, show help
    if not (args.file or args.directory or args.dmesg or args.syslog):
        parser.print_help()
        print("\nExample usage:")
        print("  python log_parser.py --dmesg")
        print("  python log_parser.py -f /var/log/syslog")
        print("  python log_parser.py -d /var/log/ -p '*.log'")
        print("  python log_parser.py --syslog")
        return
    
    # Generate and display report
    print("\n" + log_parser.generate_report())
    
    # Save outputs
    log_parser.save_report(args.output)
    
    if args.csv:
        log_parser.save_detailed_csv(args.csv)


if __name__ == '__main__':
    main()

