#!/usr/bin/env python3

import yaml
import argparse
import sys
import os
from datetime import datetime

def yaml_to_html(data, filename):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>YAML Viewer</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .yaml-content {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            white-space: pre-wrap;
            font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
            line-height: 1.5;
        }}
        .key {{
            color: #2c3e50;
            font-weight: bold;
            cursor: pointer;
        }}
        .value {{
            color: #27ae60;
        }}
        .number {{
            color: #e67e22;
        }}
        .null {{
            color: #95a5a6;
            font-style: italic;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.8em;
            text-align: right;
            margin-top: 20px;
        }}
        .collapsible {{
            cursor: pointer;
            user-select: none;
            position: relative;
            padding-left: 15px;
            margin: 2px 0;
        }}
        .collapsible::before {{
            content: '+';
            position: absolute;
            left: 0;
            color: #666;
            font-weight: bold;
            font-size: 14px;
            line-height: 1;
            width: 12px;
            text-align: center;
        }}
        .collapsible.collapsed::before {{
            content: '+';
        }}
        .collapsible:not(.collapsed)::before {{
            content: '-';
        }}
        .collapsible-content {{
            margin-left: 15px;
            display: block;
            border-left: 1px solid #ddd;
            padding-left: 10px;
        }}
        .collapsible-content.collapsed {{
            display: none;
        }}
        .controls {{
            margin-bottom: 20px;
        }}
        .controls button {{
            padding: 8px 16px;
            margin-right: 10px;
            border: none;
            border-radius: 4px;
            background-color: #3498db;
            color: white;
            cursor: pointer;
            transition: background-color 0.2s;
            font-family: inherit;
        }}
        .controls button:hover {{
            background-color: #2980b9;
        }}
        .list-item {{
            position: relative;
            padding-left: 15px;
            margin: 2px 0;
        }}
        .list-item::before {{
            content: '-';
            position: absolute;
            left: 0;
            color: #666;
            width: 12px;
            text-align: center;
        }}
        .list-container {{
            margin-left: 15px;
            border-left: 1px solid #ddd;
            padding-left: 10px;
        }}
        /* Tab styles */
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
    </style>
    <script>
        function toggleCollapse(element) {{
            element.classList.toggle('collapsed');
            const content = element.nextElementSibling;
            content.classList.toggle('collapsed');
        }}

        function expandAll() {{
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab) {{
                activeTab.querySelectorAll('.collapsible').forEach(el => {{
                    el.classList.remove('collapsed');
                    el.nextElementSibling.classList.remove('collapsed');
                }});
            }}
        }}

        function collapseAll() {{
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab) {{
                activeTab.querySelectorAll('.collapsible').forEach(el => {{
                    el.classList.add('collapsed');
                    el.nextElementSibling.classList.add('collapsed');
                }});
            }}
        }}

        function switchTab(tabId) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            // Deactivate all tabs
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            // Activate selected tab and content
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
        <h1>YAML Viewer</h1>
        <div class="tabs">
{generate_tabs(data)}
        </div>
        <div class="controls">
            <button onclick="expandAll()">Expand All</button>
            <button onclick="collapseAll()">Collapse All</button>
        </div>
{generate_tab_contents(data)}
        <div class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>
</body>
</html>"""
    
    output_file = "browse_yamls.html"
    with open(output_file, 'w') as f:
        f.write(html_content)
    return output_file

def generate_tabs(data):
    tabs = []
    for i, (filename, _) in enumerate(data.items()):
        tab_id = os.path.splitext(os.path.basename(filename))[0].replace('.', '_')
        active_class = ' active' if i == 0 else ''
        tabs.append(f'            <div class="tab{active_class}" id="tab-{tab_id}" onclick="switchTab(\'{tab_id}\')">{os.path.basename(filename)}</div>')
    return '\n'.join(tabs)

def generate_tab_contents(data):
    contents = []
    for i, (filename, yaml_data) in enumerate(data.items()):
        tab_id = os.path.splitext(os.path.basename(filename))[0].replace('.', '_')
        active_class = ' active' if i == 0 else ''
        content = f"""        <div id="tab-{tab_id}-content" class="tab-content{active_class}">
            <div class="yaml-content">
{format_yaml_for_html(yaml_data, top_level=True)}
            </div>
        </div>"""
        contents.append(content)
    return '\n'.join(contents)

def format_yaml_for_html(data, indent=0, top_level=False):
    if isinstance(data, dict):
        items = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                collapsed_class = '' if top_level else ' collapsed'
                items.append(f"{'  ' * indent}<div class='collapsible{collapsed_class}' onclick='toggleCollapse(this)'><span class='key'>{k}:</span></div>")
                items.append(f"{'  ' * indent}<div class='collapsible-content{collapsed_class}'>{format_yaml_for_html(v, indent + 1, top_level=False)}</div>")
            else:
                items.append(f"{'  ' * indent}<span class='key'>{k}:</span> {format_yaml_for_html(v, indent + 1, top_level=False)}")
        return '\n'.join(items)
    elif isinstance(data, list):
        items = []
        for item in data:
            if isinstance(item, (dict, list)):
                collapsed_class = '' if top_level else ' collapsed'
                items.append(f"{'  ' * indent}<div class='collapsible{collapsed_class}' onclick='toggleCollapse(this)'><span class='list-item'></span></div>")
                items.append(f"{'  ' * indent}<div class='collapsible-content list-container{collapsed_class}'>{format_yaml_for_html(item, indent + 1, top_level=False)}</div>")
            else:
                items.append(f"{'  ' * indent}<span class='list-item'></span> {format_yaml_for_html(item, indent + 1, top_level=False)}")
        return '\n'.join(items)
    elif data is None:
        return "<span class='null'>null</span>"
    elif isinstance(data, (int, float)):
        return f"<span class='number'>{data}</span>"
    else:
        return f"<span class='value'>{str(data)}</span>"

def pretty_print_yaml(yaml_files):
    try:
        data = {}
        for yaml_file in yaml_files:
            with open(yaml_file, 'r') as file:
                data[yaml_file] = yaml.safe_load(file)
        output_file = yaml_to_html(data, yaml_files[0])
        print(f"HTML file generated: {output_file}")
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Convert YAML files to formatted HTML')
    parser.add_argument('yaml_files', nargs='+', help='Path(s) to the YAML file(s) to convert')
    args = parser.parse_args()

    pretty_print_yaml(args.yaml_files)

if __name__ == "__main__":
    main() 