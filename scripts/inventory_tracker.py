#!/usr/bin/env python3
"""
Hardware Inventory Tracker for NVIDIA Lab
Track servers, GPUs, network equipment, and other assets
Stores data in JSON format

Author: Johnny Minier
Date: February 2026
For: NVIDIA Lab Operations
"""

import json
import os
import argparse
from datetime import datetime
from pathlib import Path


class InventoryTracker:
    """Manage hardware inventory with CRUD operations."""
    
    def __init__(self, inventory_file='inventory.json'):
        self.inventory_file = inventory_file
        self.inventory = self._load_inventory()
    
    def _load_inventory(self):
        """Load inventory from JSON file."""
        if os.path.exists(self.inventory_file):
            try:
                with open(self.inventory_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.inventory_file}, starting fresh")
                return {'assets': [], 'metadata': {'created': datetime.now().isoformat()}}
        return {'assets': [], 'metadata': {'created': datetime.now().isoformat()}}
    
    def _save_inventory(self):
        """Save inventory to JSON file."""
        self.inventory['metadata']['last_modified'] = datetime.now().isoformat()
        with open(self.inventory_file, 'w') as f:
            json.dump(self.inventory, f, indent=2)
    
    def _generate_id(self):
        """Generate a unique asset ID."""
        existing_ids = [a.get('asset_id', '') for a in self.inventory['assets']]
        counter = len(self.inventory['assets']) + 1
        while f"ASSET-{counter:04d}" in existing_ids:
            counter += 1
        return f"ASSET-{counter:04d}"
    
    def add_asset(self, asset_type, name, location, serial_number=None, 
                  status='active', notes=None, specs=None):
        """Add a new asset to inventory."""
        asset = {
            'asset_id': self._generate_id(),
            'type': asset_type,
            'name': name,
            'location': location,
            'serial_number': serial_number,
            'status': status,
            'notes': notes,
            'specs': specs or {},
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
        }
        
        self.inventory['assets'].append(asset)
        self._save_inventory()
        print(f"✓ Added asset: {asset['asset_id']} - {name}")
        return asset['asset_id']
    
    def update_asset(self, asset_id, **updates):
        """Update an existing asset."""
        for asset in self.inventory['assets']:
            if asset['asset_id'] == asset_id:
                for key, value in updates.items():
                    if value is not None:
                        asset[key] = value
                asset['last_updated'] = datetime.now().isoformat()
                self._save_inventory()
                print(f"✓ Updated asset: {asset_id}")
                return True
        
        print(f"✗ Asset not found: {asset_id}")
        return False
    
    def delete_asset(self, asset_id):
        """Delete an asset from inventory."""
        for i, asset in enumerate(self.inventory['assets']):
            if asset['asset_id'] == asset_id:
                removed = self.inventory['assets'].pop(i)
                self._save_inventory()
                print(f"✓ Deleted asset: {asset_id} - {removed['name']}")
                return True
        
        print(f"✗ Asset not found: {asset_id}")
        return False
    
    def get_asset(self, asset_id):
        """Get a specific asset by ID."""
        for asset in self.inventory['assets']:
            if asset['asset_id'] == asset_id:
                return asset
        return None
    
    def search_assets(self, query=None, asset_type=None, status=None, location=None):
        """Search assets by various criteria."""
        results = self.inventory['assets']
        
        if query:
            query_lower = query.lower()
            results = [a for a in results if 
                       query_lower in a.get('name', '').lower() or
                       query_lower in a.get('serial_number', '').lower() or
                       query_lower in a.get('asset_id', '').lower() or
                       query_lower in a.get('notes', '').lower()]
        
        if asset_type:
            results = [a for a in results if a.get('type', '').lower() == asset_type.lower()]
        
        if status:
            results = [a for a in results if a.get('status', '').lower() == status.lower()]
        
        if location:
            results = [a for a in results if location.lower() in a.get('location', '').lower()]
        
        return results
    
    def list_assets(self, asset_type=None, status=None):
        """List all assets with optional filtering."""
        assets = self.search_assets(asset_type=asset_type, status=status)
        return assets
    
    def print_asset(self, asset):
        """Pretty print a single asset."""
        print(f"\n{'='*60}")
        print(f"Asset ID: {asset['asset_id']}")
        print(f"{'='*60}")
        print(f"  Name:          {asset['name']}")
        print(f"  Type:          {asset['type']}")
        print(f"  Location:      {asset['location']}")
        print(f"  Serial:        {asset.get('serial_number', 'N/A')}")
        print(f"  Status:        {asset['status']}")
        if asset.get('notes'):
            print(f"  Notes:         {asset['notes']}")
        if asset.get('specs'):
            print(f"  Specs:")
            for key, value in asset['specs'].items():
                print(f"    - {key}: {value}")
        print(f"  Created:       {asset['created']}")
        print(f"  Last Updated:  {asset['last_updated']}")
    
    def print_table(self, assets):
        """Print assets as a formatted table."""
        if not assets:
            print("No assets found.")
            return
        
        print(f"\n{'ID':<12} {'Type':<12} {'Name':<25} {'Location':<15} {'Status':<10}")
        print("-" * 80)
        
        for asset in assets:
            print(f"{asset['asset_id']:<12} {asset['type']:<12} "
                  f"{asset['name'][:25]:<25} {asset['location'][:15]:<15} "
                  f"{asset['status']:<10}")
        
        print("-" * 80)
        print(f"Total: {len(assets)} assets")
    
    def get_summary(self):
        """Get inventory summary statistics."""
        assets = self.inventory['assets']
        
        summary = {
            'total_assets': len(assets),
            'by_type': {},
            'by_status': {},
            'by_location': {},
        }
        
        for asset in assets:
            # Count by type
            asset_type = asset.get('type', 'unknown')
            summary['by_type'][asset_type] = summary['by_type'].get(asset_type, 0) + 1
            
            # Count by status
            status = asset.get('status', 'unknown')
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # Count by location
            location = asset.get('location', 'unknown')
            summary['by_location'][location] = summary['by_location'].get(location, 0) + 1
        
        return summary
    
    def print_summary(self):
        """Print inventory summary."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("INVENTORY SUMMARY")
        print("=" * 60)
        print(f"\nTotal Assets: {summary['total_assets']}")
        
        print("\nBy Type:")
        for asset_type, count in sorted(summary['by_type'].items()):
            print(f"  {asset_type}: {count}")
        
        print("\nBy Status:")
        for status, count in sorted(summary['by_status'].items()):
            print(f"  {status}: {count}")
        
        print("\nBy Location:")
        for location, count in sorted(summary['by_location'].items()):
            print(f"  {location}: {count}")
        
        print("=" * 60)
    
    def export_csv(self, output_file):
        """Export inventory to CSV."""
        import csv
        
        with open(output_file, 'w', newline='') as f:
            fieldnames = ['asset_id', 'type', 'name', 'location', 'serial_number', 
                          'status', 'notes', 'created', 'last_updated']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for asset in self.inventory['assets']:
                writer.writerow(asset)
        
        print(f"✓ Exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Hardware Inventory Tracker')
    parser.add_argument('-f', '--file', type=str, default='inventory.json',
                        help='Inventory file path (default: inventory.json)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new asset')
    add_parser.add_argument('--type', required=True, 
                           choices=['server', 'gpu', 'switch', 'cable', 'pdu', 'storage', 'other'],
                           help='Asset type')
    add_parser.add_argument('--name', required=True, help='Asset name')
    add_parser.add_argument('--location', required=True, help='Physical location')
    add_parser.add_argument('--serial', help='Serial number')
    add_parser.add_argument('--status', default='active',
                           choices=['active', 'maintenance', 'retired', 'spare'],
                           help='Asset status')
    add_parser.add_argument('--notes', help='Additional notes')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update an asset')
    update_parser.add_argument('asset_id', help='Asset ID to update')
    update_parser.add_argument('--name', help='New name')
    update_parser.add_argument('--location', help='New location')
    update_parser.add_argument('--status', choices=['active', 'maintenance', 'retired', 'spare'])
    update_parser.add_argument('--notes', help='New notes')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an asset')
    delete_parser.add_argument('asset_id', help='Asset ID to delete')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List assets')
    list_parser.add_argument('--type', help='Filter by type')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search assets')
    search_parser.add_argument('query', help='Search query')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show asset details')
    show_parser.add_argument('asset_id', help='Asset ID to show')
    
    # Summary command
    subparsers.add_parser('summary', help='Show inventory summary')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export to CSV')
    export_parser.add_argument('-o', '--output', default='inventory_export.csv',
                              help='Output CSV file')
    
    # Demo command (populate with sample data)
    subparsers.add_parser('demo', help='Add demo data')
    
    args = parser.parse_args()
    
    tracker = InventoryTracker(args.file)
    
    if args.command == 'add':
        tracker.add_asset(
            asset_type=args.type,
            name=args.name,
            location=args.location,
            serial_number=args.serial,
            status=args.status,
            notes=args.notes
        )
    
    elif args.command == 'update':
        tracker.update_asset(
            args.asset_id,
            name=args.name,
            location=args.location,
            status=args.status,
            notes=args.notes
        )
    
    elif args.command == 'delete':
        tracker.delete_asset(args.asset_id)
    
    elif args.command == 'list':
        assets = tracker.list_assets(asset_type=args.type, status=args.status)
        tracker.print_table(assets)
    
    elif args.command == 'search':
        assets = tracker.search_assets(query=args.query)
        tracker.print_table(assets)
    
    elif args.command == 'show':
        asset = tracker.get_asset(args.asset_id)
        if asset:
            tracker.print_asset(asset)
        else:
            print(f"Asset not found: {args.asset_id}")
    
    elif args.command == 'summary':
        tracker.print_summary()
    
    elif args.command == 'export':
        tracker.export_csv(args.output)
    
    elif args.command == 'demo':
        # Add sample data
        print("Adding demo inventory data...")
        
        tracker.add_asset('server', 'DGX-B200-01', 'Rack A1, U1-10', 
                         serial_number='DGX-SN-001', status='active',
                         notes='Primary training server')
        tracker.add_asset('server', 'DGX-B200-02', 'Rack A1, U11-20',
                         serial_number='DGX-SN-002', status='active')
        tracker.add_asset('switch', 'Quantum-2 IB Switch', 'Rack A1, U41',
                         serial_number='QM2-001', status='active',
                         notes='400G InfiniBand switch')
        tracker.add_asset('pdu', 'PDU-A1-L', 'Rack A1, Left',
                         serial_number='PDU-001', status='active')
        tracker.add_asset('pdu', 'PDU-A1-R', 'Rack A1, Right',
                         serial_number='PDU-002', status='active')
        tracker.add_asset('cable', 'OSFP 400G Cable x20', 'Rack A1',
                         status='active', notes='InfiniBand cables for DGX')
        tracker.add_asset('server', 'DGX-B200-03', 'Rack A2, U1-10',
                         serial_number='DGX-SN-003', status='maintenance',
                         notes='GPU 4 being replaced')
        
        print("\nDemo data added!")
        tracker.print_summary()
    
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python inventory_tracker.py demo")
        print("  python inventory_tracker.py list")
        print("  python inventory_tracker.py add --type server "
              "--name 'DGX-B200-04' --location 'Rack B1'")
        print("  python inventory_tracker.py search 'DGX'")
        print("  python inventory_tracker.py summary")


if __name__ == '__main__':
    main()

