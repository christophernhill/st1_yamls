import yaml
import os
import pandas as pd
import argparse
import math

def read_yaml_files(): 
    yaml_files = ['lenovo.yaml', 'cambridge.yaml', 'ibm.yaml', 'markiii.yaml' , 'penguin.yaml']
    yaml_dicts = {}
    
    for file_name in yaml_files:
        try:
            with open(file_name, 'r') as file:
                # Read the file as-is, preserving indentation
                yaml_dicts[file_name] = yaml.safe_load(file)
                print(f"Successfully read {file_name}")
        except yaml.YAMLError as e:
            print(f"YAML error in {file_name}: {e}")
        except Exception as e:
            print(f"Error reading {file_name}: {str(e)}")
    
    return yaml_dicts

def extract_item_fields(data, alpha_percent=None, is_hs=False):
    if isinstance(data, dict):
        label = data.get('item_label', '')
        count = data.get('item_count', '')
        if count and alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            # Special handling for PiB values in hs
            if is_hs and isinstance(count, str) and 'PiB' in count:
                try:
                    count_numeric = ''.join([c for c in count if (c.isdigit() or c == '.' )])
                    count_value = float(count_numeric)
                    adjusted_count = f"{count_value * alpha_float:.1f}PiB"
                    return f"{label} (×{count},{adjusted_count})"
                except Exception:
                    return f"{label} (×{count})"
            # For other values, round down
            try:
                count_value = float(count)
                adjusted_count = math.floor(count_value * alpha_float)
                return f"{label} (×{count},{adjusted_count})"
            except (ValueError, TypeError):
                return f"{label} (×{count})"
        return f"{label} (×{count})" if count else label
    elif isinstance(data, str) and is_hs and 'PiB' in data:
        # Handle the case where hs is just a string like '14PiB'
        try:
            count_numeric = ''.join([c for c in data if (c.isdigit() or c == '.' )])
            count_value = float(count_numeric)
            if alpha_percent is not None:
                alpha_float = float(alpha_percent.strip('%')) / 100
                adjusted_count = f"{count_value * alpha_float:.1f}PiB"
                return f"(×{data},{adjusted_count})"
            else:
                return f"(×{data})"
        except Exception:
            return data
    elif isinstance(data, list):
        return [extract_item_fields(item, alpha_percent, is_hs) for item in data]
    return ''

def yaml_dicts_to_dataframe(yaml_dicts):
    columns = [
        'rfp_no', 'lead_org', 't1', 't2', 'hn', 'cn', 'hs', 'cs', 'sn', 'sstack', 'total_price'
    ]
    rows = []
    for file_name, data in yaml_dicts.items():
        rfp = data.get('rfp', {})
        row = {col: rfp.get(col, None) for col in columns}
        rows.append(row)
    df = pd.DataFrame(rows, columns=columns)
    return df

def extract_b2_value(t1_data, alpha_percent=None):
    # If it's a list, search for b200_8way in the list
    if isinstance(t1_data, list):
        for item in t1_data:
            if isinstance(item, dict) and item.get('item_label') == 'b200_8way':
                gpu_count = item.get('gpu_count', 0)
                item_count = item.get('item_count', 0)
                if alpha_percent is not None:
                    alpha_float = float(alpha_percent.strip('%')) / 100
                    adjusted_count = math.floor(item_count * alpha_float)
                    return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
                return gpu_count * item_count
    # If it's a dict, check directly
    elif isinstance(t1_data, dict) and t1_data.get('item_label') == 'b200_8way':
        gpu_count = t1_data.get('gpu_count', 0)
        item_count = t1_data.get('item_count', 0)
        if alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            adjusted_count = math.floor(item_count * alpha_float)
            return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
        return gpu_count * item_count
    return 0

