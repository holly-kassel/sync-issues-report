# Sync Issues Report

This project provides a script to fetch and update issue states from the `github/billing-product` repository. The script updates a markdown file (`issues.md`) and a JSON file (`sync_issues_report.json`) with the latest issue information.

## Features
- Fetches issue states and titles from the GitHub repository.
- Updates a markdown table in `issues.md`.
- Generates a JSON report in `sync_issues_report.json`.
- Removes closed issues from the markdown file.

## Requirements
- Python 3.6+
- [PyGithub](https://github.com/PyGithub/PyGithub): Install using `pip install PyGithub`.

## Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/holly-kassel/sync-issues-report.git
   cd sync-issues-report
   ```
2. Install dependencies:
   ```bash
   pip install PyGithub
   ```
3. Set up your GitHub token as an environment variable:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

## Usage
Run the script to update the issue states:
```bash
python3 update_issue_states.py
```

## Files
- `update_issue_states.py`: Main script to fetch and update issue states.
- `issues.md`: Markdown file containing the issue table.
- `sync_issues_report.json`: JSON file containing issue details.

## Contributing
Feel free to fork this repository and submit pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.
