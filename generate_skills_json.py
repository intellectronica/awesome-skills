#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0.1"]
# ///

"""
Convert skills.yaml to skills.json without hardcoding any field knowledge.
Performs a faithful YAML→JSON conversion using safe_load and json.dump.
Also injects the JSON data into skills.html.
"""

from pathlib import Path
import json
import sys
import re
import yaml

ROOT = Path(__file__).parent.resolve()
YAML_PATH = ROOT / "skills.yaml"
JSON_PATH = ROOT / "skills.json"
HTML_PATH = ROOT / "skills.html"

def main():
    try:
        with open(YAML_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {YAML_PATH} not found", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {YAML_PATH}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # If YAML is empty, treat as empty object for consistency
    if data is None:
        data = {}
    
    # Save to JSON file
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
                default=str  # Fallback for any non-JSON-native types
            )
            f.write("\n")  # Trailing newline for consistency
        print(f"✓ {JSON_PATH} written successfully")
    except Exception as e:
        print(f"Error writing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Inject JSON into HTML file
    try:
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Create the compact JSON string (single line, no extra whitespace)
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'), default=str)
        
        # Find and replace the content between the script tags
        updated_html = html_content
        # Split on the opening tag to find it
        if '<script id="skills-data" type="application/json">' in html_content:
            # Find the start and end positions
            start_tag = '<script id="skills-data" type="application/json">'
            end_tag = '</script>'
            
            start_idx = html_content.find(start_tag)
            if start_idx != -1:
                start_content = start_idx + len(start_tag)
                end_idx = html_content.find(end_tag, start_content)
                
                if end_idx != -1:
                    # Replace everything between the tags
                    updated_html = (
                        html_content[:start_content] +
                        '\n' + json_str + '\n' +
                        html_content[end_idx:]
                    )
        
        with open(HTML_PATH, "w", encoding="utf-8") as f:
            f.write(updated_html)
        
        print(f"✓ {HTML_PATH} updated with skills data")
    except FileNotFoundError:
        print(f"Warning: {HTML_PATH} not found, skipping HTML injection", file=sys.stderr)
    except Exception as e:
        print(f"Error updating HTML: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