def extract_h_value(t1_data, t2_data, alpha_percent=None):
    # Helper function to parse a string like 'h200_4way (×14,10)' and return (item_label, item_count)
    def parse_item_string(item_str):
        if not isinstance(item_str, str):
            return None, 0
        try:
            # Extract item_label (e.g., 'h200_4way')
            if ' (×' in item_str:
                item_label = item_str.split(' (×')[0]
                # Extract item_count (e.g., '14')
                count_str = item_str.split(' (×')[1].split(',')[0]
                try:
                    item_count = int(count_str)
                    return item_label, item_count
                except ValueError:
                    return None, 0
            else:
                # If the string doesn't match the expected format, return None
                return None, 0
        except Exception:
            return None, 0

    # Check t1_data
    if isinstance(t1_data, list):
        for item in t1_data:
            if isinstance(item, dict) and isinstance(item.get('item_label'), str) and item.get('item_label').startswith('h200_'):
                gpu_count = item.get('gpu_count', 0)
                item_count = item.get('item_count', 0)
                if alpha_percent is not None:
                    alpha_float = float(alpha_percent.strip('%')) / 100
                    adjusted_count = math.floor(item_count * alpha_float)
                    return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
                return gpu_count * item_count
            elif isinstance(item, str):
                item_label, item_count = parse_item_string(item)
                if item_label and item_label.startswith('h200_'):
                    gpu_count = 8
                    if alpha_percent is not None:
                        alpha_float = float(alpha_percent.strip('%')) / 100
                        adjusted_count = math.floor(item_count * alpha_float)
                        return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
                    return gpu_count * item_count
    elif isinstance(t1_data, dict) and isinstance(t1_data.get('item_label'), str) and t1_data.get('item_label').startswith('h200_'):
        gpu_count = t1_data.get('gpu_count', 0)
        item_count = t1_data.get('item_count', 0)
        if alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            adjusted_count = math.floor(item_count * alpha_float)
            return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
        return gpu_count * item_count
    elif isinstance(t1_data, str):
        item_label, item_count = parse_item_string(t1_data)
        if item_label and item_label.startswith('h200_'):
            gpu_count = 8
            if alpha_percent is not None:
                alpha_float = float(alpha_percent.strip('%')) / 100
                adjusted_count = math.floor(item_count * alpha_float)
                return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
            return gpu_count * item_count

    # Check t2_data
    if isinstance(t2_data, list):
        for item in t2_data:
            if isinstance(item, dict) and isinstance(item.get('item_label'), str) and item.get('item_label').startswith('h200_'):
                gpu_count = item.get('gpu_count', 0)
                item_count = item.get('item_count', 0)
                if alpha_percent is not None:
                    alpha_float = float(alpha_percent.strip('%')) / 100
                    adjusted_count = math.floor(item_count * alpha_float)
                    return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
                return gpu_count * item_count
            elif isinstance(item, str):
                item_label, item_count = parse_item_string(item)
                if item_label and item_label.startswith('h200_'):
                    gpu_count = 8
                    if alpha_percent is not None:
                        alpha_float = float(alpha_percent.strip('%')) / 100
                        adjusted_count = math.floor(item_count * alpha_float)
                        return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
                    return gpu_count * item_count
    elif isinstance(t2_data, dict) and isinstance(t2_data.get('item_label'), str) and t2_data.get('item_label').startswith('h200_'):
        gpu_count = t2_data.get('gpu_count', 0)
        item_count = t2_data.get('item_count', 0)
        if alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            adjusted_count = math.floor(item_count * alpha_float)
            return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
        return gpu_count * item_count
    elif isinstance(t2_data, str):
        item_label, item_count = parse_item_string(t2_data)
        if item_label and item_label.startswith('h200_'):
            gpu_count = 8
            if alpha_percent is not None:
                alpha_float = float(alpha_percent.strip('%')) / 100
                adjusted_count = math.floor(item_count * alpha_float)
                return f"{gpu_count * item_count},{gpu_count * adjusted_count}"
            return gpu_count * item_count

    return 0

