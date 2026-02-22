#!/usr/bin/env python3
"""
Jira Lab Operations Manager
Automates common Jira tasks for NVIDIA lab operations.

Features:
- Create maintenance tickets
- Search and list issues
- Update issue status
- Generate reports
- Dashboard data export

Usage:
    python jira_lab_manager.py create --summary "GPU Health Check" --type Task
    python jira_lab_manager.py list --status "In Progress"
    python jira_lab_manager.py report --days 7
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# For demo/testing without Jira connection
DEMO_MODE = True

class JiraLabManager:
    """Manages Jira operations for lab work."""
    
    def __init__(self, server: str = None, email: str = None, token: str = None):
        """
        Initialize Jira connection.
        
        Args:
            server: Jira server URL
            email: User email (for Jira Cloud)
            token: API token
        """
        self.server = server or os.environ.get('JIRA_SERVER', 'https://your-domain.atlassian.net')
        self.email = email or os.environ.get('JIRA_EMAIL')
        self.token = token or os.environ.get('JIRA_TOKEN')
        self.jira = None
        self.demo_mode = DEMO_MODE
        
        if not self.demo_mode:
            self._connect()
        else:
            print("[DEMO MODE] Running without Jira connection")
            self._init_demo_data()
    
    def _connect(self):
        """Establish Jira connection."""
        try:
            from jira import JIRA
            self.jira = JIRA(
                server=self.server,
                basic_auth=(self.email, self.token)
            )
            print(f"[OK] Connected to {self.server}")
        except ImportError:
            print("[WARN] jira library not installed. Run: pip install jira")
            self.demo_mode = True
            self._init_demo_data()
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            self.demo_mode = True
            self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize demo data for testing."""
        self.demo_issues = [
            {
                'key': 'LAB-101',
                'summary': 'DGX B200 Health Check - Rack A1',
                'status': 'In Progress',
                'priority': 'High',
                'assignee': 'john.doe',
                'created': '2025-02-03T10:00:00',
                'labels': ['gpu-maintenance', 'routine']
            },
            {
                'key': 'LAB-102',
                'summary': 'InfiniBand Switch Firmware Update',
                'status': 'To Do',
                'priority': 'Medium',
                'assignee': 'jane.smith',
                'created': '2025-02-04T14:30:00',
                'labels': ['network', 'firmware']
            },
            {
                'key': 'LAB-103',
                'summary': 'NCCL Performance Test - Multi-node',
                'status': 'Done',
                'priority': 'High',
                'assignee': 'john.doe',
                'created': '2025-02-01T09:00:00',
                'labels': ['testing', 'nccl']
            },
            {
                'key': 'LAB-104',
                'summary': 'GPU Memory Error Investigation - GPU 3',
                'status': 'In Progress',
                'priority': 'Critical',
                'assignee': 'john.doe',
                'created': '2025-02-05T08:15:00',
                'labels': ['troubleshooting', 'gpu-error']
            },
            {
                'key': 'LAB-105',
                'summary': 'Document NVLink Topology for DGX Systems',
                'status': 'To Do',
                'priority': 'Low',
                'assignee': None,
                'created': '2025-02-02T11:00:00',
                'labels': ['documentation']
            }
        ]
    
    def create_issue(self, summary: str, description: str = "", 
                     issue_type: str = "Task", priority: str = "Medium",
                     labels: List[str] = None, assignee: str = None) -> Dict:
        """
        Create a new Jira issue.
        
        Args:
            summary: Issue title
            description: Detailed description
            issue_type: Task, Bug, Story, etc.
            priority: Low, Medium, High, Critical
            labels: List of labels
            assignee: Username to assign
            
        Returns:
            Created issue details
        """
        if self.demo_mode:
            new_key = f"LAB-{100 + len(self.demo_issues) + 1}"
            new_issue = {
                'key': new_key,
                'summary': summary,
                'description': description,
                'status': 'To Do',
                'priority': priority,
                'assignee': assignee,
                'created': datetime.now().isoformat(),
                'labels': labels or []
            }
            self.demo_issues.append(new_issue)
            print(f"[DEMO] Created issue: {new_key}")
            return new_issue
        
        # Real Jira creation
        issue_dict = {
            'project': {'key': 'LAB'},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            'priority': {'name': priority}
        }
        
        if labels:
            issue_dict['labels'] = labels
            
        new_issue = self.jira.create_issue(fields=issue_dict)
        
        if assignee:
            self.jira.assign_issue(new_issue, assignee)
            
        return {
            'key': new_issue.key,
            'summary': summary,
            'status': 'To Do',
            'priority': priority
        }
    
    def search_issues(self, jql: str = None, status: str = None, 
                      assignee: str = None, labels: List[str] = None,
                      max_results: int = 50) -> List[Dict]:
        """
        Search for issues.
        
        Args:
            jql: Raw JQL query (overrides other params)
            status: Filter by status
            assignee: Filter by assignee
            labels: Filter by labels
            max_results: Maximum results to return
            
        Returns:
            List of matching issues
        """
        if self.demo_mode:
            results = self.demo_issues.copy()
            
            if status:
                results = [i for i in results if i['status'].lower() == status.lower()]
            if assignee:
                results = [i for i in results if i.get('assignee') == assignee]
            if labels:
                results = [i for i in results 
                          if any(l in i.get('labels', []) for l in labels)]
                
            return results[:max_results]
        
        # Build JQL if not provided
        if not jql:
            conditions = ['project = LAB']
            if status:
                conditions.append(f'status = "{status}"')
            if assignee:
                conditions.append(f'assignee = "{assignee}"')
            if labels:
                label_conditions = [f'labels = "{l}"' for l in labels]
                conditions.append(f'({" OR ".join(label_conditions)})')
            jql = ' AND '.join(conditions)
        
        issues = self.jira.search_issues(jql, maxResults=max_results)
        
        return [{
            'key': issue.key,
            'summary': issue.fields.summary,
            'status': issue.fields.status.name,
            'priority': issue.fields.priority.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None
        } for issue in issues]
    
    def get_my_issues(self) -> List[Dict]:
        """Get issues assigned to current user."""
        if self.demo_mode:
            return [i for i in self.demo_issues if i.get('assignee') == 'john.doe']
        
        return self.search_issues(jql='assignee = currentUser() AND status != Done')
    
    def update_issue(self, issue_key: str, **fields) -> bool:
        """
        Update an issue.
        
        Args:
            issue_key: Issue key (e.g., LAB-101)
            **fields: Fields to update (summary, description, etc.)
            
        Returns:
            Success status
        """
        if self.demo_mode:
            for issue in self.demo_issues:
                if issue['key'] == issue_key:
                    issue.update(fields)
                    print(f"[DEMO] Updated {issue_key}")
                    return True
            print(f"[DEMO] Issue {issue_key} not found")
            return False
        
        issue = self.jira.issue(issue_key)
        issue.update(fields=fields)
        return True
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to an issue."""
        if self.demo_mode:
            print(f"[DEMO] Added comment to {issue_key}: {comment[:50]}...")
            return True
            
        issue = self.jira.issue(issue_key)
        self.jira.add_comment(issue, comment)
        return True
    
    def transition_issue(self, issue_key: str, status: str) -> bool:
        """
        Transition an issue to a new status.
        
        Args:
            issue_key: Issue key
            status: Target status name
            
        Returns:
            Success status
        """
        if self.demo_mode:
            for issue in self.demo_issues:
                if issue['key'] == issue_key:
                    issue['status'] = status
                    print(f"[DEMO] Transitioned {issue_key} to {status}")
                    return True
            return False
        
        issue = self.jira.issue(issue_key)
        transitions = self.jira.transitions(issue)
        
        for t in transitions:
            if t['name'].lower() == status.lower():
                self.jira.transition_issue(issue, t['id'])
                return True
                
        print(f"[ERROR] Transition to '{status}' not available")
        return False
    
    def generate_report(self, days: int = 7) -> Dict:
        """
        Generate a summary report.
        
        Args:
            days: Number of days to include
            
        Returns:
            Report dictionary
        """
        all_issues = self.search_issues(max_results=100)
        
        # Status breakdown
        status_counts = {}
        priority_counts = {}
        assignee_counts = {}
        
        for issue in all_issues:
            status = issue.get('status', 'Unknown')
            priority = issue.get('priority', 'Unknown')
            assignee = issue.get('assignee', 'Unassigned')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'total_issues': len(all_issues),
            'by_status': status_counts,
            'by_priority': priority_counts,
            'by_assignee': assignee_counts,
            'issues': all_issues
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Pretty print a report."""
        print("\n" + "="*60)
        print("LAB OPERATIONS REPORT")
        print("="*60)
        print(f"Generated: {report['generated_at']}")
        print(f"Total Issues: {report['total_issues']}")
        
        print("\n--- By Status ---")
        for status, count in report['by_status'].items():
            bar = "█" * count
            print(f"  {status:15} {bar} {count}")
        
        print("\n--- By Priority ---")
        for priority, count in report['by_priority'].items():
            bar = "█" * count
            print(f"  {priority:15} {bar} {count}")
        
        print("\n--- By Assignee ---")
        for assignee, count in report['by_assignee'].items():
            bar = "█" * count
            print(f"  {assignee or 'Unassigned':15} {bar} {count}")
        
        print("\n--- Open Issues ---")
        for issue in report['issues']:
            if issue['status'] != 'Done':
                print(f"  [{issue['priority']:8}] {issue['key']}: {issue['summary'][:40]}...")
        
        print("="*60 + "\n")
    
    def export_dashboard_data(self, filename: str = "dashboard_data.json"):
        """Export data for dashboard consumption."""
        report = self.generate_report()
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': report['total_issues'],
                'open': sum(1 for i in report['issues'] if i['status'] != 'Done'),
                'in_progress': report['by_status'].get('In Progress', 0),
                'critical': report['by_priority'].get('Critical', 0)
            },
            'charts': {
                'status_pie': report['by_status'],
                'priority_bar': report['by_priority'],
                'assignee_workload': report['by_assignee']
            },
            'recent_issues': report['issues'][:10]
        }
        
        with open(filename, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        print(f"[OK] Dashboard data exported to {filename}")
        return dashboard_data


# Pre-built maintenance ticket templates
TICKET_TEMPLATES = {
    'gpu_health_check': {
        'summary': 'DGX B200 Health Check - {location}',
        'description': '''Routine health check for DGX B200 system.

## Checklist
- [ ] Run nvidia-smi and verify all GPUs detected
- [ ] Check GPU temperatures (< 80°C under load)
- [ ] Verify memory (no ECC errors)
- [ ] Run NVSM health check
- [ ] Check NVLink status
- [ ] Verify network connectivity

## Notes
Location: {location}
System: DGX B200
''',
        'labels': ['gpu-maintenance', 'routine'],
        'priority': 'Medium'
    },
    'firmware_update': {
        'summary': 'Firmware Update Required - {component}',
        'description': '''Firmware update scheduled for {component}.

## Details
- Current Version: {current_version}
- Target Version: {target_version}
- Maintenance Window: {window}

## Pre-Update Checklist
- [ ] Backup configuration
- [ ] Notify users
- [ ] Verify firmware package

## Post-Update Verification
- [ ] Verify new version
- [ ] Run connectivity tests
- [ ] Update documentation
''',
        'labels': ['firmware', 'maintenance'],
        'priority': 'High'
    },
    'incident': {
        'summary': 'INCIDENT: {title}',
        'description': '''Incident report for {title}.

## Impact
{impact}

## Timeline
- Detected: {detected_time}
- Acknowledged: 
- Resolved: 

## Root Cause
TBD

## Resolution Steps
1. 

## Prevention
TBD
''',
        'labels': ['incident', 'troubleshooting'],
        'priority': 'Critical'
    }
}


def create_from_template(manager: JiraLabManager, template_name: str, **kwargs) -> Dict:
    """Create an issue from a template."""
    if template_name not in TICKET_TEMPLATES:
        print(f"[ERROR] Unknown template: {template_name}")
        print(f"Available: {', '.join(TICKET_TEMPLATES.keys())}")
        return None
    
    template = TICKET_TEMPLATES[template_name].copy()
    
    # Format strings with provided kwargs
    summary = template['summary'].format(**kwargs)
    description = template['description'].format(**kwargs)
    
    return manager.create_issue(
        summary=summary,
        description=description,
        labels=template.get('labels', []),
        priority=template.get('priority', 'Medium')
    )


def main():
    parser = argparse.ArgumentParser(description='Jira Lab Operations Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new issue')
    create_parser.add_argument('--summary', '-s', required=True, help='Issue summary')
    create_parser.add_argument('--description', '-d', default='', help='Description')
    create_parser.add_argument('--type', '-t', default='Task', help='Issue type')
    create_parser.add_argument('--priority', '-p', default='Medium', help='Priority')
    create_parser.add_argument('--labels', '-l', nargs='+', help='Labels')
    create_parser.add_argument('--assignee', '-a', help='Assignee username')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Create from template')
    template_parser.add_argument('name', choices=TICKET_TEMPLATES.keys())
    template_parser.add_argument('--vars', '-v', nargs='+', help='Template variables (key=value)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List issues')
    list_parser.add_argument('--status', '-s', help='Filter by status')
    list_parser.add_argument('--assignee', '-a', help='Filter by assignee')
    list_parser.add_argument('--labels', '-l', nargs='+', help='Filter by labels')
    list_parser.add_argument('--jql', help='Raw JQL query')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('--days', '-d', type=int, default=7, help='Days to include')
    report_parser.add_argument('--export', '-e', help='Export to JSON file')
    
    # My issues
    subparsers.add_parser('mine', help='Show my assigned issues')
    
    # Transition
    transition_parser = subparsers.add_parser('transition', help='Transition an issue')
    transition_parser.add_argument('issue', help='Issue key (e.g., LAB-101)')
    transition_parser.add_argument('status', help='Target status')
    
    # Comment
    comment_parser = subparsers.add_parser('comment', help='Add comment')
    comment_parser.add_argument('issue', help='Issue key')
    comment_parser.add_argument('text', help='Comment text')
    
    # Demo
    subparsers.add_parser('demo', help='Run demo with sample data')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = JiraLabManager()
    
    if args.command == 'create':
        result = manager.create_issue(
            summary=args.summary,
            description=args.description,
            issue_type=args.type,
            priority=args.priority,
            labels=args.labels,
            assignee=args.assignee
        )
        print(f"Created: {result['key']} - {result['summary']}")
    
    elif args.command == 'template':
        template_vars = {}
        if args.vars:
            for var in args.vars:
                key, value = var.split('=', 1)
                template_vars[key] = value
        result = create_from_template(manager, args.name, **template_vars)
        if result:
            print(f"Created: {result['key']} - {result['summary']}")
    
    elif args.command == 'list':
        issues = manager.search_issues(
            jql=args.jql,
            status=args.status,
            assignee=args.assignee,
            labels=args.labels
        )
        print(f"\nFound {len(issues)} issues:\n")
        for issue in issues:
            status_icon = {'Done': '✓', 'In Progress': '→', 'To Do': '○'}.get(issue['status'], '?')
            print(f"  {status_icon} [{issue['priority']:8}] {issue['key']}: {issue['summary']}")
    
    elif args.command == 'mine':
        issues = manager.get_my_issues()
        print(f"\nYour assigned issues ({len(issues)}):\n")
        for issue in issues:
            print(f"  [{issue['status']:12}] {issue['key']}: {issue['summary']}")
    
    elif args.command == 'report':
        report = manager.generate_report(days=args.days)
        manager.print_report(report)
        if args.export:
            manager.export_dashboard_data(args.export)
    
    elif args.command == 'transition':
        success = manager.transition_issue(args.issue, args.status)
        if success:
            print(f"Transitioned {args.issue} to {args.status}")
    
    elif args.command == 'comment':
        manager.add_comment(args.issue, args.text)
        print(f"Added comment to {args.issue}")
    
    elif args.command == 'demo':
        print("\n=== DEMO: Jira Lab Operations Manager ===\n")
        
        # Show all issues
        print("1. Listing all issues:")
        issues = manager.search_issues()
        for issue in issues:
            print(f"   {issue['key']}: {issue['summary']} [{issue['status']}]")
        
        # Create new issue
        print("\n2. Creating new issue:")
        new = manager.create_issue(
            summary="Test: New GPU monitoring script",
            description="Implement automated GPU monitoring",
            labels=['automation', 'monitoring']
        )
        print(f"   Created: {new['key']}")
        
        # Generate report
        print("\n3. Generating report:")
        report = manager.generate_report()
        manager.print_report(report)
        
        # Create from template
        print("4. Creating from template:")
        template_issue = create_from_template(
            manager, 
            'gpu_health_check',
            location='Rack A1'
        )
        print(f"   Created: {template_issue['key']}")


if __name__ == '__main__':
    main()
