import os
import sys
import argparse
import pandas as pd
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description="Modify YAML based on CSV filters.")
    parser.add_argument("--input", required=True, help="Path to input YAML")
    parser.add_argument("--output", required=True, help="Path to save updated YAML")
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--tenant", required=True, help="Tenant ID filter")
    parser.add_argument("--prefix", required=True, help="Prefix filter")
    parser.add_argument("--key", required=True, help="Nested YAML key to edit (e.g., settings.timeout)")
    return parser.parse_args()

def set_nested_value(data, key_path, value):
    """Dynamically sets a value in a nested dictionary using dot notation."""
    keys = key_path.split('.')
    for key in keys[:-1]:
        data = data.setdefault(key, {})
    data[keys[-1]] = value
def main():
    args = parse_args()
    
    # 1. Load CSV and apply filters
    if not os.path.exists(args.csv):
        print(f"Error: CSV file not found at {args.csv}", file=sys.stderr)
        sys.exit(1)
        
    df = pd.read_csv(args.csv)
    
    # Ensure strings for filtering comparison
    df['tenant_id'] = df['tenant_id'].astype(str)
    df['prefix'] = df['prefix'].astype(str)
    
    filtered_df = df[(df['tenant_id'] == args.tenant) & (df['prefix'] == args.prefix)]
    
    if filtered_df.empty:
        print(f"Error: No matching CSV rows found for Tenant: {args.tenant}, Prefix: {args.prefix}", file=sys.stderr)
        sys.exit(1)
        
    # Assuming the target value is in a column named 'new_value'
    if 'new_value' not in filtered_df.columns:
        print("Error: CSV must contain a 'new_value' column.", file=sys.stderr)
        sys.exit(1)
        
    target_value = filtered_df.iloc[0]['new_value']
  
    # 2. Load YAML
    if not os.path.exists(args.input):
        print(f"Error: Input YAML file not found at {args.input}", file=sys.stderr)
        sys.exit(1)
        
    with open(args.input, 'r') as f:
        yaml_data = yaml.safe_load(f) or {}

    # 3. Update the value
    try:
        # Cast value to int/float if appropriate, otherwise keep as string
        if str(target_value).isdigit():
            target_value = int(target_value)
        
        set_nested_value(yaml_data, args.key, target_value)
        print(f"Successfully updated '{args.key}' to '{target_value}'")
    except Exception as e:
        print(f"Error parsing/modifying YAML key structure: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Save to output directory
    with open(args.output, 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=False)
        
if __name__ == "__main__":
    main()