def extract_r_value(t1_data, t2_data, alpha_percent=None):
    total = 0
    adjusted_total = 0
    # Helper function to parse a string like 'rtx6000_8way (×45,35)' and return (item_label, item_count)
    def parse_item_string(item_str):
        if not isinstance(item_str, str):
            return None, 0
        try:
            # Extract item_label (e.g., 'rtx6000_8way')
            if ' (×' in item_str:
                item_label = item_str.split(' (×')[0]
                # Extract item_count (e.g., '45')
                count_str = item_str.split(' (×')[1].split(',')[0]
                try:
                    item_count = int(count_str)
                    return item_label, item_count
                except ValueError:
                    return None, 0
            else:
                # If the string doesn't match the expected format, return None
                return None, 0
        except Exception:
            return None, 0

    # Check t1_data
    if isinstance(t1_data, list):
        for item in t1_data:
            if isinstance(item, dict) and isinstance(item.get('item_label'), str) and item.get('item_label').startswith('rtx6000_'):
                gpu_count = item.get('gpu_count', 0)
                item_count = item.get('item_count', 0)
                total += gpu_count * item_count
                if alpha_percent is not None:
                    alpha_float = float(alpha_percent.strip('%')) / 100
                    adjusted_count = math.floor(item_count * alpha_float)
                    adjusted_total += gpu_count * adjusted_count
            elif isinstance(item, str):
                item_label, item_count = parse_item_string(item)
                if item_label and item_label.startswith('rtx6000_'):
                    # Assume gpu_count is 8 for rtx6000_ entries if not provided
                    gpu_count = 8
                    total += gpu_count * item_count
                    if alpha_percent is not None:
                        alpha_float = float(alpha_percent.strip('%')) / 100
                        adjusted_count = math.floor(item_count * alpha_float)
                        adjusted_total += gpu_count * adjusted_count
    elif isinstance(t1_data, dict) and isinstance(t1_data.get('item_label'), str) and t1_data.get('item_label').startswith('rtx6000_'):
        gpu_count = t1_data.get('gpu_count', 0)
        item_count = t1_data.get('item_count', 0)
        total += gpu_count * item_count
        if alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            adjusted_count = math.floor(item_count * alpha_float)
            adjusted_total += gpu_count * adjusted_count
    elif isinstance(t1_data, str):
        item_label, item_count = parse_item_string(t1_data)
        if item_label and item_label.startswith('rtx6000_'):
            gpu_count = 8
            total += gpu_count * item_count
            if alpha_percent is not None:
                alpha_float = float(alpha_percent.strip('%')) / 100
                adjusted_count = math.floor(item_count * alpha_float)
                adjusted_total += gpu_count * adjusted_count

    # Check t2_data
    if isinstance(t2_data, list):
        for item in t2_data:
            if isinstance(item, dict) and isinstance(item.get('item_label'), str) and item.get('item_label').startswith('rtx6000_'):
                gpu_count = item.get('gpu_count', 0)
                item_count = item.get('item_count', 0)
                total += gpu_count * item_count
                if alpha_percent is not None:
                    alpha_float = float(alpha_percent.strip('%')) / 100
                    adjusted_count = math.floor(item_count * alpha_float)
                    adjusted_total += gpu_count * adjusted_count
            elif isinstance(item, str):
                item_label, item_count = parse_item_string(item)
                if item_label and item_label.startswith('rtx6000_'):
                    gpu_count = 8
                    total += gpu_count * item_count
                    if alpha_percent is not None:
                        alpha_float = float(alpha_percent.strip('%')) / 100
                        adjusted_count = math.floor(item_count * alpha_float)
                        adjusted_total += gpu_count * adjusted_count
    elif isinstance(t2_data, dict) and isinstance(t2_data.get('item_label'), str) and t2_data.get('item_label').startswith('rtx6000_'):
        gpu_count = t2_data.get('gpu_count', 0)
        item_count = t2_data.get('item_count', 0)
        total += gpu_count * item_count
        if alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            adjusted_count = math.floor(item_count * alpha_float)
            adjusted_total += gpu_count * adjusted_count
    elif isinstance(t2_data, str):
        item_label, item_count = parse_item_string(t2_data)
        if item_label and item_label.startswith('rtx6000_'):
            gpu_count = 8
            total += gpu_count * item_count
            if alpha_percent is not None:
                alpha_float = float(alpha_percent.strip('%')) / 100
                adjusted_count = math.floor(item_count * alpha_float)
                adjusted_total += gpu_count * adjusted_count

    if total > 0:
        return f"{total},{adjusted_total}" if alpha_percent is not None else total
    return 0

