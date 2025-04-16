#!/usr/bin/env python3
"""
Run Billing Issues Trend Analysis Dashboard

This simple script serves as an entry point to run the trend analysis dashboard.
"""

import os
import sys
from trend_analysis_dashboard import main

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data/issues", exist_ok=True)
    
    # Run the dashboard
    main()
    
    print("\nDashboard generation complete!")
    print("Open billing_issues_dashboard.html in your browser to view the interactive dashboard.")
    print("Open billing_issues_table.html to view the sortable issues table.")
