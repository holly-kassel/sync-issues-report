#!/usr/bin/env python3
"""
This script synchronizes the issues.md file with the current state of open issues
from the github/billing-product repository.

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

# Path to the issues.md file
ISSUES_FILE = Path("issues.md")

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

    # Fetch all open issues from the repository
    print("Fetching open issues from the repository...")
    open_issues = {issue.number: issue for issue in repo.get_issues(state="open")}

    # Read the issues.md file
    with open(ISSUES_FILE, "r") as f:
        content = f.read()

    # Extract all issue numbers from the file
    issue_pattern = r'\[(\d+)\]\(https://github\\.com/github/billing-product/issues/(\d+)\)'
    matches = re.finditer(issue_pattern, content)

    # Prepare a dictionary to store the issues currently in the file
    file_issues = {}
    for match in matches:
        issue_num = int(match.group(1))
        file_issues[issue_num] = match.group(0)

    # Prepare updated content
    updated_content = []
    in_table = False
    for line in content.split('\n'):
        if not in_table and '| Issue Number | Issue Title |' in line:
            updated_content.append(line)
            in_table = True
        elif in_table and '|--' in line:
            updated_content.append(line)
        elif in_table and '| [' in line:
            # Extract issue number from the line
            issue_match = re.search(r'\[(\d+)\]', line)
            if issue_match:
                issue_num = int(issue_match.group(1))
                if issue_num in open_issues:
                    # Update the state if necessary
                    issue = open_issues[issue_num]
                    parts = [p.strip() for p in line.split('|')]
                    updated_line = f"| [{issue.number}](https://github.com/github/billing-product/issues/{issue.number}) | {issue.title} | {issue.state} |"
                    updated_content.append(updated_line)
                    del open_issues[issue_num]  # Remove from open_issues as it's already handled
                else:
                    # Issue is no longer open, skip it
                    continue
            else:
                updated_content.append(line)
        else:
            updated_content.append(line)

    # Add new open issues that are not in the file
    for issue_num, issue in open_issues.items():
        updated_content.append(f"| [{issue.number}](https://github.com/github/billing-product/issues/{issue.number}) | {issue.title} | {issue.state} |")

    # Write the updated content back to the file
    with open(ISSUES_FILE, "w") as f:
        f.write('\n'.join(updated_content))

    print(f"Successfully synchronized issues in {ISSUES_FILE}")

if __name__ == "__main__":
    main()