def extract_l_value(t1_data, t2_data, alpha_percent=None):
    total = 0
    adjusted_total = 0
    # Helper function to parse a string like 'l40s_8way (×45,35)' and return (item_label, item_count)
    def parse_item_string(item_str):
        if not isinstance(item_str, str):
            return None, 0
        try:
            # Extract item_label (e.g., 'l40s_8way')
            if ' (×' in item_str:
                item_label = item_str.split(' (×')[0]
                # Extract item_count (e.g., '45')
                count_str = item_str.split(' (×')[1].split(',')[0]
                try:
                    item_count = int(count_str)
                    return item_label, item_count
                except ValueError:
                    return None, 0
            else:
                # If the string doesn't match the expected format, return None
                return None, 0
        except Exception:
            return None, 0

    # Check t1_data
    if isinstance(t1_data, list):
        for item in t1_data:
            if isinstance(item, dict) and isinstance(item.get('item_label'), str) and item.get('item_label').startswith('l40s_'):
                gpu_count = item.get('gpu_count', 0)
                item_count = item.get('item_count', 0)
                total += gpu_count * item_count
                if alpha_percent is not None:
                    alpha_float = float(alpha_percent.strip('%')) / 100
                    adjusted_count = math.floor(item_count * alpha_float)
                    adjusted_total += gpu_count * adjusted_count
            elif isinstance(item, str):
                item_label, item_count = parse_item_string(item)
                if item_label and item_label.startswith('l40s_'):
                    # Assume gpu_count is 8 for l40s_ entries if not provided
                    gpu_count = 8
                    total += gpu_count * item_count
                    if alpha_percent is not None:
                        alpha_float = float(alpha_percent.strip('%')) / 100
                        adjusted_count = math.floor(item_count * alpha_float)
                        adjusted_total += gpu_count * adjusted_count
    elif isinstance(t1_data, dict) and isinstance(t1_data.get('item_label'), str) and t1_data.get('item_label').startswith('l40s_'):
        gpu_count = t1_data.get('gpu_count', 0)
        item_count = t1_data.get('item_count', 0)
        total += gpu_count * item_count
        if alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            adjusted_count = math.floor(item_count * alpha_float)
            adjusted_total += gpu_count * adjusted_count
    elif isinstance(t1_data, str):
        item_label, item_count = parse_item_string(t1_data)
        if item_label and item_label.startswith('l40s_'):
            gpu_count = 8
            total += gpu_count * item_count
            if alpha_percent is not None:
                alpha_float = float(alpha_percent.strip('%')) / 100
                adjusted_count = math.floor(item_count * alpha_float)
                adjusted_total += gpu_count * adjusted_count

    # Check t2_data
    if isinstance(t2_data, list):
        for item in t2_data:
            if isinstance(item, dict) and isinstance(item.get('item_label'), str) and item.get('item_label').startswith('l40s_'):
                gpu_count = item.get('gpu_count', 0)
                item_count = item.get('item_count', 0)
                total += gpu_count * item_count
                if alpha_percent is not None:
                    alpha_float = float(alpha_percent.strip('%')) / 100
                    adjusted_count = math.floor(item_count * alpha_float)
                    adjusted_total += gpu_count * adjusted_count
            elif isinstance(item, str):
                item_label, item_count = parse_item_string(item)
                if item_label and item_label.startswith('l40s_'):
                    gpu_count = 8
                    total += gpu_count * item_count
                    if alpha_percent is not None:
                        alpha_float = float(alpha_percent.strip('%')) / 100
                        adjusted_count = math.floor(item_count * alpha_float)
                        adjusted_total += gpu_count * adjusted_count
    elif isinstance(t2_data, dict) and isinstance(t2_data.get('item_label'), str) and t2_data.get('item_label').startswith('l40s_'):
        gpu_count = t2_data.get('gpu_count', 0)
        item_count = t2_data.get('item_count', 0)
        total += gpu_count * item_count
        if alpha_percent is not None:
            alpha_float = float(alpha_percent.strip('%')) / 100
            adjusted_count = math.floor(item_count * alpha_float)
            adjusted_total += gpu_count * adjusted_count
    elif isinstance(t2_data, str):
        item_label, item_count = parse_item_string(t2_data)
        if item_label and item_label.startswith('l40s_'):
            gpu_count = 8
            total += gpu_count * item_count
            if alpha_percent is not None:
                alpha_float = float(alpha_percent.strip('%')) / 100
                adjusted_count = math.floor(item_count * alpha_float)
                adjusted_total += gpu_count * adjusted_count

    if total > 0:
        return f"{total},{adjusted_total}" if alpha_percent is not None else total
    return 0

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process YAML files and calculate alpha values.')
    parser.add_argument('--tgp', type=float, default=1.7, help='Target ST1 price (default: 1.7)')
    args = parser.parse_args()
    
    # Read all YAML files
    yaml_data = read_yaml_files()
    df = yaml_dicts_to_dataframe(yaml_data)
    
    # Set display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', None)
    
    # Calculate alpha values first
    df['alpha'] = (1 / (df['total_price'] / args.tgp)) * 100
    df['alpha'] = df['alpha'].apply(lambda x: f"{x:.1f}%")
    
    # Add a new column 'B' that holds the product of gpu_count and item_count for b200_8way entries
    df['B'] = df.apply(lambda row: extract_b2_value(row['t1'], row['alpha']), axis=1)
    # Remove the old 'b2' column if it exists
    if 'b2' in df.columns:
        df.drop(columns=['b2'], inplace=True)
    
    # Add a new column 'H' that holds the product of gpu_count and item_count for h200_8way entries
    df['H'] = df.apply(lambda row: extract_h_value(row['t1'], row['t2'], row['alpha']), axis=1)
    
    # Extract and format item fields, passing alpha values for t1, t2, and hs
    for col in ['cs', 'cn']:
        df[col] = df[col].apply(extract_item_fields)
    
    # Special handling for t1, t2, hs, and hn to include adjusted counts
    df['t1'] = df.apply(lambda row: extract_item_fields(row['t1'], row['alpha']), axis=1)
    df['t2'] = df.apply(lambda row: extract_item_fields(row['t2'], row['alpha']), axis=1)
    df['hs'] = df.apply(lambda row: extract_item_fields(row['hs'], row['alpha'], is_hs=True), axis=1)
    df['hn'] = df.apply(lambda row: extract_item_fields(row['hn'], row['alpha']), axis=1)
    df['sn'] = df.apply(lambda row: extract_item_fields(row['sn'], row['alpha']), axis=1)
    
    # Add a new column 'R' that holds the total product of gpu_count and item_count for rtx6000_ entries
    df['R'] = df.apply(lambda row: extract_r_value(row['t1'], row['t2'], row['alpha']), axis=1)
    
    # Add a new column 'L' that holds the total product of gpu_count and item_count for l40s_ entries
    df['L'] = df.apply(lambda row: extract_l_value(row['t1'], row['t2'], row['alpha']), axis=1)
    
    # Add a new column 'T' that holds the sum of B, H, R, and L values
    def calculate_t(row):
        def get_values(val):
            if isinstance(val, str) and ',' in val:
                return [int(x) for x in val.split(',')]
            return [int(val), 0]
        
        b_values = get_values(row['B'])
        h_values = get_values(row['H'])
        r_values = get_values(row['R'])
        l_values = get_values(row['L'])
        
        return f"{b_values[0] + h_values[0] + r_values[0] + l_values[0]},{b_values[1] + h_values[1] + r_values[1] + l_values[1]}"
    
    df['T'] = df.apply(calculate_t, axis=1)
    
    # Add TGP value information
    df['TGP_Info'] = f"TGP value is {args.tgp}"
    
    print("\nPandas DataFrame (showing item_label and item_count values):")
    print(df)
    
    # Write DataFrame to CSV
    tgp_str = str(args.tgp).replace('.', 'p')
    df.to_csv(f'summary_ST1-{tgp_str}.csv', index=False)
    print(f"\nData has been written to summary_ST1-{tgp_str}.csv (using TGP value: {args.tgp})") 
