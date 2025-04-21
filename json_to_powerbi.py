#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON to Power BI Converter

This script converts the existing sync_issues_report.json file to formats
that Power BI can directly consume (Excel/CSV).
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class JSONToPowerBI:
    def __init__(self, json_file, output_dir="data"):
        """
        Initialize the JSON to Power BI converter.
        
        Args:
            json_file (str): Path to the JSON file containing issues data
            output_dir (str): Directory to save output files
        """
        self.json_file = json_file
        self.output_dir = output_dir
        self.issues_data = []
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_json_data(self):
        """
        Load the issues data from the JSON file.
        
        Returns:
            list: Issues data
        """
        try:
            with open(self.json_file, 'r') as f:
                self.issues_data = json.load(f)
            logger.info(f"Loaded {len(self.issues_data)} issues from {self.json_file}")
            return self.issues_data
        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            return []
    
    def calculate_metrics(self, issues=None):
        """
        Calculate various metrics from issues data.
        
        Args:
            issues (list, optional): List of issues to analyze.
                                   If None, use the ones we've already loaded.
        
        Returns:
            dict: Calculated metrics
        """
        if issues is None:
            issues = self.issues_data
            
        if not issues:
            return {}
        
        # Calculate metrics
        total_issues = len(issues)
        open_issues = sum(1 for i in issues if i.get("state") == "open")
        closed_issues = sum(1 for i in issues if i.get("state") == "closed")
        
        # Count epic-related issues (based on title or labels)
        epics = sum(1 for i in issues if "epic" in i.get("title", "").lower())
        
        # Calculate additional metrics where possible
        # These calculations may need adjustment based on your actual data structure
        
        return {
            "total_issues": total_issues,
            "open_issues": open_issues,
            "closed_issues": closed_issues,
            "percent_closed": (closed_issues / total_issues * 100) if total_issues > 0 else 0,
            "epics_count": epics
        }
    
    def export_to_excel(self, filename="github_issues_data.xlsx"):
        """
        Export all data to Excel for Power BI consumption.
        
        Args:
            filename (str): Output filename
            
        Returns:
            str: Path to the created Excel file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Convert issues data to DataFrame
            if self.issues_data:
                issues_df = pd.DataFrame(self.issues_data)
                issues_df.to_excel(writer, sheet_name="Issues", index=False)
            
            # Add metrics
            metrics = self.calculate_metrics()
            if metrics:
                # Convert metrics to a format that can be saved in Excel
                metrics_data = []
                for key, value in metrics.items():
                    metrics_data.append({"Metric": key, "Value": value})
                
                metrics_df = pd.DataFrame(metrics_data)
                metrics_df.to_excel(writer, sheet_name="Metrics", index=False)
        
        logger.info(f"Data exported to {filepath}")
        return filepath
    
    def export_to_csv(self, base_filename="sync_issues"):
        """
        Export all data to separate CSV files for Power BI consumption.
        
        Args:
            base_filename (str): Base filename for CSV files.
        
        Returns:
            dict: Paths to the created CSV files
        """
        csv_files = {}
        
        # Export issues
        if self.issues_data:
            issues_filepath = os.path.join(self.output_dir, f"{base_filename}_issues.csv")
            issues_df = pd.DataFrame(self.issues_data)
            issues_df.to_csv(issues_filepath, index=False, encoding='utf-8-sig')
            csv_files["issues"] = issues_filepath
            logger.info(f"Issues data exported to {issues_filepath}")
            
        # Export metrics
        metrics = self.calculate_metrics()
        if metrics:
            metrics_filepath = os.path.join(self.output_dir, f"{base_filename}_metrics.csv")
            metrics_data = []
            for key, value in metrics.items():
                metrics_data.append({"Metric": key, "Value": value})
            
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_csv(metrics_filepath, index=False, encoding='utf-8-sig')
            csv_files["metrics"] = metrics_filepath
            logger.info(f"Metrics data exported to {metrics_filepath}")
            
        return csv_files
    
    def export_to_json(self, filename="github_issues_data.json"):
        """
        Export the processed data back to JSON in a format optimized for Power BI.
        
        Args:
            filename (str): Output filename
            
        Returns:
            str: Path to the created JSON file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        # Combine issues and metrics into a single JSON structure
        output_data = {
            "issues": self.issues_data,
            "metrics": self.calculate_metrics()
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(output_data, f, indent=2)
            logger.info(f"Data exported to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return None

def main():
    # Set the path to your JSON file and output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, "sync_issues_report.json")
    output_dir = os.path.join(script_dir, "data")
    
    # Create converter and load data
    converter = JSONToPowerBI(json_file, output_dir)
    converter.load_json_data()
    
    # Export data in different formats
    converter.export_to_excel()
    converter.export_to_csv()
    converter.export_to_json()
    
    logger.info("All exports completed successfully!")
    
if __name__ == "__main__":
    main()
