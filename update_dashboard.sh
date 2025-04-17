#!/bin/zsh
# Script to update issues data and regenerate dashboard

# Set the working directory
cd "/Users/hollykassel/Documents/AI Week/Test"

# Set required environment variables (replace with your actual GitHub token)
# Ensure the GITHUB_TOKEN is set in the environment before running the script
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN is not set. Please export it before running this script."
  exit 1
fi

# Run the sync script to update issue data
python3 sync_issues.py

# Optional: run enhanced sync if needed
# python3 enhanced_sync_issues.py

# Run the dashboard generator
python3 run_dashboard.py

# Load the billing dashboard service
launchctl load ~/Library/LaunchAgents/com.user.billingdashboard.plist

# Log completion with timestamp
echo "Dashboard updated at $(date)" >> dashboard_update.log
