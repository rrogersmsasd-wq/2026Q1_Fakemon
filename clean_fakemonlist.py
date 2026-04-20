#!/usr/bin/env python3
"""
clean_fakemonlist.py
Rebuilds fakemon/fakemonlist.json from every .json file in fakemon/json/.
Run from the repo root:
    python clean_fakemonlist.py
"""

import json
from pathlib import Path

json_dir    = Path("fakemon/json")
output_file = Path("fakemon/fakemonlist.json")

files = sorted(f.stem for f in json_dir.glob("*.json"))

output_file.write_text(json.dumps({"fakemon": files}, indent=2), encoding="utf-8")

print(f"Updated fakemonlist.json with {len(files)} fakemon:")
for name in files:
    print(f"  {name}")