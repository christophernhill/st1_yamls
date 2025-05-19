#!/usr/bin/env python3

import csv
import argparse
import sys
import os
from datetime import datetime

def csvs_to_html(csv_data_dict):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>CSV Table Viewer</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            width: 100%;
            max-width: none;
            margin: 0;
            background-color: white;
            padding: 0;
            border-radius: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .tabs {{
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border: 1px solid transparent;
            border-bottom: none;
            margin-right: 5px;
            border-radius: 4px 4px 0 0;
            background-color: #f8f9fa;
        }}
        .tab.active {{
            background-color: white;
            border-color: #ddd;
            border-bottom-color: white;
            margin-bottom: -1px;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .csv-table-wrapper {{
            overflow-x: auto;
            margin-bottom: 20px;
            width: 100%;
        }}
        table.csv-table {{
            border-collapse: collapse;
            width: 100%;
            min-width: 100%;
            background: #fff;
        }}
        table.csv-table th, table.csv-table td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
            font-size: 15px;
        }}
        table.csv-table th {{
            background-color: #f2f2f2;
            color: #333;
            font-weight: bold;
        }}
        table.csv-table tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.8em;
            text-align: right;
            margin-top: 20px;
        }}
    </style>
    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            var tabBtn = document.getElementById('tab-' + tabId);
            var tabContent = document.getElementById('tab-' + tabId + '-content');
            if (tabBtn && tabContent) {{
                tabBtn.classList.add('active');
                tabContent.classList.add('active');
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>CSV Table Viewer</h1>
        <div class="tabs">
{generate_tabs(csv_data_dict)}
        </div>
{generate_tab_contents(csv_data_dict)}
        <div class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
</body>
</html>"""
    output_file = "browse_csvs.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return output_file

def generate_tabs(csv_data_dict):
    tabs = []
    for i, (filename, _) in enumerate(csv_data_dict.items()):
        tab_id = os.path.splitext(os.path.basename(filename))[0].replace('.', '_')
        active_class = ' active' if i == 0 else ''
        tabs.append(f'            <div class="tab{active_class}" id="tab-{tab_id}" onclick="switchTab(\'{tab_id}\')">{os.path.basename(filename)}</div>')
    return '\n'.join(tabs)

def generate_tab_contents(csv_data_dict):
    contents = []
    for i, (filename, rows) in enumerate(csv_data_dict.items()):
        tab_id = os.path.splitext(os.path.basename(filename))[0].replace('.', '_')
        active_class = ' active' if i == 0 else ''
        table_html = csv_rows_to_table(rows)
        content = f"""        <div id="tab-{tab_id}-content" class="tab-content{active_class}">
            <div class="csv-table-wrapper">
{table_html}
            </div>
        </div>"""
        contents.append(content)
    return '\n'.join(contents)

def csv_rows_to_table(rows):
    if not rows:
        return '<p><em>No data found in this CSV.</em></p>'
    header = rows[0]
    table = ['<table class="csv-table">']
    # Header
    table.append('<tr>' + ''.join(f'<th>{escape_html(col)}</th>' for col in header) + '</tr>')
    # Rows
    for row in rows[1:]:
        table.append('<tr>' + ''.join(f'<td>{escape_html(cell)}</td>' for cell in row) + '</tr>')
    table.append('</table>')
    return '\n'.join(table)

def escape_html(text):
    # First escape HTML special characters (except ×)
    escaped = (str(text)
               .replace('&', '&amp;')
               .replace('<', '&lt;')
               .replace('>', '&gt;')
               .replace('"', '&quot;')
               .replace("'", '&#39;'))
    # Now replace the times symbol with the HTML entity
    return escaped.replace('×', '&times;')

def read_csv_files(csv_files):
    csv_data_dict = {}
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                csv_data_dict[csv_file] = rows
        except FileNotFoundError:
            print(f"Error: File '{csv_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading '{csv_file}': {e}")
            sys.exit(1)
    return csv_data_dict

def main():
    parser = argparse.ArgumentParser(description='Convert CSV files to a tabbed HTML table viewer')
    parser.add_argument('csv_files', nargs='+', help='Path(s) to the CSV file(s) to convert')
    args = parser.parse_args()

    csv_data_dict = read_csv_files(args.csv_files)
    output_file = csvs_to_html(csv_data_dict)
    print(f"HTML file generated: {output_file}")

if __name__ == "__main__":
    main() 