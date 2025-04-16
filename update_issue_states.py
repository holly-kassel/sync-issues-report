#!/usr/bin/env python3
"""
This script updates the issues.md file by adding the state of each issue from 
the github/billing-product repository and writes the issue states to a JSON file.

Requirements:
- Python 3.6+
- PyGithub package: pip install PyGithub
"""

import os
import re
import sys
from github import Github
from pathlib import Path

# You'll need to set this environment variable with your GitHub token
# that has access to the github/billing-product repository
# export GITHUB_TOKEN=your_token_here
TOKEN = os.environ.get("GITHUB_TOKEN")

# Update the path to issues.md to use an absolute path
ISSUES_FILE = Path("/Users/hollykassel/Documents/AI Week/Test/issues.md")

# Path to the JSON file for issue states
JSON_FILE_PATH = Path("/Users/hollykassel/Documents/AI Week/Test/sync_issues_report.json")

def main():
    if not TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set it with: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    if not ISSUES_FILE.exists():
        print(f"Error: {ISSUES_FILE} not found.")
        sys.exit(1)
    
    # Initialize GitHub API client
    g = Github(TOKEN)
    
    try:
        # Get the repository
        repo = g.get_repo("github/billing-product")
        print(f"Successfully connected to repository: github/billing-product")
    except Exception as e:
        print(f"Error accessing repository: {e}")
        sys.exit(1)
    
    # Read the issues.md file
    with open(ISSUES_FILE, "r") as f:
        content = f.read()
    
    # Extract all issue/PR links and numbers
    issue_pattern = r'\[(\d+)\]\(https://github\.com/github/billing-product/issues/(\d+)\)'
    pr_pattern = r'\[(\d+)\]\(https://github\.com/github/billing-product/pull/(\d+)\)'
    
    # Find all issues and PRs in the file
    issue_matches = re.finditer(issue_pattern, content)
    pr_matches = re.finditer(pr_pattern, content)
    
    # Prepare a dictionary to store the issue/PR numbers and their states
    issue_states = {}
    
    # Process issues
    print("Fetching issue states...")
    for match in issue_matches:
        issue_num = int(match.group(1))
        try:
            issue = repo.get_issue(issue_num)
            issue_states[issue_num] = issue.state
            print(f"Issue #{issue_num}: {issue.state}")
        except Exception as e:
            print(f"Error fetching issue #{issue_num}: {e}")
            issue_states[issue_num] = "unknown"
    
    # Process pull requests
    print("Fetching pull request states...")
    for match in pr_matches:
        pr_num = int(match.group(1))
        try:
            pr = repo.get_pull(pr_num)
            # PRs can be open, closed, or merged
            state = "merged" if pr.merged else pr.state
            issue_states[pr_num] = state
            print(f"PR #{pr_num}: {state}")
        except Exception as e:
            print(f"Error fetching PR #{pr_num}: {e}")
            issue_states[pr_num] = "unknown"
    
    # Update the markdown table to include states and remove closed issues
    updated_content = []
    in_table = False
    for line in content.split('\n'):
        if not in_table and '| Issue Number | Issue Title |' in line:
            # Found the table header, modify it to include State column
            updated_content.append('| Issue Number | Issue Title | State |')
            in_table = True
        elif not in_table and '| Issue Number | Issue Title | State |' in line:
            # Header already includes State column
            updated_content.append(line)
            in_table = True
        elif in_table and '|--' in line:
            # Found the separator row, update it to include State column
            updated_content.append('|--------------|-------------|-------|')
        elif in_table and '| [' in line:
            # Found an issue row, check its state
            issue_match = re.search(r'\[(\d+)\]', line)
            if issue_match:
                issue_num = int(issue_match.group(1))
                state = issue_states.get(issue_num, "unknown")
                if state != "closed":
                    # Only include issues that are not closed
                    if not line.endswith('|'):
                        updated_content.append(f"{line} {state} |")
                    else:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 4:  # Has at least Issue Number, Title and State columns
                            updated_line = f"| {parts[1]} | {parts[2]} | {state} |"
                            updated_content.append(updated_line)
                        else:
                            updated_content.append(line)
        else:
            updated_content.append(line)
    
    # Write the updated content back to the file
    with open(ISSUES_FILE, "w") as f:
        f.write('\n'.join(updated_content))
    
    print(f"Successfully updated issue states in {ISSUES_FILE}")

    # Prepare data for JSON output
    json_data = []
    for issue_num, state in issue_states.items():
        try:
            issue = repo.get_issue(issue_num)
            json_data.append({
                "issue_number": issue_num,
                "state": state,
                "title": issue.title
            })
        except Exception as e:
            print(f"Error fetching title for issue #{issue_num}: {e}")
            json_data.append({
                "issue_number": issue_num,
                "state": state,
                "title": "unknown"
            })

    # Write the JSON data to sync_issues_report.json
    with open(JSON_FILE_PATH, "w") as json_file:
        import json
        json.dump(json_data, json_file, indent=4)

    print(f"Successfully wrote issue states with titles to {JSON_FILE_PATH}")

if __name__ == "__main__":
    main()
