#!/usr/bin/env python3
"""
This script synchronizes the issues from the github/billing-product repository
and generates AI summaries based on issue descriptions and comments.

Requirements:
- Python 3.6+
- PyGithub package: pip install PyGithub
- requests package: pip install requests
"""

import os
import json
import sys
import requests
import tempfile
from github import Github
from pathlib import Path

# You'll need to set these environment variables
# export GITHUB_TOKEN=your_token_here
TOKEN = os.environ.get("GITHUB_TOKEN")

# Path to save the JSON report
REPORT_FILE = Path("sync_issues_report.json")

def generate_ai_summary(issue_data):
    """
    Generate an AI summary for the issue using GitHub's model API
    """
    # Create the prompt for the AI model
    prompt = f"""
    Issue Title: {issue_data['title']}
    
    Issue Description:
    {issue_data['description']}
    
    Issue Comments (up to 5):
    {' '.join(issue_data['comments'][:5])}
    
    Generate a concise summary (under 250 characters) of the problem being solved in this issue. 
    Focus on the core problem rather than just rephrasing the title. Include important context from the description and comments.
    """

    model_input = {
        "model": "github-model",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes GitHub issues."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100
    }

    # Save the model input to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(model_input, tmp)
        input_file = tmp.name

    try:
        # Using curl through os.system to invoke GitHub's model API
        cmd = f'''curl -s "https://models.github.ai/inference/chat/completions" \\
                -H "Content-Type: application/json" \\
                -H "Authorization: Bearer {TOKEN}" \\
                -d @{input_file}'''
        
        response = os.popen(cmd).read()
        response_data = json.loads(response)
        
        # Extract the generated summary from the response
        summary = response_data["choices"][0]["message"]["content"].strip()
        
        # Remove temporary file
        os.unlink(input_file)
        
        return summary
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        if os.path.exists(input_file):
            os.unlink(input_file)
        return "Failed to generate AI summary."

def get_issue_data(repo, issue):
    """
    Extract detailed data from a GitHub issue
    """
    description = issue.body or ""
    
    # Get comments
    comments_text = []
    try:
        comments = issue.get_comments()
        for comment in comments:
            comments_text.append(comment.body)
    except Exception as e:
        print(f"Error fetching comments for issue #{issue.number}: {e}")
    
    return {
        "issue_number": issue.number,
        "state": issue.state,
        "title": issue.title,
        "description": description,
        "comments": comments_text
    }

def main():
    if not TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set it with: export GITHUB_TOKEN=your_token_here")
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
    issues_data = []

    try:
        open_issues = repo.get_issues(state="open")
        issue_count = 0

        for issue in open_issues:
            issue_count += 1
            print(f"Processing issue #{issue.number}: {issue.title}")
            
            # Get detailed issue data
            issue_data = get_issue_data(repo, issue)
            
            # Generate AI summary
            print(f"Generating AI summary for issue #{issue.number}")
            ai_summary = generate_ai_summary(issue_data)
            
            # Create the final issue entry for our JSON
            issues_entry = {
                "issue_number": issue_data["issue_number"],
                "state": issue_data["state"],
                "title": issue_data["title"],
                "AI Summary": ai_summary
            }
            
            issues_data.append(issues_entry)
            
            # Add a small progress indicator
            if issue_count % 10 == 0:
                print(f"Processed {issue_count} issues...")
        
        # Save to JSON file
        with open(REPORT_FILE, "w") as f:
            json.dump(issues_data, f, indent=4)
            
        print(f"✅ Successfully processed {issue_count} issues and saved to {REPORT_FILE}")
        
    except Exception as e:
        print(f"Error processing issues: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
