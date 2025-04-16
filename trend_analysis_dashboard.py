#!/usr/bin/env python3
"""
Billing Issues Trend Analysis Dashboard

This script processes GitHub issue data from JSON files to create an interactive
dashboard showing trends, themes, and backlog analysis of billing-related issues.
"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import re
from dateutil import parser

# Configuration
ISSUES_DIR = 'data/issues'
OUTPUT_FILE = 'billing_issues_dashboard.html'
THEME_KEYWORDS = {
    'billing': ['billing', 'payment', 'invoice', 'cost', 'charge', 'price'],
    'subscription': ['subscription', 'plan', 'tier', 'license', 'seat'],
    'infrastructure': ['infrastructure', 'platform', 'system', 'api', 'endpoint'],
    'ui/ux': ['ui', 'ux', 'interface', 'design', 'experience', 'navigation'],
    'enterprise': ['enterprise', 'organization', 'admin', 'manage', 'role', 'permission'],
    'copilot': ['copilot', 'ai', 'assistant', 'model'],
    'documentation': ['doc', 'documentation', 'help', 'guide', 'instruction'],
    'integration': ['integration', 'connect', 'azure', 'marketplace', 'zuora']
}

def extract_date_from_creation(issue):
    """
    Extract or estimate creation date from issue data.
    In a real GitHub API response we'd have this directly,
    but we need to simulate it for our demonstration.
    """
    # If we had real GitHub API data, it would include a 'created_at' field
    # Since we're working with simulated data, we'll use the issue number as a proxy
    # Assuming lower issue numbers are older (created earlier)
    
    # Use issue number to simulate creation date
    # Let's assume issue #1 was created on 2023-01-01, and each issue ~2 days after
    base_date = datetime(2023, 1, 1)
    if 'issue_number' in issue:
        days_offset = (issue['issue_number'] - 1) * 2  # Each issue ~2 days apart
        from datetime import timedelta
        return (base_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
    return None

def extract_themes(issue):
    """Extract themes from issue title and description"""
    themes = []
    
    # Check title for theme keywords
    title = issue.get('title', '').lower()
    
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in title for keyword in keywords):
            themes.append(theme)
            
    # If no specific theme is found, check for general categories
    if '[Epic]' in issue.get('title', ''):
        themes.append('epic')
    elif 'bug' in issue.get('title', '').lower() or '[bug]' in issue.get('title', '').lower():
        themes.append('bug')
    elif 'feature' in issue.get('title', '').lower() or '[feature]' in issue.get('title', '').lower():
        themes.append('feature')
    elif 'design' in issue.get('title', '').lower() or '[design]' in issue.get('title', '').lower():
        themes.append('design')
        
    # If still no theme identified, mark as 'other'
    if not themes:
        themes.append('other')
        
    return themes

def load_issue_data():
    """Load and process issue data from JSON files"""
    all_issues = []
    
    # Check if we have JSON files in the data directory
    json_files = [f for f in os.listdir(ISSUES_DIR) if f.endswith('.json')]
    
    # If no files in data directory, use the main sync_issues_report.json
    if not json_files:
        try:
            with open('sync_issues_report.json', 'r') as f:
                issue_data = json.load(f)
                all_issues = issue_data
        except FileNotFoundError:
            print("Error: Could not find sync_issues_report.json")
            return []
    else:
        # Load from all JSON files in the data directory
        for json_file in json_files:
            file_path = os.path.join(ISSUES_DIR, json_file)
            with open(file_path, 'r') as f:
                try:
                    issues = json.load(f)
                    if isinstance(issues, list):
                        all_issues.extend(issues)
                    else:
                        all_issues.append(issues)
                except json.JSONDecodeError:
                    print(f"Error: Could not parse JSON from {file_path}")
    
    return all_issues

def prepare_data_for_analysis(issues):
    """Convert issues to a pandas DataFrame for analysis"""
    processed_data = []
    
    today = datetime.now()
    current_date_str = today.strftime('%Y-%m-%d')
    
    for issue in issues:
        if isinstance(issue, dict) and ('title' in issue or 'issue_number' in issue):
            created_date = extract_date_from_creation(issue)
            
            # Skip if we couldn't determine a creation date
            if not created_date:
                continue
                
            # Calculate days in backlog
            try:
                created_datetime = parser.parse(created_date)
                days_in_backlog = (today - created_datetime).days
            except:
                days_in_backlog = 0
                
            # Extract themes
            themes = extract_themes(issue)
            theme_str = ', '.join(themes)
            
            # Extract state (open/closed)
            state = issue.get('state', 'unknown')
            
            # Issue data for analysis
            issue_data = {
                'issue_number': issue.get('issue_number', 'N/A'),
                'title': issue.get('title', 'Untitled Issue'),
                'state': state,
                'created_date': created_date,
                'days_in_backlog': days_in_backlog,
                'primary_theme': themes[0] if themes else 'other',
                'themes': theme_str,
                'ai_summary': issue.get('AI Summary', '')
            }
            
            processed_data.append(issue_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(processed_data)
    
    # Ensure date column is datetime type
    if 'created_date' in df.columns:
        df['created_date'] = pd.to_datetime(df['created_date'])
        
    # Add month and year columns for aggregation
    if 'created_date' in df.columns:
        df['month'] = df['created_date'].dt.strftime('%Y-%m')
        df['year'] = df['created_date'].dt.year
    
    return df

def generate_dashboard(df):
    """Generate the interactive dashboard using Plotly"""
    # Create a figure with subplots
    fig = make_subplots(
        rows=3, cols=2,
        specs=[
            [{"colspan": 2}, None],
            [{"colspan": 2}, None],
            [{}, {}]
        ],
        subplot_titles=(
            "Issue Creation Over Time", 
            "Backlog Age Distribution by Theme",
            "Theme Distribution", 
            "Open vs Closed Issues by Theme"
        ),
        vertical_spacing=0.1
    )

    # 1. Issues created over time (line chart)
    if 'created_date' in df.columns:
        monthly_issues = df.groupby('month').size().reset_index(name='count')
        monthly_issues = monthly_issues.sort_values('month')
        
        fig.add_trace(
            go.Scatter(
                x=monthly_issues['month'], 
                y=monthly_issues['count'],
                mode='lines+markers',
                name='Issues Created'
            ),
            row=1, col=1
        )
    
    # 2. Backlog age distribution by theme (box plot)
    if 'days_in_backlog' in df.columns and 'primary_theme' in df.columns:
        fig.add_trace(
            go.Box(
                x=df['primary_theme'],
                y=df['days_in_backlog'],
                name='Days in Backlog'
            ),
            row=2, col=1
        )
    
    # 3. Theme distribution (pie chart)
    if 'primary_theme' in df.columns:
        theme_counts = df['primary_theme'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=theme_counts.index,
                values=theme_counts.values,
                name='Theme Distribution'
            ),
            row=3, col=1
        )
    
    # 4. Open vs. Closed issues by theme (bar chart)
    if 'primary_theme' in df.columns and 'state' in df.columns:
        state_theme = df.groupby(['primary_theme', 'state']).size().unstack(fill_value=0)
        
        # Handle the case where 'open' or 'closed' columns might not exist
        if 'open' not in state_theme.columns:
            state_theme['open'] = 0
        if 'closed' not in state_theme.columns:
            state_theme['closed'] = 0
        
        fig.add_trace(
            go.Bar(
                x=state_theme.index,
                y=state_theme['open'],
                name='Open Issues'
            ),
            row=3, col=2
        )
        
        if 'closed' in state_theme.columns:
            fig.add_trace(
                go.Bar(
                    x=state_theme.index,
                    y=state_theme['closed'],
                    name='Closed Issues'
                ),
                row=3, col=2
            )
    
    # Update layout for better appearance
    fig.update_layout(
        title_text="Billing Issues Trend Analysis Dashboard",
        height=1200,
        legend=dict(orientation="h", y=-0.1),
        template="plotly_white"
    )
    
    # Save the dashboard to an HTML file
    fig.write_html(OUTPUT_FILE)
    print(f"Dashboard saved to {OUTPUT_FILE}")
    
    return fig

def create_issue_table(df):
    """Create a sortable table of issues"""
    table_file = 'billing_issues_table.html'
    
    # Sort by days in backlog (descending)
    if 'days_in_backlog' in df.columns:
        df_sorted = df.sort_values('days_in_backlog', ascending=False)
    else:
        df_sorted = df
    
    # Create a styled HTML table
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Billing Issues Analysis - Issue Table</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333366; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; cursor: pointer; }
            tr:hover { background-color: #f5f5f5; }
            .sorter:after { content: " ⇵"; color: #999; }
        </style>
        <script>
            function sortTable(n) {
                var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                table = document.getElementById("issueTable");
                switching = true;
                dir = "asc";
                while (switching) {
                    switching = false;
                    rows = table.rows;
                    for (i = 1; i < (rows.length - 1); i++) {
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName("TD")[n];
                        y = rows[i + 1].getElementsByTagName("TD")[n];
                        
                        if (dir == "asc") {
                            if (isNaN(x.innerHTML) && isNaN(y.innerHTML)) {
                                // Text comparison
                                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                                    shouldSwitch = true;
                                    break;
                                }
                            } else {
                                // Numeric comparison
                                if (Number(x.innerHTML) > Number(y.innerHTML)) {
                                    shouldSwitch= true;
                                    break;
                                }
                            }
                        } else if (dir == "desc") {
                            if (isNaN(x.innerHTML) && isNaN(y.innerHTML)) {
                                // Text comparison
                                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                                    shouldSwitch = true;
                                    break;
                                }
                            } else {
                                // Numeric comparison
                                if (Number(x.innerHTML) < Number(y.innerHTML)) {
                                    shouldSwitch = true;
                                    break;
                                }
                            }
                        }
                    }
                    if (shouldSwitch) {
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount ++;
                    } else {
                        if (switchcount == 0 && dir == "asc") {
                            dir = "desc";
                            switching = true;
                        }
                    }
                }
            }
        </script>
    </head>
    <body>
        <h1>Billing Issues Analysis - Sortable Issue Table</h1>
        <p>Click on column headers to sort. Issues are initially sorted by days in backlog (descending).</p>
        <table id="issueTable">
            <tr>
                <th class="sorter" onclick="sortTable(0)">Issue #</th>
                <th class="sorter" onclick="sortTable(1)">Title</th>
                <th class="sorter" onclick="sortTable(2)">State</th>
                <th class="sorter" onclick="sortTable(3)">Created Date</th>
                <th class="sorter" onclick="sortTable(4)">Days in Backlog</th>
                <th class="sorter" onclick="sortTable(5)">Theme</th>
                <th class="sorter" onclick="sortTable(6)">AI Summary</th>
            </tr>
    """
    
    # Add rows for each issue
    for _, row in df_sorted.iterrows():
        issue_num = row.get('issue_number', 'N/A')
        title = row.get('title', 'Untitled Issue')
        state = row.get('state', 'unknown')
        created_date = row.get('created_date', '')
        if created_date and not isinstance(created_date, str):
            created_date = created_date.strftime('%Y-%m-%d')
        days_in_backlog = row.get('days_in_backlog', 0)
        theme = row.get('primary_theme', 'other')
        ai_summary = row.get('ai_summary', '')
        
        html_content += f"""
            <tr>
                <td>{issue_num}</td>
                <td>{title}</td>
                <td>{state}</td>
                <td>{created_date}</td>
                <td>{days_in_backlog}</td>
                <td>{theme}</td>
                <td>{ai_summary}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    # Write to file
    with open(table_file, 'w') as f:
        f.write(html_content)
    
    print(f"Issue table saved to {table_file}")

def main():
    """Main function to run the dashboard generation"""
    print("Loading issue data...")
    issues = load_issue_data()
    
    if not issues:
        print("No issue data found. Please check your data files.")
        return
    
    print(f"Loaded {len(issues)} issues. Preparing data for analysis...")
    df = prepare_data_for_analysis(issues)
    
    print("Generating dashboard...")
    generate_dashboard(df)
    
    print("Creating sortable issue table...")
    create_issue_table(df)
    
    print("Dashboard generation complete!")

if __name__ == "__main__":
    main()
