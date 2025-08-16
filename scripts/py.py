#!/usr/bin/env python3
import csv
import subprocess
import sys
import time

def create_github_issue(title, body, labels):
    """Create a GitHub issue using the gh CLI"""
    try:
        cmd = ['gh', 'issue', 'create', '--title', title, '--body', body, '--label', labels]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
        print(f"✓ Created issue: {title[:50]}...")
        return True
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout creating issue '{title[:50]}...': Request timed out")
        return False
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        print(f"✗ Failed to create issue '{title[:50]}...': {error_msg}")
        return False

def main():
    csv_file = 'issues.csv'
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            # Use csv.reader to properly handle quoted fields and embedded commas
            csv_reader = csv.reader(file)
            
            # Skip header row
            next(csv_reader)
            
            issue_count = 0
            success_count = 0
            
            for row in csv_reader:
                # Skip empty rows
                if not row or len(row) < 3:
                    continue
                
                title = row[0].strip()
                body = row[1].strip()
                labels = row[2].strip()
                
                # Skip rows with empty titles
                if not title:
                    continue
                
                issue_count += 1
                print(f"\nProcessing issue {issue_count}: {title[:50]}...")
                
                if create_github_issue(title, body, labels):
                    success_count += 1
                
                # Longer delay to avoid rate limiting and connection issues
                time.sleep(3)
            
            print(f"\n{'='*50}")
            print(f"Total issues processed: {issue_count}")
            print(f"Successfully created: {success_count}")
            print(f"Failed: {issue_count - success_count}")
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{csv_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()