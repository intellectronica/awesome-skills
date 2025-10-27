#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0.1"]
# ///

"""
Convert skills.yaml to skills.json without hardcoding any field knowledge.
Performs a faithful YAML→JSON conversion using safe_load and json.dump.
"""

from pathlib import Path
import json
import sys
import yaml

ROOT = Path(__file__).parent.resolve()
YAML_PATH = ROOT / "skills.yaml"
JSON_PATH = ROOT / "skills.json"

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

if __name__ == "__main__":
    main()
